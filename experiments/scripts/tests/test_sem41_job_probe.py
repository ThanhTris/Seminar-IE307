"""Synthetic safeguards for diagnostic provenance/privacy; not device measurements."""

from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import probe_sem41_jobs as probe
from run_sem41_dispatch_diagnostic import exact_job, window_events


def sample():
    reason = {"code": 12, "name": "PENDING_JOB_REASON_QUOTA"}
    return {"probe_version": "1.0.0", "sdk_int": 37, "utc_epoch_ms": 1000,
            "elapsed_realtime_ms": 500, "package": probe.PACKAGE,
            "namespace": probe.NAMESPACE, "read_only": True, "jobs": [{
                "job_id": 2, "service": "androidx.work.impl.background.systemjob.SystemJobService",
                "work_id": "11111111-2222-3333-4444-555555555555", "generation": 0,
                "system_job_is_periodic": False, "minimum_latency_ms": 900000,
                "job_disappeared_during_query": False,
                "pending_reasons": [reason], "history": [{"timestamp_ms": 900, "reasons": [reason]}],
                "stats": [{"reason": reason, "duration_ms": 100}]}]}


class JobProbeTests(unittest.TestCase):
    def test_direct_dispatch_requires_exactly_one_matching_work(self):
        data = sample()
        work = data["jobs"][0]["work_id"]
        self.assertEqual(exact_job(data, work)["job_id"], 2)
        with self.assertRaisesRegex(RuntimeError, "EXACT_PENDING_WORK_REQUIRED"):
            exact_job(data, "99999999-2222-3333-4444-555555555555")
        data["jobs"].append(deepcopy(data["jobs"][0]))
        with self.assertRaisesRegex(RuntimeError, "EXACT_PENDING_WORK_REQUIRED"):
            exact_job(data, work)

    def test_disappeared_job_cannot_be_directly_dispatched(self):
        data = sample()
        data["jobs"][0]["job_disappeared_during_query"] = True
        with self.assertRaisesRegex(RuntimeError, "PENDING_JOB_QUERY_RACE"):
            exact_job(data, data["jobs"][0]["work_id"])

    def test_cycle_count_excludes_setup_and_later_direct_dispatch(self):
        rows = [{"requestId": request, "eventType": event, "elapsedRealtimeMillis": when}
                for request, event, when in [("setup", "work_started", 90),
                    ("setup", "snapshot_applied", 110), ("natural", "work_started", 150),
                    ("direct", "work_started", 201), ("direct", "snapshot_applied", 210)]]
        events, count = window_events(rows, 100, 200)
        self.assertEqual(count, 1)
        self.assertEqual({row["requestId"] for row in events}, {"setup", "natural"})

    def test_accepts_pending_reason_evidence_without_reclassifying_it(self):
        data = sample()
        self.assertEqual(probe.validate(data), data)

    def test_empty_jobs_is_valid_after_cleanup_not_a_fake_executed_job(self):
        data = sample()
        data["jobs"] = []
        self.assertEqual(probe.validate(data)["jobs"], [])

    def test_rejects_other_app_namespace_and_mutating_profile(self):
        for key, value in [("package", "other.app"), ("namespace", "other"), ("read_only", False)]:
            with self.subTest(key=key):
                data = sample()
                data[key] = value
                with self.assertRaisesRegex(RuntimeError, "SCOPE_MISMATCH"):
                    probe.validate(data)

    def test_rejects_opaque_extra_fields_at_every_level(self):
        for section in [lambda d: d, lambda d: d["jobs"][0],
                        lambda d: d["jobs"][0]["pending_reasons"][0],
                        lambda d: d["jobs"][0]["history"][0],
                        lambda d: d["jobs"][0]["stats"][0]]:
            data = deepcopy(sample())
            section(data)["private_value"] = "opaque"
            with self.assertRaises(RuntimeError):
                probe.validate(data)

    def test_rejects_invalid_work_identity_and_sensitive_reason_text(self):
        for key, value in [("work_id", "not-a-work-id"), ("service", "other.Service")]:
            data = sample()
            data["jobs"][0][key] = value
            with self.assertRaises(RuntimeError):
                probe.validate(data)
        data = sample()
        data["jobs"][0]["pending_reasons"][0]["name"] = "opaque platform exception"
        with self.assertRaisesRegex(RuntimeError, "REASON_INVALID"):
            probe.validate(data)

    def test_rejects_unsupported_sdk_and_invalid_measurement_types(self):
        for change in [lambda d: d.update(sdk_int=35), lambda d: d.update(utc_epoch_ms="private"),
                       lambda d: d["jobs"][0]["stats"][0].update(duration_ms=-1),
                       lambda d: d["jobs"][0]["history"][0].update(timestamp_ms=False)]:
            data = sample()
            change(data)
            with self.assertRaises(RuntimeError):
                probe.validate(data)

    def test_adb_timeout_and_failure_hide_private_identifier(self):
        private = "device-identifier-private"
        outcomes = [subprocess.TimeoutExpired(["adb", "-s", private], 30),
                    OSError(private), subprocess.CompletedProcess([], 1, b"", private.encode())]
        for outcome in outcomes:
            with self.subTest(outcome=type(outcome).__name__):
                options = {"side_effect": outcome} if isinstance(outcome, BaseException) else {"return_value": outcome}
                with patch.object(probe.subprocess, "run", **options):
                    with self.assertRaisesRegex(RuntimeError, "^JOB_PROBE_ADB_FAILED$") as raised:
                        probe.adb_call("adb", private, "shell", "query")
                self.assertNotIn(private, str(raised.exception))


if __name__ == "__main__":
    unittest.main()
