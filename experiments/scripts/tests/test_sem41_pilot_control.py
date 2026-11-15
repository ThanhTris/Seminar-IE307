"""Synthetic transition checks; never device measurements."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_sem41_periodic_pilots as pilot


class IdleRestoreTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.batch = pilot.PilotBatch.__new__(pilot.PilotBatch)
        self.batch.current = Path(temporary.name)
        self.batch.idle_changed = True

    def test_delayed_active_transition_is_confirmed_before_continuing(self):
        states = iter(["IDLE", "ACTIVE"])
        def shell(*args):
            return next(states) if args == ("dumpsys", "deviceidle", "get", "deep") else ""
        self.batch.shell = shell
        with patch.object(pilot.time, "sleep") as sleep:
            self.batch.restore_idle()
        self.assertFalse(self.batch.idle_changed)
        self.assertEqual(sleep.call_count, 1)
        proof = pilot.json.loads((self.batch.current / "idle-restore-1-transition.json").read_text())
        self.assertEqual(proof["status"], "PASS")
        self.assertEqual([sample["deep_idle"] for sample in proof["samples"]], ["IDLE", "ACTIVE"])

    def test_unconfirmed_exit_keeps_cleanup_required_and_records_failure(self):
        self.batch.shell = lambda *args: "IDLE" if args == ("dumpsys", "deviceidle", "get", "deep") else ""
        with patch.object(pilot.time, "sleep"), patch.object(pilot.time, "monotonic", side_effect=[0, 0, 11]):
            with self.assertRaisesRegex(RuntimeError, "IDLE_RESTORE_NOT_CONFIRMED"):
                self.batch.restore_idle()
        self.assertTrue(self.batch.idle_changed)
        proof = pilot.json.loads((self.batch.current / "idle-restore-1-transition.json").read_text())
        self.assertEqual(proof["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
