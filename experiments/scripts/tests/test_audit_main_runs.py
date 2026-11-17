"""Synthetic regression tests for SEM-44 tooling, not experimental run results."""
import copy
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout

REPO=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('auditor',REPO/'experiments/scripts/audit_main_runs.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.run=self.root/'runs'/'synthetic';self.run.mkdir(parents=True)
        self.m=json.loads((REPO/'experiments/fixtures/sem24/manifest.json').read_text())
        self.m.update(data_kind='OBSERVED',run_phase='main',execution_status='COMPLETED',outcome='SUCCESS',validity='VALID')
        self.m['build']['candidate_gate_passed']=True
        self.events=[json.loads(x) for x in (REPO/'experiments/fixture_exports/run-sem24-fixture/events.jsonl').read_text().splitlines()]
        self.write()
    def write(self):
        (self.run/'manifest.json').write_text(json.dumps(self.m))
        (self.run/'events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in self.events))
    def csv(self, change=None, duplicate=False):
        fields=sorted(a.CSV_REQUIRED|{'work_started_event_count_all','snapshot_applied_event_count_all','eligible','update_to_applied_ms'})
        row={k:str(self.m.get(k,'')) for k in fields}
        row.update({k:str(self.m['build'][k]) for k in ('app_commit','server_commit','apk_sha256')})
        row.update(manifest_sha256=hashlib.sha256((self.run/'manifest.json').read_bytes()).hexdigest(),events_sha256=hashlib.sha256((self.run/'events.jsonl').read_bytes()).hexdigest(),work_started_event_count_all='1',snapshot_applied_event_count_all='1',eligible='false',update_to_applied_ms='')
        if change:row.update(change)
        p=self.root/'results.csv'
        with p.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerow(row)
            if duplicate:w.writerow(row)
        return p
    def test_valid_structure(self):
        m,events,issues=a.audit_run(self.run);self.assertEqual(issues,[])
        _,issues=a.audit_csv(self.csv(),[(m,events,issues)]);self.assertEqual(issues,[])
    def test_pilot_excluded_not_main(self):
        self.m['run_phase']='pilot';self.write()
        with redirect_stdout(io.StringIO()):rc=a.main(['--runs',str(self.root/'runs'),'--csv',str(self.root/'missing.csv'),'--output',str(self.root/'report.md')])
        self.assertEqual(rc,2);text=(self.root/'report.md').read_text();self.assertIn('Runs inspected: 0',text);self.assertIn('Non-main directories excluded: 1',text)
    def test_blank_metadata_and_changed_hash_rejected(self):
        run=a.audit_run(self.run);_,issues=a.audit_csv(self.csv({'app_commit':'','events_sha256':'bad'}),[run]);self.assertTrue(any('APP_COMMIT' in x for x in issues));self.assertTrue(any('HASH_MISMATCH' in x for x in issues))
    def test_duplicate_csv_rejected(self):
        run=a.audit_run(self.run);_,issues=a.audit_csv(self.csv(duplicate=True),[run]);self.assertTrue(any('DUPLICATE_CSV' in x for x in issues))
    def test_csv_counts_all_recomputed(self):
        run=a.audit_run(self.run);_,issues=a.audit_csv(self.csv({'work_started_event_count_all':'9'}),[run]);self.assertTrue(any('COUNT_MISMATCH' in x for x in issues))
    def test_timeout_positive_and_scientific_zero_latency_rejected(self):
        self.m.update(outcome='TIMEOUT',reason_codes=['TIMEOUT']);self.write();run=a.audit_run(self.run)
        for value in ('0e0','12'):
            _,issues=a.audit_csv(self.csv({'update_to_applied_ms':value}),[run]);self.assertTrue(any('TIMEOUT_HAS' in x for x in issues))
    def test_main_not_run_not_certified(self):
        self.m.update(execution_status='NOT_RUN',outcome='NOT_RUN',validity='NOT_ASSESSED');self.events=[];self.write()
        _,_,issues=a.audit_run(self.run);self.assertIn('RUN_NOT_EXECUTED',issues)
    def test_higher_snapshot_is_not_target_mismatch(self):
        self.m['observation']['target_version']=0;self.write();_,_,issues=a.audit_run(self.run);self.assertNotIn('APPLIED_VERSION_DIFFERS_FROM_TARGET',issues)
    def test_missing_boot_prevents_monotonic_join(self):
        for e in self.events:
            if e['origin']=='ANDROID':e['boot_session_id']=None
        self.write();_,_,issues=a.audit_run(self.run);self.assertIn('SYNC_MONOTONIC_BOOT_UNVERIFIED',issues)
    def test_input_overwrite_blocked(self):
        original=(self.run/'events.jsonl').read_bytes()
        with redirect_stdout(io.StringIO()):rc=a.main(['--runs',str(self.root/'runs'),'--csv',str(self.root/'results.csv'),'--output',str(self.run/'events.jsonl')])
        self.assertEqual(rc,2);self.assertEqual(original,(self.run/'events.jsonl').read_bytes())
    def test_conflicting_event_id_not_counted_twice(self):
        duplicate=copy.deepcopy(self.events[-1]);duplicate['timestamp_utc']='2026-11-03T00:01:30Z';self.events.append(duplicate);self.write()
        _,events,issues=a.audit_run(self.run);self.assertTrue(any('EVENT_ID_CONFLICT' in x for x in issues));self.assertEqual(len(events),len(self.events)-1)
    def test_invalid_run_cannot_be_eligible(self):
        self.m.update(validity='INVALID',reason_codes=['INVALID_RESPONSE']);self.write();run=a.audit_run(self.run)
        _,issues=a.audit_csv(self.csv({'eligible':'true'}),[run]);self.assertTrue(any('INELIGIBLE_INCLUDED' in x for x in issues))

if __name__=='__main__':unittest.main()
