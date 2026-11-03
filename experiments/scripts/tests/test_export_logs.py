"""Synthetic SEM-24 tool checks; never app/server/FCM experiment results."""

from contextlib import redirect_stderr, redirect_stdout
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "export_logs.py"
REPO = SCRIPT.parents[2]
FIXTURE = REPO / "experiments/fixtures/sem24"
spec = importlib.util.spec_from_file_location("export_logs", SCRIPT)
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.root_patch = patch.object(exporter, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.manifest = json.loads((FIXTURE / "manifest.json").read_text())
        self.android = [json.loads(x) for x in (FIXTURE / "android.jsonl").read_text().splitlines()]
        self.server = [json.loads(x) for x in (FIXTURE / "server.jsonl").read_text().splitlines()]
        self.deny = ["SYNTHETIC_PRIVATE_TOKEN", "SYNTHETIC_PRIVATE_SERIAL"]

    def invoke(self, fixture=True, android=True, server=True, extra=()):
        (self.root / "manifest.json").write_text(json.dumps(self.manifest))
        (self.root / "deny.json").write_text(json.dumps(self.deny))
        args = ["--manifest", str(self.root / "manifest.json"), "--run-id", self.manifest["run_id"], "--device-alias", self.manifest["device_alias"], "--deny-values", str(self.root / "deny.json")]
        for enabled, name, events in ((android, "android", self.android), (server, "server", self.server)):
            if enabled:
                path = self.root / (name + ".jsonl")
                path.write_text("".join(json.dumps(e) + "\n" for e in events))
                args += ["--" + name + "-log", str(path)]
        if fixture:
            args += ["--fixture"]
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = exporter.main(args + list(extra))
        self.output = out.getvalue()
        self.error = err.getvalue()
        self.public = self.root / "experiments" / ("fixture_exports" if fixture else "runs") / self.manifest["run_id"]
        return code

    def failure(self, **kwargs):
        self.assertEqual(self.invoke(**kwargs), 2)
        self.assertFalse(self.public.exists())
        self.assertNotIn("Traceback", self.error)
        for value in self.deny:
            self.assertNotIn(value, self.output + self.error)

    def test_selected_events_preserve_values_and_correlation(self):
        self.assertEqual(self.invoke(), 0)
        actual = [json.loads(x) for x in (self.public / "events.jsonl").read_text().splitlines()]
        expected = [{k: e[k] for k in exporter.FIELDS} for e in self.android[:-1] + self.server[:2]]
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 8)
        report = json.loads((self.public / "export_report.json").read_text())
        self.assertEqual(report["sources"][0]["other_run_or_device"], 1)
        self.assertEqual(report["sources"][1]["duplicates"], 1)
        self.assertFalse(report["analysis_performed"])
        text = "".join(p.read_text() for p in self.public.iterdir())
        for value in self.deny:
            self.assertNotIn(value, text)
        self.assertEqual(json.loads((self.public / "manifest.json").read_text()), self.manifest)

    def test_other_device_never_joins_selected_run(self):
        self.android[-1]["run_id"] = self.manifest["run_id"]
        self.android[-1]["device_alias"] = "other-device"
        self.assertEqual(self.invoke(), 0)
        self.assertEqual(json.loads(self.output)["events"], 8)

    def test_conflicting_event_id_aborts_without_output(self):
        self.server[-1]["timestamp_utc"] = "2026-11-03T00:00:02Z"
        self.failure()
        self.assertIn("CONFLICTING_EVENT_ID", self.error)

    def test_known_secret_in_allowed_field_aborts_without_rewriting(self):
        self.android[0]["message_id"] = self.deny[0]
        self.failure()
        self.assertIn("DENIED_PUBLIC_VALUE", self.error)

    def test_credential_signature_in_manifest_aborts(self):
        self.manifest["device"]["model"] = "AIza" + "x" * 35
        self.failure()
        self.assertIn("SENSITIVE_PUBLIC_VALUE", self.error)

    def test_extra_manifest_fields_are_not_published(self):
        self.manifest["token"] = self.deny[0]
        self.manifest["device"]["serial"] = self.deny[1]
        self.assertEqual(self.invoke(), 0)
        text = (self.public / "manifest.json").read_text()
        self.assertNotIn(self.deny[0], text)
        self.assertNotIn(self.deny[1], text)

    def test_nested_object_cannot_bypass_leaf_allowlist(self):
        self.manifest["device"]["model"] = {"token": self.deny[0]}
        self.failure()

    def test_template_is_not_an_exportable_manifest(self):
        self.manifest["data_kind"] = "TEMPLATE"
        self.failure()

    def test_fixture_requires_explicit_flag(self):
        self.failure(fixture=False)

    def test_fixture_cannot_be_main(self):
        self.manifest["run_phase"] = "main"
        self.failure()

    def test_fixture_source_cannot_be_relabelled_observed(self):
        self.manifest["data_kind"] = "OBSERVED"
        self.manifest["execution_status"] = "COMPLETED"
        self.manifest["outcome"] = "UNKNOWN"
        self.manifest["reason_codes"] = ["FIXTURE_TEST_ONLY"]
        self.failure(fixture=False)
        self.assertIn("FIXTURE_INPUT_FOR_OBSERVED", self.error)

    def test_legacy_events_do_not_get_synthetic_fields(self):
        del self.android[0]["schema_version"]
        self.failure()
        self.assertIn("EVENT_FIELDS_MISSING", self.error)

    def test_unknown_event_is_not_silently_lost(self):
        self.android[0]["event_type"] = "future_receipt"
        self.failure()

    def test_unsupported_major_is_rejected(self):
        self.android[0]["schema_version"] = "1.0.0"
        self.failure()

    def test_hint_is_not_applied_data(self):
        self.android[0]["data_version"] = 1
        self.failure()
        self.assertIn("RECEIPT_NOT_DATA", self.error)

    def test_applied_must_match_cache(self):
        self.android[-2]["cached_version"] = 0
        self.failure()

    def test_boolean_cannot_be_integer_measurement(self):
        self.android[0]["elapsed_realtime_ms"] = True
        self.failure()

    def test_nan_is_not_json_measurement(self):
        self.android[0]["elapsed_realtime_ms"] = float("nan")
        self.failure()

    def test_source_mode_mismatch_rejected(self):
        self.android[1]["mode"] = "PERIODIC"
        self.failure()

    def test_send_accepted_requires_provider_id(self):
        self.server[1]["message_id"] = None
        self.failure()

    def test_duplicate_key_rejected_without_echo(self):
        with self.assertRaises(exporter.ExportError) as error:
            exporter.parse_json('{"x":1,"x":"SYNTHETIC_PRIVATE_TOKEN"}')
        self.assertEqual(str(error.exception), "DUPLICATE_JSON_KEY")

    def test_clock_claim_needs_before_and_after_samples(self):
        self.manifest["clock"]["controlled"] = True
        self.failure()
        self.assertIn("CLOCK_EVIDENCE_REQUIRED", self.error)

    def test_main_valid_run_requires_candidate(self):
        self.manifest.update(data_kind="OBSERVED", run_phase="main", validity="VALID", execution_status="COMPLETED", outcome="TIMEOUT", reason_codes=["TIMEOUT"])
        self.manifest["build"]["candidate_gate_passed"] = None
        self.android = []
        self.server = []
        self.failure(fixture=False)

    def test_timeout_and_late_event_are_not_rewritten_to_success(self):
        self.manifest.update(data_kind="OBSERVED", run_phase="pilot", validity="VALID", execution_status="COMPLETED", outcome="TIMEOUT", reason_codes=["TIMEOUT"])
        for e in self.android + self.server:
            e.pop("fixture", None)
            if e["message_id"] is not None:
                e["message_id"] = "projects/test-only/messages/test-123"
        self.android[-2]["timestamp_utc"] = "2026-11-03T00:03:00Z"
        self.assertEqual(self.invoke(fixture=False), 0)
        saved = json.loads((self.public / "manifest.json").read_text())
        self.assertEqual(saved["outcome"], "TIMEOUT")
        self.assertEqual(saved["observation"], self.manifest["observation"])
        self.assertIn("2026-11-03T00:03:00Z", (self.public / "events.jsonl").read_text())

    def test_output_never_overwrites_previous_export(self):
        self.assertEqual(self.invoke(), 0)
        original = (self.public / "events.jsonl").read_bytes()
        self.assertEqual(self.invoke(), 2)
        self.assertEqual((self.public / "events.jsonl").read_bytes(), original)

    def test_not_run_blocker_can_export_without_events(self):
        self.manifest.update(data_kind="OBSERVED", reason_codes=["DEVICE_UNAVAILABLE"])
        self.assertEqual(self.invoke(fixture=False, android=False, server=False), 0)
        self.assertEqual((self.public / "events.jsonl").read_text(), "")

    def test_observed_not_run_cannot_claim_events(self):
        self.manifest["data_kind"] = "OBSERVED"
        for e in self.android + self.server:
            e.pop("fixture", None)
            if e["message_id"] is not None:
                e["message_id"] = "projects/test-only/messages/test-123"
        self.failure(fixture=False)

    def test_adb_private_capture_and_serial_never_published(self):
        mapping = self.root / "devices.json"
        mapping.write_text(json.dumps({self.manifest["device_alias"]: self.deny[1]}))
        raw = "".join(json.dumps(e) + "\n" for e in self.android).encode()
        result = subprocess.CompletedProcess([], 0, stdout=raw, stderr=b"private diagnostic")
        with patch.object(exporter.subprocess, "run", return_value=result) as call:
            self.assertEqual(self.invoke(android=False, extra=("--adb", "fake-adb", "--device-map", str(mapping))), 0)
        self.assertEqual(call.call_args.args[0], ["fake-adb", "-s", self.deny[1], "exec-out", "run-as", "com.thanhtris.seminarie307", "cat", "files/experiment-events.jsonl"])
        captures = list((self.root / "experiments/private").rglob("android.raw.jsonl"))
        self.assertEqual(len(captures), 1)
        self.assertEqual(captures[0].read_bytes(), raw)
        if os.name != 'nt':
            self.assertEqual(captures[0].stat().st_mode & 0o777, 0o600)
            self.assertEqual(captures[0].parent.stat().st_mode & 0o777, 0o700)
        self.assertNotIn(self.deny[1], "".join(p.read_text() for p in self.public.iterdir()))

    def test_adb_failure_does_not_expose_stderr_or_fallback(self):
        mapping = self.root / "devices.json"
        mapping.write_text(json.dumps({self.manifest["device_alias"]: self.deny[1]}))
        result = subprocess.CompletedProcess([], 1, stdout=b"", stderr=self.deny[0].encode())
        with patch.object(exporter.subprocess, "run", return_value=result) as call:
            self.failure(android=False, extra=("--adb", "fake-adb", "--device-map", str(mapping)))
        self.assertEqual(call.call_count, 1)
        self.assertEqual(self.error, "ERROR ADB_CAPTURE_FAILED\n")

    def test_path_traversal_cannot_choose_output_location(self):
        self.manifest["run_id"] = "../../outside"
        self.failure()

    def test_observed_export_requires_local_sensitive_values_file(self):
        args = ["--manifest", str(FIXTURE / "manifest.json"), "--run-id", "run-sem24-fixture", "--device-alias", "fixture-device"]
        error = io.StringIO()
        with redirect_stderr(error):
            self.assertEqual(exporter.main(args), 2)
        self.assertEqual(error.getvalue(), "ERROR DENY_VALUES_REQUIRED_FOR_OBSERVED\n")

    def test_hash_preserves_original_crlf_input_bytes(self):
        content = ("".join(json.dumps(e) + "\r\n" for e in self.android)).encode()
        path = self.root / "crlf.jsonl"
        path.write_bytes(content)
        text = exporter.read_text(path)
        _, reports = exporter.select_events([("ANDROID", text)], self.manifest, True)
        self.assertEqual(reports[0]["sha256"], hashlib.sha256(content).hexdigest())

    def test_fixture_marker_string_is_not_a_boolean(self):
        self.android[0]["fixture"] = "true"
        self.failure()

    def test_not_run_cannot_have_success_outcome(self):
        self.manifest["outcome"] = "SUCCESS"
        self.failure()

    def test_invalid_unicode_fails_before_public_output(self):
        self.manifest["device"]["model"] = "\ud800"
        self.failure()
        self.assertIn("INVALID_UNICODE", self.error)

    def test_all_current_event_types_have_valid_examples(self):
        started, applied = self.android[2], self.android[5]
        base = copy.deepcopy(started)
        cases = {
            "trigger_rejected": {"outcome": "rejected", "reason": "MODE_DISABLED"},
            "periodic_registered": {"source": "PERIODIC", "mode": "PERIODIC", "request_id": None, "outcome": "registered"},
            "snapshot_unchanged": {"outcome": "unchanged", "data_version": 0, "cached_version": 0},
            "snapshot_stale": {"outcome": "stale", "data_version": 0, "cached_version": 1, "reason": "VERSION_STALE"},
            "sync_retrying": {"outcome": "retry", "reason": "NETWORK_ERROR"},
            "sync_failed": {"outcome": "failure", "reason": "RETRY_EXHAUSTED"},
        }
        events = [*self.android[:-1], *self.server[:2]]
        for kind, delta in cases.items():
            events.append({**base, "event_type": kind, **delta})
        server = copy.deepcopy(self.server[1])
        for kind, delta in {
            "push_send_rejected": {"outcome": "rejected", "reason": "FCM_REJECTED", "message_id": None, "http_status": 404},
            "push_send_unknown": {"outcome": "unknown", "reason": "FCM_RESPONSE_UNKNOWN", "message_id": None, "http_status": None},
            "push_send_failed_local": {"outcome": "failure", "reason": "INVALID_FCM_CONFIG", "message_id": None, "send_attempt_id": None, "provider_code": None, "http_status": None},
            "push_send_skipped": {"outcome": "skipped", "reason": "FAULT_INJECTION_SKIP", "message_id": None, "send_attempt_id": None, "http_status": None},
        }.items():
            events.append({**server, "event_type": kind, **delta})
        self.assertEqual({e["event_type"] for e in events}, set(exporter.EVENTS))
        for event in events:
            with self.subTest(event=event["event_type"]):
                canonical = exporter.validate_event(event)
                self.assertEqual(set(canonical), set(exporter.FIELDS))


if __name__ == "__main__":
    unittest.main()
