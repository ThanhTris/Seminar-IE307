"""SEM-45 tool tests use synthetic data only, never device measurements."""

import copy
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

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

    def test_malformed_types_return_static_error_instead_of_traceback(self):
        self.manifest["mode"] = []
        with self.assertRaisesRegex(analyzer.AnalysisError, "INPUT_TYPES_INVALID"):
            self.load()

    def test_no_not_run_observed_events(self):
        self.manifest.update(data_kind="OBSERVED", run_phase="pilot")
        with self.assertRaisesRegex(analyzer.AnalysisError, "NOT_RUN_HAS_EVENTS"):
            # Remove the deliberately synthetic FCM response ID first.
            self.events = [e for e in self.events if e["origin"] == "ANDROID"]
            self.load("pilot")


class MetricTests(unittest.TestCase):
    load = InputTests.load

    def setUp(self):
        InputTests.setUp(self)
        self.manifest.update(execution_status="COMPLETED", outcome="SUCCESS", validity="VALID")
        self.manifest["observation"].update(start_elapsed_realtime_ms=30000,
            end_elapsed_realtime_ms=150000, boot_session_id="boot-fixture-01")
        self.next_id = 100

    def analyze(self):
        return analyzer.analyze_run(self.load())

    def event(self, kind, ms, **changes):
        base = copy.deepcopy(next(e for e in self.events if e["event_type"] == "work_started"))
        self.next_id += 1
        base.update(event_id=f"00000000-0000-4000-8000-{self.next_id:012d}", event_type=kind,
                    elapsed_realtime_ms=ms,
                    timestamp_utc=(datetime(2026, 11, 3, tzinfo=timezone.utc) +
                                   timedelta(milliseconds=ms - 30000)).isoformat().replace("+00:00", "Z"))
        base["outcome"] = next(iter(analyzer.contract.EVENTS[kind][2]))
        if kind == "sync_retrying":
            base["reason"] = "NETWORK_ERROR"
        if kind == "sync_failed":
            base["reason"] = "RETRY_EXHAUSTED"
        if kind == "snapshot_applied":
            base.update(data_version=1, cached_version=1)
        base.update(changes)
        self.events.append(base)
        return base

    def controlled_clock(self, reference="ANDROID"):
        sample = {"client_send_utc": "2026-11-02T23:59:59Z",
                  "client_receive_utc": "2026-11-02T23:59:59.010Z",
                  "server_utc": "2026-11-03T00:00:00.005Z", "resolution_ms": 1}
        after = {"client_send_utc": "2026-11-03T00:02:01Z",
                 "client_receive_utc": "2026-11-03T00:02:01.010Z",
                 "server_utc": "2026-11-03T00:02:02.005Z", "resolution_ms": 1}
        self.manifest["clock"].update(controlled=True, client_clock=reference, method_code="FIXTURE_CLOCK",
            offset_before_ms=1000, offset_after_ms=1000, uncertainty_before_ms=6,
            uncertainty_after_ms=6, before_samples=[sample] * 3, after_samples=[after] * 3)

    def test_stages_are_separate_and_uncontrolled_cross_clock_is_null(self):
        row = self.analyze()["row"]
        self.assertEqual(row["received_to_enqueue_ms"], 1000)
        self.assertEqual(row["queue_ms"], 1000)
        self.assertEqual(row["sync_ms"], 3000)
        self.assertIsNone(row["update_to_applied_ms"])
        self.assertIsNone(row["db_write_count"])
        self.assertEqual(row["get_started_count"], 1)
        self.assertEqual(row["observed_completion"], "APPLIED_TARGET")
        self.assertFalse(row["eligible"])  # Still synthetic, never a main sample.

    def test_timeout_with_late_apply_stays_timeout_and_latency_empty(self):
        self.manifest.update(outcome="TIMEOUT", reason_codes=["TIMEOUT"])
        applied = next(e for e in self.events if e["event_type"] == "snapshot_applied")
        applied["elapsed_realtime_ms"] = 150001
        row = self.analyze()["row"]
        self.assertEqual(row["outcome"], "TIMEOUT")
        self.assertEqual(row["observed_completion"], "LATE_TARGET")
        self.assertEqual(row["late_target_applied_count"], 1)
        self.assertFalse(row["target_applied_in_window"])
        self.assertIsNone(row["sync_ms"])
        self.assertIsNone(row["update_to_applied_ms"])

    def test_accepted_without_receipt_is_not_completion(self):
        self.events = [e for e in self.events if e["origin"] == "SERVER"]
        self.manifest.update(outcome="UNKNOWN", reason_codes=["FCM_RESPONSE_UNKNOWN"])
        row = self.analyze()["row"]
        self.assertFalse(row["target_applied_in_window"])
        self.assertIsNone(row["received_to_enqueue_ms"])
        self.assertEqual(row["observed_completion"], "NO_TARGET_EVIDENCE")

    def test_monotonic_survives_wall_clock_jump_and_input_order(self):
        self.events.reverse()
        next(e for e in self.events if e["event_type"] == "snapshot_applied")["timestamp_utc"] = "2026-11-02T00:00:00Z"
        row = self.analyze()["row"]
        self.assertEqual(row["sync_ms"], 3000)
        self.assertTrue(row["target_applied_in_window"])

    def test_reboot_and_unknown_boot_do_not_produce_duration_or_completion(self):
        applied = next(e for e in self.events if e["event_type"] == "snapshot_applied")
        for boot in (None, "boot-other"):
            with self.subTest(boot=boot):
                applied["boot_session_id"] = boot
                row = self.analyze()["row"]
                self.assertIsNone(row["sync_ms"])
                self.assertFalse(row["target_applied_in_window"])
                self.assertIn("ANDROID_WINDOW_OR_BOOT_UNKNOWN", row["flags"])

    def test_clock_offset_sign_and_uncertainty(self):
        self.controlled_clock()
        row = self.analyze()["row"]
        self.assertEqual(row["update_to_applied_ms"], 8000)
        self.assertEqual(row["update_to_received_ms"], 3000)
        self.assertEqual(row["update_to_applied_uncertainty_ms"], 6)
        # Response can be logged after callback; it is not a receipt timestamp.
        next(e for e in self.events if e["event_type"] == "push_send_accepted")["timestamp_utc"] = "2026-11-03T00:00:10Z"
        self.assertEqual(self.analyze()["row"]["update_to_received_ms"], 3000)

    def test_host_clock_bad_samples_and_negative_bound_not_used(self):
        self.controlled_clock("HOST")
        self.assertIsNone(self.analyze()["row"]["update_to_applied_ms"])
        self.controlled_clock()
        self.manifest["clock"]["uncertainty_before_ms"] = 0
        self.assertIsNone(self.analyze()["row"]["update_to_applied_ms"])
        self.controlled_clock()
        server = next(e for e in self.events if e["event_type"] == "server_updated")
        server["timestamp_utc"] = "2026-11-03T00:00:08Z"
        self.assertIsNone(self.analyze()["row"]["update_to_applied_ms"])

    def test_missing_enqueue_and_ambiguous_receipts_do_not_guess(self):
        receipt = copy.deepcopy(next(e for e in self.events if e["event_type"] == "push_received"))
        receipt["event_id"] = "00000000-0000-4000-8000-000000000099"
        self.events.append(receipt)
        self.assertIsNone(self.analyze()["row"]["received_to_enqueue_ms"])
        self.events = [e for e in self.events if e["event_type"] != "work_enqueued"]
        self.assertIsNone(self.analyze()["row"]["queue_ms"])

    def test_retry_keeps_logical_request_and_each_get_separate(self):
        self.event("sync_retrying", 36500)
        self.event("work_started", 38000, work_attempt=1)
        for e in self.events:
            if e["event_type"] == "snapshot_applied":
                e.update(work_attempt=1, elapsed_realtime_ms=41000)
        self.event("snapshot_fetch_started", 39000, work_attempt=1,
                   network_call_id="00000000-0000-4000-8000-000000000020")
        self.event("snapshot_fetch_completed", 40000, work_attempt=1,
                   network_call_id="00000000-0000-4000-8000-000000000020",
                   outcome="success", data_version=1, http_status=200)
        result = self.analyze()
        self.assertEqual(result["row"]["work_attempt_count"], 2)
        self.assertEqual(result["row"]["retry_event_count"], 1)
        self.assertEqual(result["row"]["get_started_count"], 2)
        self.assertEqual(result["row"]["sync_ms"], 3000)
        self.assertEqual([f["duration_ms"] for f in result["fetches"]], [1000, 1000])

    def test_shared_work_id_is_not_shared_periodic_cycle(self):
        self.manifest.update(case_id="E01", mode="PERIODIC")
        self.manifest["observation"].update(planned_window_seconds=5400, actual_duration_ms=5400000,
                                           end_elapsed_realtime_ms=5430000)
        self.events = [e for e in self.events if e["event_type"] in {"work_started", "snapshot_applied"}]
        for e in self.events:
            e.update(mode="PERIODIC", source="PERIODIC", signal_ids=[])
        self.event("work_started", 940000, mode="PERIODIC", source="PERIODIC", request_id="cycle-two", signal_ids=[])
        self.event("work_started", 950000, mode="PERIODIC", source="PERIODIC", request_id="cycle-two", work_attempt=1, signal_ids=[])
        row = self.analyze()["row"]
        self.assertEqual(row["natural_periodic_cycles"], 2)
        self.assertEqual(row["work_attempt_count"], 3)

    def test_setup_recovery_manual_and_short_window_are_flagged(self):
        next(e for e in self.events if e["event_type"] == "work_started")["elapsed_realtime_ms"] = 29000
        self.assertIn("TARGET_START_NOT_IN_WINDOW", self.analyze()["row"]["flags"])
        self.event("work_started", 45000, source="MANUAL", request_id="manual-request",
                   work_id="00000000-0000-4000-8000-000000000022", signal_ids=[])
        self.assertIn("MANUAL_IN_WINDOW", self.analyze()["row"]["flags"])
        self.manifest["observation"]["end_elapsed_realtime_ms"] = 50000
        self.assertIn("WINDOW_SHORT_OR_UNDECLARED", self.analyze()["row"]["flags"])

    def test_network_call_cannot_join_a_different_attempt(self):
        next(e for e in self.events if e["event_type"] == "snapshot_fetch_completed")["work_attempt"] = 1
        with self.assertRaisesRegex(analyzer.AnalysisError, "FETCH_CORRELATION_CONFLICT"):
            self.analyze()

    def test_same_target_hint_or_unchanged_does_not_imply_applied(self):
        self.events = [e for e in self.events if e["event_type"] != "snapshot_applied"]
        self.manifest.update(outcome="TIMEOUT", reason_codes=["TIMEOUT"])
        row = self.analyze()["row"]
        self.assertFalse(row["target_applied_in_window"])
        self.assertIsNone(row["sync_ms"])

    def test_group_identity_separates_phase_build_config_and_injection(self):
        original = analyzer.group_identity(self.manifest)
        for section, key, value in ((None, "run_phase", "main"), (None, "intervention", "INJECTED"),
                ("build", "apk_sha256", "4" * 64), ("config", "battery_saver", True)):
            m = copy.deepcopy(self.manifest)
            (m[section] if section else m)[key] = value
            self.assertNotEqual(analyzer.group_identity(m), original)

    def test_clock_samples_need_to_bracket_events_and_wall_clock_must_be_stable(self):
        self.controlled_clock()
        self.events[0]["timestamp_utc"] = "2026-11-03T01:00:00Z"
        result = self.analyze()
        self.assertIsNone(result["row"]["update_to_applied_ms"])
        self.assertIsNotNone(result["clock_reason"])

    def test_hybrid_skip_case_requires_real_skipped_event_for_the_target_update(self):
        self.manifest.update(case_id="E06", mode="HYBRID")
        self.manifest["observation"].update(planned_window_seconds=2700, actual_duration_ms=2700000,
                                           end_elapsed_realtime_ms=2730000)
        self.events = [e for e in self.events if e["event_type"] in
                       {"work_started", "snapshot_applied", "server_updated"}]
        for e in self.events:
            e["mode"] = "HYBRID"
            if e["origin"] == "ANDROID":
                e.update(source="PERIODIC", signal_ids=[])
        self.assertIn("FAULT_SKIP_EVIDENCE_MISSING", self.analyze()["row"]["flags"])
        skipped = copy.deepcopy(next(e for e in self.events if e["event_type"] == "server_updated"))
        skipped.update(event_id="00000000-0000-4000-8000-000000000099", event_type="push_send_skipped",
                       source="PUSH", outcome="skipped", reason="FAULT_INJECTION_SKIP")
        self.events.append(skipped)
        self.assertNotIn("FAULT_SKIP_EVIDENCE_MISSING", self.analyze()["row"]["flags"])


class OutputTests(unittest.TestCase):
    load = InputTests.load
    setUp = MetricTests.setUp

    def main_input(self):
        self.manifest.update(data_kind="OBSERVED", run_phase="main")
        self.manifest["build"]["candidate_gate_passed"] = True
        self.events = [e for e in self.events if e["event_type"] != "push_send_accepted"]
        return self.load("main")

    def test_csv_nulls_are_empty_not_zero_and_fixture_never_enters_denominator(self):
        result = analyzer.analyze_run(self.load())
        text = analyzer.csv_text([result])
        import csv
        row = next(csv.DictReader(io.StringIO(text)))
        self.assertEqual(row["update_to_applied_ms"], "")
        self.assertEqual(row["eligible"], "false")
        group = analyzer.summarize([result])[0]
        self.assertEqual(group["n_eligible"], 0)
        self.assertIsNone(group["completion_rate"])

    def test_valid_main_timeouts_remain_in_denominator(self):
        success = analyzer.analyze_run(self.main_input())
        self.manifest.update(outcome="TIMEOUT", reason_codes=["TIMEOUT"])
        self.events = [e for e in self.events if e["event_type"] != "snapshot_applied"]
        timeout = analyzer.analyze_run(self.load("main"))
        group = analyzer.summarize([success, timeout])[0]
        self.assertEqual(group["n_eligible"], 2)
        self.assertEqual(group["n_complete"], 1)
        self.assertEqual(group["completion_rate"], 0.5)
        self.assertEqual(group["eligible_outcomes"]["TIMEOUT"], 1)
        self.assertEqual(group["metrics"]["sync_ms"]["n_measured"], 1)
        self.assertIsNone(group["metrics"]["update_to_applied_ms"]["median"])

    def test_not_run_is_excluded_without_hiding_rows(self):
        self.main_input()
        self.manifest.update(execution_status="NOT_RUN", outcome="NOT_RUN", validity="NOT_ASSESSED")
        self.events = []
        analysis = analyzer.analyze_run(self.load("main"))
        group = analyzer.summarize([analysis])[0]
        self.assertEqual(group["n_input"], 1)
        self.assertEqual(group["n_not_run"], 1)
        self.assertEqual(group["n_excluded"], 1)

    def test_cannot_overwrite_output_and_report_hashes_match_bytes(self):
        import hashlib
        self.load()
        base = self.directory / "out"
        analyzer.publish([self.directory], "fixture", base, "one")
        output = base / "fixture_analysis/one"
        report = json.loads((output / "analysis_report.json").read_text(encoding="utf-8"))
        self.assertFalse(report["runtime_experiment_performed"])
        for filename, digest in report["outputs_sha256"].items():
            self.assertEqual(hashlib.sha256((output / filename).read_bytes()).hexdigest(), digest)
        with self.assertRaisesRegex(analyzer.AnalysisError, "OUTPUT_EXISTS"):
            analyzer.publish([self.directory], "fixture", base, "one")

    def test_multiple_batches_are_reproducible_and_inputs_unchanged(self):
        self.load()
        original = (self.directory / "events.jsonl").read_bytes()
        for batch in ("one", "two"):
            analyzer.publish([self.directory], "fixture", self.directory / "out", batch)
        for filename in ("results.csv", "summary.json"):
            self.assertEqual((self.directory / "out/fixture_analysis/one" / filename).read_bytes(),
                             (self.directory / "out/fixture_analysis/two" / filename).read_bytes())
        reports = [json.loads((self.directory / f"out/fixture_analysis/{batch}/analysis_report.json").read_text())
                   for batch in ("one", "two")]
        reports[0]["batch_id"] = reports[1]["batch_id"]
        self.assertEqual(reports[0], reports[1])
        self.assertEqual((self.directory / "events.jsonl").read_bytes(), original)

    def test_bad_input_or_duplicate_run_does_not_create_output(self):
        self.load()
        base = self.directory / "out"
        with self.assertRaisesRegex(analyzer.AnalysisError, "DUPLICATE_RUN_INPUT"):
            analyzer.publish([self.directory, self.directory], "fixture", base, "one")
        self.assertFalse(base.exists())
        self.events[0]["mode"] = "HYBRID"
        (self.directory / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in self.events), encoding="utf-8")
        with self.assertRaises(analyzer.AnalysisError):
            analyzer.publish([self.directory], "fixture", base, "two")
        self.assertFalse(base.exists())

    def test_cli_has_safe_errors_without_raw_fields_or_traceback(self):
        self.load()
        (self.directory / "events.jsonl").write_text('{"private":"SYNTHETIC_SECRET"}\n', encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = analyzer.main(["--run", str(self.directory), "--dataset", "fixture",
                                  "--output-base", str(self.directory / "out"), "--batch-id", "bad"])
        self.assertEqual(code, 2)
        self.assertIn("CANONICAL_FIELDS_REQUIRED", err.getvalue())
        self.assertNotIn("SYNTHETIC_SECRET", out.getvalue() + err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())

    def test_exporter_to_analyzer_integration(self):
        source = SCRIPTS.parents[1] / "experiments/fixtures/sem24"
        base = self.directory / "export"
        with patch.object(analyzer.contract, "ROOT", base), redirect_stdout(io.StringIO()):
            code = analyzer.contract.main(["--manifest", str(source / "manifest.json"),
                "--android-log", str(source / "android.jsonl"), "--server-log", str(source / "server.jsonl"),
                "--run-id", "run-sem24-fixture", "--device-alias", "fixture-device", "--fixture"])
        self.assertEqual(code, 0)
        exported = base / "experiments/fixture_exports/run-sem24-fixture"
        analyzer.publish([exported], "fixture", self.directory / "analysis", "integration")
        report = json.loads((self.directory / "analysis/fixture_analysis/integration/analysis_report.json").read_text())
        self.assertEqual(report["runs"][0]["event_counts"]["push_send_accepted"], 1)
        self.assertEqual(report["runs"][0]["row"]["outcome"], "NOT_RUN")

    def test_csv_results_do_not_depend_on_directory_input_order(self):
        self.load()
        second = self.directory / "second"
        second.mkdir()
        manifest = copy.deepcopy(self.manifest)
        manifest["run_id"] = "run-sem45-second"
        (second / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        events = [dict(e, run_id=manifest["run_id"]) for e in self.events]
        (second / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")
        for batch, inputs in (("one", [self.directory, second]), ("two", [second, self.directory])):
            analyzer.publish(inputs, "fixture", self.directory / "out", batch)
        for filename in ("results.csv", "summary.json"):
            self.assertEqual((self.directory / "out/fixture_analysis/one" / filename).read_bytes(),
                             (self.directory / "out/fixture_analysis/two" / filename).read_bytes())

    def test_missing_candidate_and_success_without_apply_do_not_enter_statistics(self):
        self.main_input()
        self.manifest["build"]["candidate_gate_passed"] = False
        with self.assertRaisesRegex(analyzer.AnalysisError, "MAIN_CANDIDATE_REQUIRED"):
            self.load("main")
        self.manifest["build"]["candidate_gate_passed"] = True
        self.events = [e for e in self.events if e["event_type"] != "snapshot_applied"]
        row = analyzer.analyze_run(self.load("main"))["row"]
        self.assertFalse(row["eligible"])
        self.assertIn("OUTCOME_EVIDENCE_CONFLICT", row["flags"])


if __name__ == "__main__":
    unittest.main()
