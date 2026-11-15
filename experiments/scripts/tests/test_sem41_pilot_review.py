"""Synthetic review checks, not measurements or pilot artifacts."""

import json
from pathlib import Path
import sys
import sqlite3
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import export_sem41_pilots as reviewer


class PilotReviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name) / "run"
        self.folder.mkdir()
        self.record = {"run_id": "synthetic-review", "case_id": "E01", "stage": "FINISHED", "execution_status": "COMPLETED", "run_phase": "pilot", "candidate_gate_passed": False, "outcome": "TIMEOUT", "cleanup_passed": True, "start_elapsed_realtime_ms": 1000, "end_elapsed_realtime_ms": 5401000, "target_version": 2, "work_id": "synthetic-work", "new_periodic_cycles": 0}
        self.events = [{"event_id": "synthetic-registration", "event_type": "periodic_registered", "request_id": None, "source": "PERIODIC", "work_id": "synthetic-work", "elapsed_realtime_ms": 0}]
        self.raw = [{"eventId": "synthetic-registration"}]
        self.report = {"exported_event_count": 1, "omitted_event_count": 0, "omitted_events": []}
        reviewer.save(self.folder / "cleanup-checkpoint.json", {"package_stopped": False, "app_resumed": False, "network_connected": True, "idle": "ACTIVE", "elapsed_realtime_ms": 5401002})
        for label in ("background", "window-end"):
            reviewer.save(self.folder / (label + "-checkpoint.json"), {"package_stopped": False, "app_resumed": False, "network_connected": True, "idle": "ACTIVE", "elapsed_realtime_ms": 0 if label == "background" else 5401001})
        reviewer.save(self.folder / "export-v2-state.json", {"periodic_work": []})
        (self.folder / "setup-db").mkdir()
        connection = sqlite3.connect(str(self.folder / "setup-db/seminar_bulletin.db"))
        connection.executescript("CREATE TABLE sync_metadata(key TEXT,value TEXT); INSERT INTO sync_metadata VALUES('cachedVersion','1'); CREATE TABLE bulletin_items(id TEXT,title TEXT,body TEXT,version INTEGER); INSERT INTO bulletin_items VALUES('one','baseline','body',1);")
        connection.close()
        (self.folder.parent / "store").mkdir()
        snapshot = {"version": 1, "items": [{"id": "one", "title": "baseline", "body": "body", "version": 1}]}
        reviewer.save(self.folder.parent / "store/state.json", {"snapshot": snapshot, "ledger": {"synthetic": {"response": snapshot}}})

    def review(self):
        reviewer.save(self.folder / "observation.json", self.record)
        reviewer.save(self.folder / "events-v2-export-report.json", self.report)
        for name, values in [("events-v2.jsonl", self.events), ("export-v2-events-legacy.jsonl", self.raw)]:
            (self.folder / name).write_text("".join(json.dumps(value) + "\n" for value in values))
        return reviewer.review(self.folder)[1]

    def test_full_window_timeout_is_retained_as_valid(self):
        self.assertEqual(self.review()["validity"], "VALID")

    def test_short_window_is_invalid_even_without_sync_errors(self):
        self.record["end_elapsed_realtime_ms"] -= 1
        self.assertEqual(self.review()["validity"], "INVALID")

    def test_manual_contamination_cannot_pass(self):
        self.events[0]["source"] = "MANUAL"
        self.assertEqual(self.review()["validity"], "INVALID")

    def test_missing_lifecycle_evidence_cannot_pass(self):
        (self.folder / "background-checkpoint.json").unlink()
        self.assertEqual(self.review()["validity"], "INVALID")

    def test_aborted_capture_without_cleanup_evidence_is_retained(self):
        self.record.update(execution_status="ABORTED", outcome="FAILURE", cleanup_passed=False)
        (self.folder / "cleanup-checkpoint.json").unlink()
        audit = self.review()
        self.assertEqual(audit["validity"], "INVALID")
        self.assertFalse(audit["checks"]["cleanup_evidence"])
        self.assertFalse(audit["checks"]["cleanup"])
        self.assertEqual(reviewer.load(self.folder / "observation.json")["outcome"], "FAILURE")

    def test_completed_capture_cannot_pass_without_cleanup_evidence(self):
        (self.folder / "cleanup-checkpoint.json").unlink()
        self.assertEqual(self.review()["validity"], "INVALID")

    def offline_case(self, applied_at=None):
        self.record.update(case_id="E04", offline_elapsed_realtime_ms=2000,
                           reconnect_elapsed_realtime_ms=122000, end_elapsed_realtime_ms=1922000)
        reviewer.save(self.folder / "offline-proof.json", {
            "default_network_absent": True, "guest_server_http_reachable": False,
            "same_boot_as_batch": True, "elapsed_realtime_ms": 2100})
        if applied_at is not None:
            self.record.update(outcome="SUCCESS", new_periodic_cycles=1)
            for offset, kind in enumerate(("work_started", "snapshot_fetch_started",
                                           "snapshot_fetch_completed", "snapshot_applied")):
                event = {"event_id": "synthetic-" + kind, "event_type": kind,
                         "request_id": "synthetic-request", "source": "PERIODIC",
                         "work_id": "synthetic-work", "elapsed_realtime_ms": applied_at - 3 + offset,
                         "data_version": 2, "outcome": "success", "network_call_id": "synthetic-fetch"}
                self.events.append(event)
                self.raw.append({"eventId": event["event_id"]})
            self.report["exported_event_count"] = len(self.events)

    def test_offline_target_apply_invalidates_otherwise_successful_e04(self):
        self.offline_case(applied_at=120000)
        audit = self.review()
        self.assertEqual(audit["validity"], "INVALID")
        self.assertFalse(audit["checks"]["target_applied_after_reconnect"])
        self.assertTrue(audit["checks"]["applied_fetch_provenance"])
        self.assertTrue(audit["checks"]["record_outcome"])
        self.assertEqual(audit["applied_target_count_in_window"], 1)

    def test_e04_target_apply_after_reconnect_is_valid(self):
        self.offline_case(applied_at=122004)
        self.assertEqual(self.review()["validity"], "VALID")

    def test_e04_target_apply_at_reconnect_boundary_is_valid(self):
        self.offline_case(applied_at=122000)
        self.assertEqual(self.review()["validity"], "VALID")

    def test_e04_full_window_timeout_remains_valid(self):
        self.offline_case()
        audit = self.review()
        self.assertEqual(audit["validity"], "VALID")
        self.assertEqual(audit["applied_target_count_in_window"], 0)

    def test_e04_missing_reconnect_cannot_qualify(self):
        self.offline_case(applied_at=122004)
        self.record.pop("reconnect_elapsed_realtime_ms")
        self.assertEqual(self.review()["validity"], "INVALID")

    def test_equal_version_with_different_cache_payload_is_invalid(self):
        connection = sqlite3.connect(str(self.folder / "setup-db/seminar_bulletin.db"))
        connection.execute("UPDATE bulletin_items SET body='different epoch'")
        connection.commit()
        connection.close()
        audit = self.review()
        self.assertEqual(audit["validity"], "INVALID")
        self.assertEqual(audit["baseline_content"]["reason"], "BASELINE_PAYLOAD_MISMATCH")

    def test_later_updates_do_not_rewrite_the_recorded_baseline(self):
        path = self.folder.parent / "store/state.json"
        state = reviewer.load(path)
        state["snapshot"] = {"version": 2, "items": []}
        reviewer.save(path, state)
        self.assertEqual(self.review()["validity"], "VALID")

    def test_missing_raw_row_refuses_export(self):
        self.raw = []
        with self.assertRaisesRegex(reviewer.canonical.ExportError, "RAW_EVENT_ACCOUNTING_MISMATCH"):
            self.review()

    def test_missing_critical_producer_event_makes_run_invalid(self):
        self.report["omitted_events"] = [{"event_id": "synthetic-missing", "event_type": "snapshot_applied"}]
        self.report["omitted_event_count"] = 1
        self.raw.append({"eventId": "synthetic-missing"})
        self.assertEqual(self.review()["validity"], "INVALID")

    def test_running_window_refuses_export(self):
        self.record["stage"] = "NATURAL_PERIODIC"
        self.record["execution_status"] = "RUNNING"
        with self.assertRaisesRegex(reviewer.canonical.ExportError, "RUN_NOT_FINISHED"):
            self.review()


if __name__ == "__main__":
    unittest.main()
