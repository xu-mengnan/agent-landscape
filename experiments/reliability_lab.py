"""Original, deterministic reliability lab; NOT an implementation of any Agent SDK.

All identities/data are synthetic. No network, model calls, secrets or external effects.
The two SQLite databases model distinct worker and downstream persistence boundaries.
Python 3.10+. This educational implementation is not a distributed production service.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class Conflict(ValueError):
    """A stable operation identifier was reused with incompatible contents."""


class InjectedCrash(RuntimeError):
    """Deterministic fault injection, not a normal business failure."""


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


@contextmanager
def connection(path: str | Path) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(str(path), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        with conn:
            yield conn
    finally:
        conn.close()


class RemoteService:
    """Downstream simulation. Dedup key and payload hash commit atomically.

    Real downstream systems must independently guarantee the same invariant.
    A local outbox alone cannot make a non-idempotent remote API exactly-once.
    """
    def __init__(self, path: str | Path):
        self.path = Path(path)
        with connection(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS effects(
                tenant TEXT NOT NULL, op_key TEXT NOT NULL,
                payload_hash TEXT NOT NULL, payload TEXT NOT NULL,
                PRIMARY KEY(tenant, op_key))""")

    def execute(self, tenant: str, op_key: str, payload: dict[str, Any]) -> bool:
        hashed = digest(payload)
        with connection(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT payload_hash FROM effects WHERE tenant=? AND op_key=?",
                             (tenant, op_key)).fetchone()
            if row:
                if row["payload_hash"] != hashed:
                    raise Conflict("operation key reused with a different payload")
                return False
            db.execute("INSERT INTO effects VALUES (?,?,?,?)",
                       (tenant, op_key, hashed, canonical(payload)))
            return True

    def count(self, tenant: str | None = None) -> int:
        with connection(self.path) as db:
            if tenant is None:
                return db.execute("SELECT COUNT(*) FROM effects").fetchone()[0]
            return db.execute("SELECT COUNT(*) FROM effects WHERE tenant=?", (tenant,)).fetchone()[0]


class Outbox:
    """Persistent intent, independent from downstream; illustrative single-task worker.

    No distributed leases, automatic backoff or multi-region guarantees are implemented.
    Cancellation is checked before dispatch; it cannot revoke already committed effects.
    """
    def __init__(self, path: str | Path):
        self.path = Path(path)
        with connection(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS jobs(
                tenant TEXT NOT NULL, task_id TEXT NOT NULL,
                payload TEXT NOT NULL, payload_hash TEXT NOT NULL,
                approved INTEGER NOT NULL, state TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(tenant, task_id))""")

    def enqueue(self, tenant: str, task_id: str, payload: dict[str, Any], *, approved: bool) -> bool:
        with connection(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT payload_hash FROM jobs WHERE tenant=? AND task_id=?",
                             (tenant, task_id)).fetchone()
            if row:
                if row[0] != digest(payload):
                    raise Conflict("task identifier reused with a different payload")
                return False
            db.execute("INSERT INTO jobs VALUES (?,?,?,?,?,'pending',0)",
                       (tenant, task_id, canonical(payload), digest(payload), int(approved)))
            return True

    def read(self, tenant: str, task_id: str) -> dict[str, Any]:
        with connection(self.path) as db:
            row = db.execute("SELECT * FROM jobs WHERE tenant=? AND task_id=?",
                             (tenant, task_id)).fetchone()
            if row is None:
                raise KeyError((tenant, task_id))
            return dict(row)

    def cancel(self, tenant: str, task_id: str) -> bool:
        with connection(self.path) as db:
            return db.execute("UPDATE jobs SET state='cancelled' WHERE tenant=? AND task_id=? AND state='pending'",
                              (tenant, task_id)).rowcount == 1

    def deliver(self, remote: RemoteService, tenant: str, task_id: str, *,
                crash_at: str | None = None, hard_exit: bool = False,
                max_attempts: int = 3) -> str:
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        with connection(self.path) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM jobs WHERE tenant=? AND task_id=?",
                             (tenant, task_id)).fetchone()
            if row is None:
                raise KeyError((tenant, task_id))
            if row['state'] != 'pending':
                return row['state']
            if not row['approved']:
                return 'approval_required'
            if row['attempts'] >= max_attempts:
                db.execute("UPDATE jobs SET state='reconcile_required' WHERE tenant=? AND task_id=?",
                           (tenant, task_id))
                return 'reconcile_required'
            db.execute("UPDATE jobs SET attempts=attempts+1 WHERE tenant=? AND task_id=?", (tenant, task_id))
            payload = json.loads(row['payload'])
        if crash_at == 'before_remote':
            raise InjectedCrash('before_remote')
        # This is deliberately outside the local transaction: a realistic failure window.
        remote.execute(tenant, task_id, payload)
        if crash_at == 'after_remote':
            if hard_exit:
                os._exit(23)  # only used by a disposable child process in tests
            raise InjectedCrash('after_remote')
        with connection(self.path) as db:
            # Concurrent cancellation after dispatch needs reconciliation, not false rollback.
            changed = db.execute("UPDATE jobs SET state='done' WHERE tenant=? AND task_id=? AND state='pending'",
                                 (tenant, task_id)).rowcount
            if not changed:
                return 'reconcile_required'
        return 'done'


class VersionedState:
    ALLOWED = {'draft': {'review', 'cancelled'}, 'review': {'approved', 'cancelled'},
               'approved': {'sent', 'cancelled'}, 'sent': set(), 'cancelled': set()}

    def __init__(self, path: str | Path):
        self.path = Path(path)
        with connection(self.path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS state(
                tenant TEXT, item TEXT, stage TEXT, version INTEGER,
                PRIMARY KEY(tenant,item))""")

    def create(self, tenant: str, item: str) -> None:
        with connection(self.path) as db:
            db.execute("INSERT INTO state VALUES (?,?,'draft',0)", (tenant, item))

    def read(self, tenant: str, item: str) -> tuple[str, int]:
        with connection(self.path) as db:
            row = db.execute('SELECT stage,version FROM state WHERE tenant=? AND item=?',
                             (tenant, item)).fetchone()
            if row is None:
                raise KeyError((tenant, item))
            return row[0], row[1]

    def advance(self, tenant: str, item: str, expected_version: int, new_stage: str) -> bool:
        with connection(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT stage,version FROM state WHERE tenant=? AND item=?',
                             (tenant, item)).fetchone()
            if row is None:
                raise KeyError((tenant, item))
            if row['version'] != expected_version:
                return False
            if new_stage not in self.ALLOWED[row['stage']]:
                raise ValueError('illegal transition')
            return db.execute('UPDATE state SET stage=?,version=version+1 WHERE tenant=? AND item=? AND version=?',
                              (new_stage, tenant, item, expected_version)).rowcount == 1


class Memory:
    """An illustrative key-level revision/source policy, not semantic memory reasoning.

    Revisions are assigned by trusted application code, not a model. Tombstones here
    are permanent until explicit external policy changes; no vector index is modeled.
    """
    RANK = {'user': 1, 'authoritative_tool': 2}

    def __init__(self):
        self.rows: dict[tuple[str, str], dict[str, Any]] = {}

    def put(self, tenant: str, key: str, value: Any, *, source: str, revision: int,
            expires: float | None = None) -> bool:
        if source not in self.RANK or revision < 1:
            raise ValueError('untrusted source or invalid revision')
        old = self.rows.get((tenant, key))
        if old and (old['deleted'] or revision <= old['revision']):
            return False
        if old and value != old['value'] and self.RANK[source] < self.RANK[old['source']]:
            return False
        self.rows[(tenant, key)] = dict(value=value, source=source, revision=revision,
                                       expires=expires, deleted=False)
        return True

    def get(self, tenant: str, key: str, *, now: float) -> Any:
        row = self.rows.get((tenant, key))
        if not row or row['deleted'] or (row['expires'] is not None and now >= row['expires']):
            return None
        return row['value']

    def delete(self, tenant: str, key: str, *, revision: int) -> bool:
        old = self.rows.get((tenant, key))
        if revision < 1 or (old and revision <= old['revision']):
            return False
        self.rows[(tenant, key)] = dict(value=None, source='authoritative_tool',
                                       revision=revision, expires=None, deleted=True)
        return True


def naive_lost_ack() -> int:
    """Negative control: two invocations cause two non-idempotent effects."""
    effects = []
    for _ in range(2):
        effects.append('notification')
    return len(effects)


def naive_stale_overwrite() -> str:
    state = 'approved'
    state = 'review'  # late callback overwrites a newer state without version validation
    return state


def policy_order(*, check_before: bool) -> dict[str, Any]:
    """A counterexample schedule, NOT an executed SDK/LLM concurrency benchmark."""
    effects: list[str] = []
    allowed = False
    if check_before and not allowed:
        return dict(effects=0, rejected=True)
    effects.append('write')
    return dict(effects=len(effects), rejected=not allowed)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker-db', required=True)
    parser.add_argument('--remote-db', required=True)
    parser.add_argument('--tenant', default='tenant-a')
    parser.add_argument('--task', default='task-1')
    parser.add_argument('--crash-after-remote', action='store_true')
    args = parser.parse_args()
    outbox, remote = Outbox(args.worker_db), RemoteService(args.remote_db)
    result = outbox.deliver(remote, args.tenant, args.task,
                            crash_at='after_remote' if args.crash_after_remote else None,
                            hard_exit=args.crash_after_remote)
    print(result)


if __name__ == '__main__':
    main()
