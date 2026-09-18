"""Actual deterministic tests; the negative controls pass by exposing expected defects."""
from __future__ import annotations
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from experiments.reliability_lab import (
    Conflict, InjectedCrash, Memory, Outbox, RemoteService, VersionedState,
    naive_lost_ack, naive_stale_overwrite, policy_order,
)

ROOT = Path(__file__).resolve().parents[1]


class ReliabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.remote = RemoteService(self.base / 'remote.sqlite')
        self.outbox = Outbox(self.base / 'worker.sqlite')
        self.payload = {'message': 'synthetic reminder', 'recipient': 'user-a'}
        self.outbox.enqueue('a', 'job', self.payload, approved=True)

    def test_normal_delivery(self):
        self.assertEqual(self.outbox.deliver(self.remote, 'a', 'job'), 'done')
        self.assertEqual(self.remote.count(), 1)

    def test_negative_control_ack_loss_duplicates(self):
        self.assertEqual(naive_lost_ack(), 2)

    def test_lost_ack_then_retry_one_effect(self):
        with self.assertRaises(InjectedCrash):
            self.outbox.deliver(self.remote, 'a', 'job', crash_at='after_remote')
        self.assertEqual(self.remote.count(), 1)
        self.assertEqual(self.outbox.read('a', 'job')['state'], 'pending')
        self.assertEqual(self.outbox.deliver(self.remote, 'a', 'job'), 'done')
        self.assertEqual(self.remote.count(), 1)
        self.assertEqual(self.outbox.read('a', 'job')['attempts'], 2)

    def test_crash_before_remote_then_retry(self):
        with self.assertRaises(InjectedCrash):
            self.outbox.deliver(self.remote, 'a', 'job', crash_at='before_remote')
        self.assertEqual(self.remote.count(), 0)
        self.outbox.deliver(self.remote, 'a', 'job')
        self.assertEqual(self.remote.count(), 1)

    def test_real_child_process_exit_and_restart(self):
        cmd = [sys.executable, '-m', 'experiments.reliability_lab', '--worker-db',
               str(self.outbox.path), '--remote-db', str(self.remote.path),
               '--tenant', 'a', '--task', 'job']
        crashed = subprocess.run(cmd + ['--crash-after-remote'], cwd=ROOT,
                                 capture_output=True, text=True, timeout=10)
        self.assertEqual(crashed.returncode, 23, crashed.stderr)
        self.assertEqual(self.remote.count(), 1)
        self.assertEqual(self.outbox.read('a', 'job')['state'], 'pending')
        resumed = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertEqual(resumed.stdout.strip(), 'done')
        self.assertEqual(self.remote.count(), 1)

    def test_finished_job_not_resent(self):
        self.outbox.deliver(self.remote, 'a', 'job')
        self.outbox.deliver(self.remote, 'a', 'job')
        self.assertEqual(self.remote.count(), 1)
        self.assertEqual(self.outbox.read('a', 'job')['attempts'], 1)

    def test_duplicate_enqueue(self):
        self.assertFalse(self.outbox.enqueue('a', 'job', self.payload, approved=True))

    def test_payload_collision_is_error(self):
        with self.assertRaises(Conflict):
            self.outbox.enqueue('a', 'job', {'message': 'changed'}, approved=True)

    def test_remote_payload_collision_is_error(self):
        self.remote.execute('a', 'key', self.payload)
        with self.assertRaises(Conflict):
            self.remote.execute('a', 'key', {'message': 'changed'})
        self.assertEqual(self.remote.count(), 1)

    def test_remote_dedup_under_concurrent_calls(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            values = list(pool.map(lambda _: self.remote.execute('a', 'key', self.payload), range(16)))
        self.assertEqual(sum(values), 1)
        self.assertEqual(self.remote.count(), 1)

    def test_tenant_dedup_isolation(self):
        self.remote.execute('a', 'same-key', self.payload)
        self.remote.execute('b', 'same-key', self.payload)
        self.assertEqual(self.remote.count(), 2)

    def test_approval_blocks_before_effect(self):
        self.outbox.enqueue('a', 'not-approved', self.payload, approved=False)
        self.assertEqual(self.outbox.deliver(self.remote, 'a', 'not-approved'), 'approval_required')
        self.assertEqual(self.remote.count(), 0)

    def test_cancel_before_dispatch(self):
        self.assertTrue(self.outbox.cancel('a', 'job'))
        self.assertEqual(self.outbox.deliver(self.remote, 'a', 'job'), 'cancelled')
        self.assertEqual(self.remote.count(), 0)

    def test_cancel_cannot_undo_finished_effect(self):
        self.outbox.deliver(self.remote, 'a', 'job')
        self.assertFalse(self.outbox.cancel('a', 'job'))
        self.assertEqual(self.remote.count(), 1)

    def test_exhaustion_requires_reconciliation(self):
        with self.assertRaises(InjectedCrash):
            self.outbox.deliver(self.remote, 'a', 'job', crash_at='after_remote', max_attempts=1)
        self.assertEqual(self.outbox.deliver(self.remote, 'a', 'job', max_attempts=1), 'reconcile_required')
        self.assertEqual(self.remote.count(), 1)

    def test_missing_job(self):
        with self.assertRaises(KeyError):
            self.outbox.read('b', 'job')

    def test_negative_control_late_validation(self):
        self.assertEqual(policy_order(check_before=False), {'effects': 1, 'rejected': True})

    def test_pre_execution_authorization(self):
        self.assertEqual(policy_order(check_before=True), {'effects': 0, 'rejected': True})

    def test_negative_control_stale_overwrite(self):
        self.assertEqual(naive_stale_overwrite(), 'review')

    def test_versioned_valid_flow(self):
        state = VersionedState(self.base / 'state.sqlite')
        state.create('a', 'order')
        for i, stage in enumerate(['review', 'approved', 'sent']):
            self.assertTrue(state.advance('a', 'order', i, stage))
        self.assertEqual(state.read('a', 'order'), ('sent', 3))

    def test_versioned_rejects_stale_callback(self):
        state = VersionedState(self.base / 'state.sqlite')
        state.create('a', 'order')
        state.advance('a', 'order', 0, 'review')
        state.advance('a', 'order', 1, 'approved')
        self.assertFalse(state.advance('a', 'order', 0, 'cancelled'))
        self.assertEqual(state.read('a', 'order'), ('approved', 2))

    def test_illegal_transition(self):
        state = VersionedState(self.base / 'state.sqlite')
        state.create('a', 'order')
        with self.assertRaises(ValueError):
            state.advance('a', 'order', 0, 'sent')

    def test_terminal_state(self):
        state = VersionedState(self.base / 'state.sqlite')
        state.create('a', 'order')
        state.advance('a', 'order', 0, 'cancelled')
        with self.assertRaises(ValueError):
            state.advance('a', 'order', 1, 'review')

    def test_two_writers_one_version_winner(self):
        state = VersionedState(self.base / 'state.sqlite')
        state.create('a', 'order')
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda stage: state.advance('a','order',0,stage), ['review','cancelled']))
        self.assertEqual(sum(results), 1)
        self.assertEqual(state.read('a','order')[1], 1)

    def test_memory_latest_revision(self):
        m = Memory()
        self.assertTrue(m.put('a','preference','email',source='user',revision=1))
        self.assertTrue(m.put('a','preference','none',source='user',revision=2))
        self.assertFalse(m.put('a','preference','sms',source='user',revision=1))
        self.assertEqual(m.get('a','preference',now=0), 'none')

    def test_memory_authoritative_conflict(self):
        m = Memory()
        m.put('a','paid',False,source='authoritative_tool',revision=1)
        self.assertFalse(m.put('a','paid',True,source='user',revision=2))
        self.assertFalse(m.get('a','paid',now=0))

    def test_memory_expiry_boundary(self):
        m = Memory()
        m.put('a','temp','value',source='user',revision=1,expires=10)
        self.assertEqual(m.get('a','temp',now=9), 'value')
        self.assertIsNone(m.get('a','temp',now=10))

    def test_memory_tenant_isolation(self):
        m = Memory()
        m.put('a','profile','only-a',source='user',revision=1)
        self.assertIsNone(m.get('b','profile',now=0))

    def test_memory_tombstone_blocks_resurrection(self):
        m = Memory()
        m.put('a','profile','old',source='user',revision=1)
        self.assertTrue(m.delete('a','profile',revision=2))
        self.assertFalse(m.put('a','profile','old',source='user',revision=1))
        self.assertFalse(m.put('a','profile','new',source='user',revision=3))
        self.assertIsNone(m.get('a','profile',now=0))

    def test_invalid_memory_source(self):
        with self.assertRaises(ValueError):
            Memory().put('a','key','value',source='model_claimed_admin',revision=1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
