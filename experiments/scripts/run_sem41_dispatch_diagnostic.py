#!/usr/bin/env python3
"""One development-only dispatch diagnostic; never counts as a natural E01 pilot.

Observe 20 minutes past a single registration, query pending reasons without
instrumentation, then optionally dispatch the exact pending job with --satisfied.
No app/server/APK changes, quota tuning, rescheduling, or constraint bypass.
"""

import argparse
import json
from pathlib import Path
import signal
import subprocess
import time
import uuid

import probe_sem41_jobs as probe
from run_sem41_periodic_pilots import PACKAGE, ROOT, PilotBatch, utc, write_json

OBSERVATION_SECONDS = 1200


def exact_job(sample, work_id):
    matches = [job for job in sample["jobs"] if job["work_id"] == work_id]
    if len(matches) != 1:
        raise RuntimeError("EXACT_PENDING_WORK_REQUIRED")
    if matches[0].get("job_disappeared_during_query"):
        raise RuntimeError("PENDING_JOB_QUERY_RACE")
    return matches[0]


def window_events(rows, start, end):
    setup = {row["requestId"] for row in rows
             if row["eventType"] == "work_started" and row["elapsedRealtimeMillis"] < start}
    within = [row for row in rows if start <= row["elapsedRealtimeMillis"] <= end]
    cycles = {row["requestId"] for row in within if row["eventType"] == "work_started"} - setup
    return within, len(cycles)


class DispatchDiagnostic(PilotBatch):
    RUN_PHASE = "development"

    def __init__(self, args):
        super().__init__(args)
        sources = [Path(__file__).resolve(), Path(probe.__file__).resolve(), probe.SOURCE.resolve(),
                   ROOT / "experiments/scripts/run_sem41_periodic_pilots.py",
                   ROOT / "experiments/scripts/sem41_baseline.py"]
        relative = [str(path.relative_to(ROOT)) for path in sources]
        if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", *relative], cwd=ROOT).returncode:
            raise RuntimeError("DIAGNOSTIC_SOURCE_NOT_COMMITTED")
        for name in relative:
            if subprocess.run(["git", "ls-files", "--error-unmatch", name], cwd=ROOT,
                              capture_output=True).returncode:
                raise RuntimeError("DIAGNOSTIC_SOURCE_NOT_TRACKED")
        write_json(self.folder / "runner-identity.json", {
            "observer_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
            "sources_sha256": {name: probe.sha(path) for name, path in zip(relative, sources)},
            "probe_dex_sha256": probe.sha(args.dex), "phase": "development",
            "candidate_gate_passed": False, "direct_dispatch_permitted": args.permit_direct_dispatch,
            "not_a_natural_e01_sample": True,
        })

    def sample(self, label):
        def pid():
            result = subprocess.run([str(self.args.adb), "-s", self.serial, "shell", "pidof", PACKAGE],
                                    capture_output=True, timeout=15)
            return result.stdout.decode().strip()
        before = pid()
        result = probe.capture(self.args.adb, self.serial, self.args.dex)
        after = pid()
        result["target_process_unchanged_across_query"] = before == after
        result["target_process_present_before_query"] = bool(before)
        write_json(self.current / (label + "-scheduler.json"), result)
        return result

    def run_one(self, _case, _repetition):
        run = "run-sem41-dispatch-diagnostic-" + uuid.uuid4().hex[:12]
        self.current = self.folder / run
        self.current.mkdir()
        self.record = {
            "run_id": run, "case_id": "CONTROL", "repetition": 1, "run_phase": "development",
            "intervention": "INJECTED", "execution_status": "RUNNING", "outcome": "UNKNOWN",
            "candidate_gate_passed": False, "mode": "PERIODIC", "reason_codes": ["DISPATCH_DIAGNOSTIC_ONLY"],
            "app_source_commit": self.identity["app_source_commit"],
            "server_source_commit": self.identity["server_source_commit"],
            "apk_sha256": self.identity["apk_artifacts"]["application_apk"]["sha256"],
        }
        self.persist("SETUP")
        try:
            self.configure("PERIODIC", run)
            self.record.update(start_utc=utc(), start_elapsed_realtime_ms=self.elapsed())
            self.update("PERIODIC")
            self.persist("OBSERVE_DISPATCH")
            deadline = time.monotonic() + OBSERVATION_SECONDS
            next_sample = time.monotonic()
            count = 0
            while time.monotonic() < deadline:
                if time.monotonic() >= next_sample:
                    self.sample("query-" + str(count))
                    if count % 5 == 0:
                        state = self.checkpoint("observe-" + str(count))
                        if state["app_resumed"] or state["package_stopped"] or not state["network_connected"] or state["idle"] != "ACTIVE":
                            raise RuntimeError("DIAGNOSTIC_BASELINE_CHANGED")
                    count += 1
                    next_sample += 60
                write_json(self.folder / "heartbeat.json", {"utc": utc(), "run_id": run,
                           "stage": "OBSERVE_DISPATCH", "remaining_seconds": max(0, round(deadline - time.monotonic()))})
                time.sleep(min(10, max(0, deadline - time.monotonic())))
            self.record.update(undispatched_end_utc=utc(), undispatched_end_elapsed_realtime_ms=self.elapsed())
            state = self.checkpoint("before-direct-dispatch")
            if state["app_resumed"] or state["package_stopped"] or not state["network_connected"] or state["idle"] != "ACTIVE":
                raise RuntimeError("DIAGNOSTIC_BASELINE_CHANGED")
            metadata, rows = self.database("before-direct-dispatch-db")
            within, cycles = window_events(rows, self.record["start_elapsed_realtime_ms"],
                                           self.record["undispatched_end_elapsed_realtime_ms"])
            applied = any(row["eventType"] == "snapshot_applied" and row["version"] == self.record["target_version"] for row in within)
            self.record.update(undispatched_cycles=cycles, undispatched_target_applied=applied,
                               cached_version_before_direct_dispatch=int(metadata["cachedVersion"]),
                               direct_dispatch_attempted=False)
            before = self.sample("before-direct-dispatch")
            if self.args.permit_direct_dispatch and not applied:
                job = exact_job(before, self.record["work_id"])
                self.persist("DIRECT_DISPATCH")
                self.record.update(direct_dispatch_attempted=True, direct_dispatch_job_id=job["job_id"],
                                   direct_dispatch_start_utc=utc(), direct_dispatch_start_elapsed_realtime_ms=self.elapsed())
                command = [str(self.args.adb), "-s", self.serial, "shell", "cmd", "jobscheduler", "run",
                           "--satisfied", "--namespace", probe.NAMESPACE, PACKAGE, str(job["job_id"])]
                result = subprocess.run(command, capture_output=True, timeout=30)
                (self.current / "direct-dispatch-output.private.txt").write_bytes(result.stdout + result.stderr)
                self.record["direct_dispatch_exit_code"] = result.returncode
                # One direct request only. Keep any rejection/failure; never retry with --force.
                time.sleep(10)
            self.record.update(end_utc=utc(), end_elapsed_realtime_ms=self.elapsed())
            self.checkpoint("window-end")
            metadata, rows = self.database("window-end-db")
            within, _ = window_events(rows, self.record["start_elapsed_realtime_ms"], self.record["end_elapsed_realtime_ms"])
            any_apply = any(row["eventType"] == "snapshot_applied" and row["version"] == self.record["target_version"] for row in within)
            self.record.update(execution_status="COMPLETED", outcome="SUCCESS" if any_apply else "TIMEOUT",
                               cached_version_after=int(metadata["cachedVersion"]))
            self.sample("window-end")
        except Exception as failure:
            self.record.update(execution_status="ABORTED", outcome="FAILURE", end_utc=utc(),
                               end_elapsed_realtime_ms=self.elapsed())
            self.record["reason_codes"].append(str(failure) if isinstance(failure, RuntimeError) else type(failure).__name__.upper())
            raise
        finally:
            self.persist("CLEANUP")
            self.instrument("cancel")
            self.instrument("export-v2")
            self.shell("am", "start", "-W", "-n", PACKAGE + "/.MainActivity")
            self.shell("input", "keyevent", "KEYCODE_HOME")
            self.checkpoint("cleanup")
            self.sample("cleanup")
            self.record["cleanup_passed"] = True
            self.persist("FINISHED")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adb", type=Path, required=True)
    parser.add_argument("--device-map", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, default=ROOT / "docs/evidence/SEM-41/PREFLIGHT.json")
    parser.add_argument("--private-output", type=Path, required=True)
    parser.add_argument("--store-dir", type=Path, required=True)
    parser.add_argument("--dex", type=Path, required=True)
    parser.add_argument("--permit-direct-dispatch", action="store_true")
    args = parser.parse_args()
    args.runs = ["CONTROL:1"]
    def interrupted(_signum, _frame):
        raise RuntimeError("DIAGNOSTIC_INTERRUPTED")
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    DispatchDiagnostic(args).run()


if __name__ == "__main__":
    main()
