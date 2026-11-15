#!/usr/bin/env python3
"""Review finished SEM-41 pilot captures, then export outside the main dataset.

Never touches the device or changes producer events. Requires the private batch
directory and a private deny-values JSON array. Refuses running/incomplete runs.
"""

import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace

import export_logs as canonical

ROOT = Path(__file__).resolve().parents[2]
WINDOWS = {"E01": 5400, "E03": 2100, "E04": 1920, "E06": 2700}


def load(path):
    return canonical.parse_json(canonical.read_text(path))


def lines(path):
    return [canonical.parse_json(line) for line in canonical.read_text(path).splitlines()]


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def millis(value):
    return round(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def review(folder):
    record = load(folder / "observation.json")
    canonical.require(record["stage"] == "FINISHED" and record["execution_status"] in {"COMPLETED", "ABORTED"}, "RUN_NOT_FINISHED")
    canonical.require(record["run_phase"] == "pilot" and record["candidate_gate_passed"] is False, "PILOT_ONLY")
    events = lines(folder / "events-v2.jsonl")
    raw = lines(folder / "export-v2-events-legacy.jsonl")
    report = load(folder / "events-v2-export-report.json")
    omitted = report["omitted_events"]
    canonical.require(len(events) == report["exported_event_count"] and len(omitted) == report["omitted_event_count"], "PRODUCER_REPORT_COUNT_MISMATCH")
    raw_ids = [row["eventId"] for row in raw]
    exported_ids = [event["event_id"] for event in events]
    omitted_ids = [event["event_id"] for event in omitted]
    canonical.require(len(set(raw_ids)) == len(raw_ids) and set(raw_ids) == set(exported_ids) | set(omitted_ids) and not set(exported_ids) & set(omitted_ids), "RAW_EVENT_ACCOUNTING_MISMATCH")
    checks = {}
    checks["only_cleanup_omitted"] = all(event["event_type"] == "periodic_cancelled" for event in omitted)
    checkpoints = {path.stem: load(path) for path in folder.glob("*-checkpoint.json")}
    checks["background_and_end_evidence"] = {"background-checkpoint", "window-end-checkpoint"} <= set(checkpoints)
    clean = checkpoints["cleanup-checkpoint"]
    state = load(folder / "export-v2-state.json")
    checks["cleanup"] = record.get("cleanup_passed") is True and not clean["package_stopped"] and not clean["app_resumed"] and clean["network_connected"] and clean["idle"] == "ACTIVE" and not any(work["state"] not in {"CANCELLED", "SUCCEEDED", "FAILED"} for work in state["periodic_work"])
    start, end = record.get("start_elapsed_realtime_ms"), record.get("end_elapsed_realtime_ms")
    within = [event for event in events if start is not None and start <= event["elapsed_realtime_ms"] <= end]
    setup = [event for event in events if start is not None and event["elapsed_realtime_ms"] < start]
    request_setup = {event["request_id"] for event in setup if event["event_type"] == "work_started"}
    request_cycles = {event["request_id"] for event in within if event["event_type"] == "work_started" and event["source"] == "PERIODIC"} - request_setup
    applied = [event for event in within if event["event_type"] == "snapshot_applied" and event["data_version"] == record.get("target_version") and event["source"] == "PERIODIC"]
    checks["no_manual_or_push_sync"] = all(event["source"] == "PERIODIC" for event in events)
    checks["single_registration"] = sum(event["event_type"] == "periodic_registered" for event in events) == 1
    checks["single_work_identity"] = all(event["work_id"] == record.get("work_id") for event in events)
    chains = []
    for event in applied:
        request = [item for item in events if item["request_id"] == event["request_id"] and item["work_id"] == event["work_id"] and item["elapsed_realtime_ms"] <= event["elapsed_realtime_ms"]]
        started = [item for item in request if item["event_type"] == "snapshot_fetch_started"]
        completed = [item for item in request if item["event_type"] == "snapshot_fetch_completed" and item["outcome"] == "success" and item["data_version"] == event["data_version"]]
        chains.append(any(item["event_type"] == "work_started" for item in request) and any(a["network_call_id"] == b["network_call_id"] and a["elapsed_realtime_ms"] <= b["elapsed_realtime_ms"] for a in started for b in completed))
    checks["applied_fetch_provenance"] = all(chains)
    duration = end - start if start is not None else None
    checks["full_window"] = duration is not None and duration >= WINDOWS[record["case_id"]] * 1000
    for name, checkpoint in checkpoints.items():
        if name.startswith(("background-", "window-end-", "NATURAL_PERIODIC-", "BASELINE-", "CONFIRMED_DOZE-", "POST_DOZE-", "CONFIRMED_OFFLINE-", "POST_RECONNECT-", "CONTROLLED_SKIP_PERIODIC_RECOVERY-")):
            checks[name + "-background"] = not checkpoint["app_resumed"] and not checkpoint["package_stopped"]
            if not name.startswith(("CONFIRMED_DOZE-", "CONFIRMED_OFFLINE-")):
                checks[name + "-active"] = checkpoint["idle"] == "ACTIVE"
                checks[name + "-network"] = checkpoint["network_connected"]
            if name.startswith("CONFIRMED_DOZE-"):
                checks[name + "-idle"] = checkpoint["idle"] == "IDLE"
    if record["case_id"] == "E03":
        enter, leave = record.get("idle_start_elapsed_realtime_ms"), record.get("idle_exit_elapsed_realtime_ms")
        checks["doze_phases"] = all(value is not None for value in (start, enter, leave, end)) and enter - start >= 300000 and leave - enter >= 1200000 and end - leave >= 600000
    if record["case_id"] == "E04":
        offline, online = record.get("offline_elapsed_realtime_ms"), record.get("reconnect_elapsed_realtime_ms")
        checks["offline_and_reconnect_windows"] = all(value is not None for value in (offline, online, end)) and online - offline >= 120000 and end - online >= 1800000
    if record["case_id"] == "E06":
        skips = [event for event in lines(folder / "skip-events.jsonl") if event["run_id"] == record["run_id"]]
        checks["deliberate_skip"] = record.get("skip_confirmed") is True and len(skips) == 1 and skips[0]["event_type"] == "push_send_skipped" and skips[0]["reason"] == "FAULT_INJECTION_SKIP" and skips[0]["message_id"] is None and skips[0]["send_attempt_id"] is None
        checks["full_window_after_update"] = millis(record["end_utc"]) - millis(record["update_utc"]) >= 2700000
    completed = record["execution_status"] == "COMPLETED"
    checks["record_outcome"] = not completed or record["outcome"] == ("SUCCESS" if applied else "TIMEOUT")
    checks["record_cycle_count"] = not completed or record["new_periodic_cycles"] == len(request_cycles)
    phases = {}
    if record["case_id"] == "E03" and record.get("idle_exit_elapsed_realtime_ms"):
        enter, leave = record["idle_start_elapsed_realtime_ms"], record["idle_exit_elapsed_realtime_ms"]
        for name, low, high in [("baseline", start, enter), ("idle", enter, leave), ("post_idle", leave, end)]:
            phases[name] = dict(Counter(event["event_type"] for event in within if low <= event["elapsed_realtime_ms"] < high))
    return record, {"run_id": record["run_id"], "checks": checks, "validity": "VALID" if completed and all(checks.values()) else "INVALID", "actual_duration_ms": duration, "new_periodic_cycles": len(request_cycles), "applied_target_count_in_window": len(applied), "raw_rows": len(raw), "canonical_android_events": len(events), "omitted_rows": len(omitted), "phase_event_counts": phases, "clock_controlled": False, "cross_device_latency_calculated": False, "event_boot_session_ids_preserved": True}


def export_one(folder, output, deny_path):
    record, audit = review(folder)
    deny = load(deny_path)
    base = load(ROOT / "experiments/development/run-sem41-v2-smoke-20261115/manifest.json")
    canonical.require(record["app_source_commit"] == base["build"]["app_commit"] and record["server_source_commit"] == base["build"]["server_commit"] and record["apk_sha256"] == base["build"]["apk_sha256"], "SNAPSHOT_BUILD_CONFIG_MISMATCH")
    manifest = deepcopy(base)
    manifest.update(case_id=record["case_id"], subscenario="CONTROLLED_SKIP" if record["case_id"] == "E06" else "PERIODIC_BASELINE", repetition=record["repetition"], run_id=record["run_id"], run_phase="pilot", mode=record["mode"], execution_status=record["execution_status"], outcome=record["outcome"], validity=audit["validity"], reason_codes=list(record["reason_codes"]) + ["CANDIDATE_NOT_READY", "CLOCK_UNCONTROLLED", "CLEANUP_EVENT_OMITTED"], intervention="INJECTED" if record["case_id"] in {"E03", "E06"} else "NONE")
    manifest["reason_codes"] += ["AUDIT_" + key.upper().replace("-", "_")[:50] for key, passed in audit["checks"].items() if not passed]
    manifest["build"].update(app_commit=record["app_source_commit"], server_commit=record["server_source_commit"], apk_sha256=record["apk_sha256"], candidate_gate_passed=False)
    manifest["config"].update(periodic_interval_minutes=15, periodic_flex_minutes=15, periodic_initial_delay_ms=0, periodic_unique_name="periodic_bulletin_sync", periodic_policy="UPDATE", idle_method="ADB_FORCE_IDLE" if record["case_id"] == "E03" else "NATURAL", deep_idle_during="IDLE" if record.get("idle_start_utc") else "ACTIVE")
    obs = manifest["observation"]
    for key in ("start_utc", "end_utc", "start_elapsed_realtime_ms", "end_elapsed_realtime_ms", "cached_version_before", "target_version", "cached_version_after"):
        obs[key] = record.get(key)
    obs.update(planned_window_seconds=WINDOWS[record["case_id"]], actual_duration_ms=audit["actual_duration_ms"], server_version_before=record["target_version"] - 1 if record.get("target_version") else None, natural_periodic_cycles=audit["new_periodic_cycles"])
    for key in obs["milestones"]:
        obs["milestones"][key] = record.get(key)
    clean = audit["checks"]["cleanup"]
    manifest["cleanup"].update(status="PASS" if clean else "FAIL", work_drained=clean, idle_restored=clean, network_restored=clean, package_stopped_cleared=clean)
    extras = {"android-events-raw.jsonl": (folder / "export-v2-events-legacy.jsonl").read_text(), "canonical-export-report.json": (folder / "events-v2-export-report.json").read_text(), "state-after.json": (folder / "export-v2-state.json").read_text(), "observation.json": (folder / "observation.json").read_text(), "runner-identity.json": (folder.parent / "runner-identity.json").read_text()}
    if (folder / "offline-proof.json").exists():
        extras["offline-proof.json"] = (folder / "offline-proof.json").read_text()
    extras["audit.json"] = json.dumps(audit, indent=2) + "\n"
    for path in sorted(folder.glob("*-checkpoint.json")):
        extras[path.name] = path.read_text()
    manifest["evidence_files"] = sorted(extras)
    canonical.public_safe([manifest, audit] + [canonical.parse_json(text) for name, text in extras.items() if not name.endswith(".jsonl")] + [lines(folder / "export-v2-events-legacy.jsonl")], deny)
    with tempfile.TemporaryDirectory(prefix="sem41-export-") as temporary:
        scratch = Path(temporary)
        save(scratch / "manifest.json", manifest)
        sources = (folder / "server-events.jsonl").read_text() if (folder / "server-events.jsonl").exists() else ""
        if (folder / "skip-events.jsonl").exists():
            sources += (folder / "skip-events.jsonl").read_text()
        (scratch / "server.jsonl").write_text(sources)
        args = SimpleNamespace(manifest=scratch / "manifest.json", run_id=record["run_id"], device_alias="emulator-main", fixture=False, deny_values=deny_path, adb=None, android_log=folder / "events-v2.jsonl", server_log=scratch / "server.jsonl", output_base=scratch / "first")
        canonical.export(args)
        args.output_base = scratch / "second"
        canonical.export(args)
        first = scratch / "first/runs" / record["run_id"]
        second = scratch / "second/runs" / record["run_id"]
        canonical.require(all((first / name).read_bytes() == (second / name).read_bytes() for name in ("manifest.json", "events.jsonl", "export_report.json")), "REEXPORT_NOT_IDENTICAL")
        destination = output / record["run_id"]
        canonical.require(not destination.exists(), "OUTPUT_ALREADY_EXISTS")
        output.mkdir(parents=True, exist_ok=True)
        shutil.copytree(first, destination)
        for name, text in extras.items():
            (destination / name).write_text(text)
    return {"run_id": record["run_id"], "validity": audit["validity"], "outcome": record["outcome"], "new_periodic_cycles": audit["new_periodic_cycles"], "reexport_identical": True, "files_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(destination.iterdir())}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-folder", type=Path, required=True)
    parser.add_argument("--deny-values", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "experiments/pilots")
    args = parser.parse_args()
    print(json.dumps(export_one(args.run_folder, args.output, args.deny_values)))


if __name__ == "__main__":
    main()
