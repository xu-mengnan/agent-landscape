"""Run offline tests and write transparent, machine-readable execution evidence."""
from __future__ import annotations
import importlib.util
import json
import platform
import sqlite3
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append({'test': test.id(), 'status': 'passed'})
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.records.append({'test': test.id(), 'status': 'failed'})
    def addError(self, test, err):
        super().addError(test, err)
        self.records.append({'test': test.id(), 'status': 'error'})
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.records.append({'test': test.id(), 'status': 'skipped', 'reason': reason})

def available(module):
    try:
        return importlib.util.find_spec(module) is not None
    except (ModuleNotFoundError, ValueError):
        return False

if __name__ == '__main__':
    (ROOT/'results').mkdir(exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    with (ROOT/'results'/'offline-tests.log').open('w',encoding='utf-8') as log:
        result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=RecordedResult).run(suite)
    report = dict(
        evidence='E: original offline mechanisms only', started_at_utc=started,
        finished_at_utc=datetime.now(timezone.utc).isoformat(),
        python=sys.version, platform=platform.platform(), sqlite=sqlite3.sqlite_version,
        network_calls=0, model_calls=0, provider_frameworks_executed=[],
        framework_modules_available={m: available(m) for m in ['langgraph','agents','google.adk']},
        tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
        skipped=len(result.skipped), passed=sum(r['status']=='passed' for r in result.records),
        planned_real_model_trials=420, real_model_trials_completed=0,
        important_note='Negative-control tests pass by reproducing a known unsafe outcome. The suite pass rate is not an Agent success rate.',
        tests=result.records,
    )
    (ROOT/'results'/'offline-results.json').write_text(json.dumps(report, ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['tests_run','passed','failures','errors','model_calls']},ensure_ascii=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
