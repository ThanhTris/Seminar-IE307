"""SEM-45 tool tests use synthetic data only, never device measurements."""

import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("sem45_analyze", SCRIPTS / "analyze.py")
analyzer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analyzer)
FIXTURE = SCRIPTS.parents[1] / "experiments/fixture_exports/run-sem24-fixture"


class InputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.manifest = json.loads((FIXTURE / "manifest.json").read_text(encoding="utf-8"))
        self.events = [json.loads(line) for line in
                       (FIXTURE / "events.jsonl").read_text(encoding="utf-8").splitlines()]

    def load(self, dataset="fixture", raw_events=None):
        (self.directory / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        (self.directory / "events.jsonl").write_text(
            raw_events if raw_events is not None else
            "".join(json.dumps(e) + "\n" for e in self.events), encoding="utf-8")
        return analyzer.load_run(self.directory, dataset)

    def test_sem24_export_is_read_without_changing_values(self):
        run = self.load()
        self.assertEqual(run["events"], self.events)
        self.assertEqual(run["manifest"], self.manifest)
        self.assertEqual(run["duplicates"], 0)
        self.assertEqual(len(run["events_sha256"]), 64)

    def test_fixture_cannot_be_main(self):
        with self.assertRaisesRegex(analyzer.AnalysisError, "DATA_KIND_MISMATCH"):
            self.load("main")

    def test_legacy_pilot_is_rejected_without_inventing_fields(self):
        self.manifest["event_schema_version"] = "legacy-room-v1"
        with self.assertRaisesRegex(analyzer.AnalysisError, "CONTRACT_VERSION_UNSUPPORTED"):
            self.load()

    def test_other_run_or_mode_is_not_silently_joined(self):
        for key, value in (("run_id", "other-run"), ("device_alias", "other-device"),
                           ("mode", "HYBRID")):
            with self.subTest(key=key):
                old = self.events[0][key]
                self.events[0][key] = value
                with self.assertRaisesRegex(analyzer.AnalysisError, "EVENT_MANIFEST_MISMATCH"):
                    self.load()
                self.events[0][key] = old

    def test_replay_deduplicates_by_id_and_conflict_aborts(self):
        self.events.append(copy.deepcopy(self.events[0]))
        self.assertEqual(self.load()["duplicates"], 1)
        self.events[-1]["timestamp_utc"] = "2026-11-03T00:00:04Z"
        with self.assertRaisesRegex(analyzer.AnalysisError, "CONFLICTING_EVENT_ID"):
            self.load()

    def test_duplicate_keys_nonfinite_and_blank_lines_rejected(self):
        for raw in ('{"run_id":"one","run_id":"two"}\n', '{"value":NaN}\n', '\n'):
            with self.subTest(raw=raw), self.assertRaises(analyzer.AnalysisError):
                self.load(raw_events=raw)

    def test_unknown_schema_fields_and_event_types_rejected(self):
        self.events[0]["extra"] = True
        with self.assertRaisesRegex(analyzer.AnalysisError, "CANONICAL_FIELDS_REQUIRED"):
            self.load()
        del self.events[0]["extra"]
        self.events[0]["event_type"] = "future_event"
        with self.assertRaisesRegex(analyzer.AnalysisError, "EVENT_TYPE_UNSUPPORTED"):
            self.load()

    def test_no_not_run_observed_events(self):
        self.manifest.update(data_kind="OBSERVED", run_phase="pilot")
        with self.assertRaisesRegex(analyzer.AnalysisError, "NOT_RUN_HAS_EVENTS"):
            # Remove the deliberately synthetic FCM response ID first.
            self.events = [e for e in self.events if e["origin"] == "ANDROID"]
            self.load("pilot")


if __name__ == "__main__":
    unittest.main()
