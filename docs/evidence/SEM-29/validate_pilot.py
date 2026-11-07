#!/usr/bin/env python3
"""Audit the observed legacy SEM-29 pilot without converting it to schema v2."""

import argparse
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path


def audit(directory):
    manifest = json.loads((directory / "manifest.json").read_text())
    raw = (directory / "events.jsonl").read_bytes()
    events = [json.loads(line) for line in raw.decode("utf-8").splitlines()]
    report = json.loads((directory / "export_report.json").read_text())
    assert manifest["data_kind"] == "OBSERVED"
    assert manifest["run_phase"] == "pilot"
    assert manifest["event_schema_version"] == "legacy-room-v1"
    assert hashlib.sha256(raw).hexdigest() == report["android_raw_sha256"]
    assert len({event["eventId"] for event in events}) == len(events)
    assert all(event["runId"] == manifest["run_id"] for event in events)
    assert all(event["source"] == "PERIODIC" for event in events)
    assert all(event["messageId"] is None for event in events)
    expected_columns = {
        "eventId", "source", "eventType", "occurredAtEpochMillis", "occurredAtUtc",
        "runId", "version", "outcome", "reason", "requestId", "workId", "messageId",
        "elapsedRealtimeMillis",
    }
    assert all(set(event) == expected_columns for event in events)
    assert all(isinstance(event["elapsedRealtimeMillis"], int) for event in events)
    assert all(
        abs(datetime.fromisoformat(event["occurredAtUtc"].replace("Z", "+00:00")).timestamp() * 1000
            - event["occurredAtEpochMillis"]) < 2
        for event in events
    )

    obs = manifest["observation"]
    start = obs["start_elapsed_realtime_ms"]
    end = obs["end_elapsed_realtime_ms"]
    assert end >= start
    starts = [event for event in events if event["eventType"] == "work_started"]
    setup_ids = {event["requestId"] for event in starts if event["elapsedRealtimeMillis"] < start}
    window = [event for event in events if start <= event["elapsedRealtimeMillis"] <= end]
    window_starts = [event for event in window if event["eventType"] == "work_started"]
    new_ids = sorted({event["requestId"] for event in window_starts} - setup_ids)
    assert all(new_ids)
    assert obs["natural_periodic_cycles"] == len(new_ids)
    assert obs["actual_duration_ms"] == end - start
    registered = [event for event in events if event["eventType"] == "periodic_registered"]
    assert len(registered) == 1
    work_id = registered[0]["workId"]
    assert all(event["workId"] == work_id for event in events)
    target = obs["target_version"]
    applied = [event for event in window if event["eventType"] == "snapshot_applied" and event["version"] == target]
    cleanup = json.loads((directory / "state-cleanup.json").read_text())
    assert all(work["state"] in {"CANCELLED", "SUCCEEDED", "FAILED"} for work in cleanup["periodic_work"])
    assert manifest["cleanup"]["work_drained"] is True
    assert manifest["cleanup"]["status"] == "PASS"
    after = json.loads((directory / "state-after.json").read_text())
    after_version = int(after["cached_version"]) if after["cached_version"] is not None else None
    assert after_version == obs["cached_version_after"]

    server_raw = (directory / "server-events.jsonl").read_bytes()
    assert hashlib.sha256(server_raw).hexdigest() == report["server_export_sha256"]
    server_events = [json.loads(line) for line in server_raw.decode("utf-8").splitlines()]
    assert len(server_events) == 1
    server = server_events[0]
    assert server["schema_version"] == "2.0.0" and server["event_type"] == "server_updated"
    assert server["run_id"] == manifest["run_id"] and server["device_alias"] == manifest["device_alias"]
    assert server["mode"] == "PERIODIC" and server["data_version"] == target

    passed = len(new_ids) >= 2 and bool(applied) and end - start >= 5_400_000
    if manifest["outcome"] == "SUCCESS":
        assert manifest["execution_status"] == "COMPLETED" and passed
    return {
        "run_id": manifest["run_id"],
        "event_format": "legacy-room-v1",
        "window_duration_ms": end - start,
        "total_android_events": len(events),
        "setup_events": sum(event["elapsedRealtimeMillis"] < start for event in events),
        "post_window_events": sum(event["elapsedRealtimeMillis"] > end for event in events),
        "window_event_counts": dict(sorted(Counter(event["eventType"] for event in window).items())),
        "window_work_started_events": len(window_starts),
        "setup_request_ids": sorted(setup_ids),
        "new_periodic_cycle_request_ids": new_ids,
        "new_periodic_cycles": len(new_ids),
        "initial_recovery_requests_in_window": sorted({event["requestId"] for event in window_starts} & setup_ids),
        "work_id": work_id,
        "target_version": target,
        "target_applied_in_window": bool(applied),
        "first_target_applied_android_utc": applied[0]["occurredAtUtc"] if applied else None,
        "pilot_emulator_observation_passed": passed,
        "canonical_v2_handoff_ready": False,
        "clock_controlled": manifest["clock"]["controlled"],
        "cleanup_active_periodic_work": 0,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.run_directory), ensure_ascii=False, indent=2) + "\n", end="")
