"""Regression checks for the collector's ability to change scheduler state."""

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_sem41_periodic_pilots import PilotBatch
from sem41_scheduler_observation import scheduler_collection


class SchedulerObservationTests(unittest.TestCase):
    def test_scheduler_dump_is_blocked_before_any_adb_call_while_clock_open(self):
        batch = PilotBatch.__new__(PilotBatch)
        batch.record = {"start_elapsed_realtime_ms": 100}
        batch.adb = Mock(return_value="")
        with self.assertRaisesRegex(RuntimeError, "SCHEDULER_DUMP_DURING_OPEN_WINDOW"):
            batch.shell("dumpsys", "jobscheduler", "package")
        batch.adb.assert_not_called()

    def test_snapshot_after_closed_clock_is_allowed(self):
        batch = PilotBatch.__new__(PilotBatch)
        batch.record = {"start_elapsed_realtime_ms": 100, "end_elapsed_realtime_ms": 200}
        batch.adb = Mock(return_value="state\n")
        self.assertEqual(batch.shell("dumpsys", "jobscheduler", "package"), "state")
        batch.adb.assert_called_once()

    def test_default_checkpoint_does_not_query_scheduler(self):
        batch = PilotBatch.__new__(PilotBatch)
        batch.baseline = {}
        batch.elapsed = Mock(return_value=150)
        batch.capture = Mock(side_effect=["mState=ACTIVE mNetworkConnected=true mScreenOn=true",
                                         "topResumedActivity=launcher", "stopped=false", "battery"])
        with tempfile.TemporaryDirectory() as directory:
            batch.current = Path(directory)
            state = batch.checkpoint("during")
        self.assertFalse(state["scheduler_dump_performed"])
        self.assertTrue(state["network_connected"])
        self.assertFalse(any("jobscheduler" in call.args for call in batch.capture.call_args_list))

    def test_in_window_dump_invalidates_collection_even_if_label_says_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "during-checkpoint.json").write_text(json.dumps({
                "elapsed_realtime_ms": 150, "scheduler_dump_performed": False}))
            (folder / "during-jobs.txt").write_text(
                "Registered 1 jobs:\nUnsatisfied constraints: TIMING_DELAY\nReady: true\n"
                "PrefetchController:\nTimeController:\nElapsed clock: 150\nIdleController:\n")
            result = scheduler_collection(folder, {"start_elapsed_realtime_ms": 100,
                                                    "end_elapsed_realtime_ms": 200})
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["timer_transition_count"], 1)
        self.assertFalse(result["events_or_outcomes_modified"])

    def test_setup_and_after_window_dumps_do_not_invalidate_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for name, stamp in [("setup", 90), ("after", 210)]:
                (folder / (name + "-checkpoint.json")).write_text(json.dumps({"elapsed_realtime_ms": stamp}))
                (folder / (name + "-jobs.txt")).write_text("scheduler dump")
            result = scheduler_collection(folder, {"start_elapsed_realtime_ms": 100,
                                                    "end_elapsed_realtime_ms": 200})
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["in_window_dump_count"], 0)

    def test_missing_clock_is_unassessed_not_a_valid_completed_measurement(self):
        with tempfile.TemporaryDirectory() as directory:
            result = scheduler_collection(directory, {})
        self.assertEqual(result["status"], "NOT_ASSESSED")

    def test_checkpoint_without_clock_cannot_claim_outside_window(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "missing-checkpoint.json").write_text("{}")
            result = scheduler_collection(folder, {"start_elapsed_realtime_ms": 100,
                                                    "end_elapsed_realtime_ms": 200})
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["reason"], "SCHEDULER_OBSERVATION_CLOCK_MISSING")


if __name__ == "__main__":
    unittest.main()
