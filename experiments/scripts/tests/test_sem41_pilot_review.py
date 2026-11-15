"""Synthetic review checks, not measurements or pilot artifacts."""

import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import export_sem41_pilots as reviewer


class PilotReviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.record = {"run_id": "synthetic-review", "case_id": "E01", "stage": "FINISHED", "execution_status": "COMPLETED", "run_phase": "pilot", "candidate_gate_passed": False, "outcome": "TIMEOUT", "cleanup_passed": True, "start_elapsed_realtime_ms": 1000, "end_elapsed_realtime_ms": 5401000, "target_version": 2, "work_id": "synthetic-work", "new_periodic_cycles": 0}
        self.events = [{"event_id": "synthetic-registration", "event_type": "periodic_registered", "request_id": None, "source": "PERIODIC", "work_id": "synthetic-work", "elapsed_realtime_ms": 0}]
        self.raw = [{"eventId": "synthetic-registration"}]
        self.report = {"exported_event_count": 1, "omitted_event_count": 0, "omitted_events": []}
        reviewer.save(self.folder / "cleanup-checkpoint.json", {"package_stopped": False, "app_resumed": False, "network_connected": True, "idle": "ACTIVE"})
        for label in ("background", "window-end"):
            reviewer.save(self.folder / (label + "-checkpoint.json"), {"package_stopped": False, "app_resumed": False, "network_connected": True, "idle": "ACTIVE"})
        reviewer.save(self.folder / "export-v2-state.json", {"periodic_work": []})

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
