#!/usr/bin/env python3
"""SEM-45: offline analysis of canonical SEM-24 exports. Python 3.9+."""

import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import statistics
import subprocess
import sys

import export_logs as contract

VERSION = "0.6.0"
ROOT = Path(__file__).resolve().parents[2]


class AnalysisError(Exception):
    """Static error codes only; never print raw logs, credentials or paths."""


def require(condition, code):
    if not condition:
        raise AnalysisError(code)


def load_run(directory, dataset):
    """Read one explicit dataset; reject mixed routes, legacy and fake observed data."""
    directory = Path(directory)
    try:
        return load_run_bytes((directory / "manifest.json").read_bytes(),
                              (directory / "events.jsonl").read_bytes(), dataset)
    except OSError:
        raise AnalysisError("INPUT_UNREADABLE") from None


def load_run_bytes(manifest_bytes, event_bytes, dataset):
    """Use the same contract for local exports and immutable Git inputs."""
    require(dataset in {"fixture", "pilot", "main"}, "DATASET_INVALID")
    try:
        raw = contract.parse_json(manifest_bytes.decode("utf-8"))
        require(isinstance(raw, dict), "MANIFEST_OBJECT_REQUIRED")
        require(raw.get("protocol_version") == "1.0.0", "PROTOCOL_VERSION_UNSUPPORTED")
        require(contract.matches(contract.ID, raw.get("run_id")) and
                contract.matches(contract.ID, raw.get("device_alias")), "RUN_ID_INVALID")
        manifest = contract.validate_manifest(raw, raw["run_id"], raw["device_alias"],
                                              dataset == "fixture")
        require(manifest["run_phase"] == ("development" if dataset == "fixture" else dataset),
                "DATASET_PHASE_MISMATCH")
        contract.public_safe(manifest, [])
        events, seen, duplicates = [], {}, 0
        for line in event_bytes.decode("utf-8").splitlines():
            require(bool(line.strip()), "BLANK_JSONL_LINE")
            item = contract.parse_json(line)
            require(isinstance(item, dict), "EVENT_OBJECT_REQUIRED")
            require(set(item) == set(contract.FIELDS), "CANONICAL_FIELDS_REQUIRED")
            event = contract.validate_event(item)
            contract.public_safe(event, [])
            require(all(event[k] == manifest[k] for k in ("run_id", "device_alias", "mode")),
                    "EVENT_MANIFEST_MISMATCH")
            require(dataset == "fixture" or event["message_id"] is None or
                    not event["message_id"].startswith("<fixture"), "FIXTURE_IN_OBSERVED")
            eid = event["event_id"]
            if eid in seen:
                require(event == seen[eid], "CONFLICTING_EVENT_ID")
                duplicates += 1
            else:
                seen[eid] = event
                events.append(event)
        require(dataset == "fixture" or manifest["execution_status"] != "NOT_RUN" or not events,
                "NOT_RUN_HAS_EVENTS")
        return {"manifest": manifest, "events": events, "duplicates": duplicates,
                "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                "events_sha256": hashlib.sha256(event_bytes).hexdigest()}
    except contract.ExportError as error:
        raise AnalysisError(str(error)) from None
    except (OSError, UnicodeError):
        raise AnalysisError("INPUT_UNREADABLE") from None
    except (TypeError, KeyError, RecursionError):
        raise AnalysisError("INPUT_TYPES_INVALID") from None


def source_bytes(commit, path):
    """Read an exact repository object without checkout, network or source edits."""
    require(isinstance(path, str) and bool(path) and
            all(part not in {"", ".", ".."} for part in path.split("/")) and
            not any(c in path for c in ("\\", ":", "\x00", "\n", "\r")), "SOURCE_PATH_INVALID")
    try:
        return subprocess.run(["git", "show", f"{commit}:{path}"], cwd=ROOT,
                              check=True, capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError):
        raise AnalysisError("SOURCE_OBJECT_UNAVAILABLE") from None


def load_source_index(path, dataset):
    """Verify pinned source bytes, including the upstream review evidence."""
    try:
        index_bytes = Path(path).read_bytes()
        index = contract.parse_json(index_bytes.decode("utf-8"))
        require(isinstance(index, dict) and index.get("index_version") == "1.0.0",
                "SOURCE_INDEX_INVALID")
        require(index.get("dataset") == dataset, "DATASET_PHASE_MISMATCH")
        commit = index.get("source_commit")
        require(contract.matches(r"[0-9a-f]{40}", commit), "SOURCE_COMMIT_INVALID")
        require(isinstance(index.get("runs"), list) and bool(index["runs"]) and
                isinstance(index.get("evidence"), list), "SOURCE_INDEX_INVALID")

        def checked_bytes(path, expected):
            require(contract.matches(r"[0-9a-f]{64}", expected), "SOURCE_HASH_INVALID")
            value = source_bytes(commit, path)
            require(hashlib.sha256(value).hexdigest() == expected, "SOURCE_HASH_MISMATCH")
            return value

        for evidence in index["evidence"]:
            checked_bytes(evidence["path"], evidence["sha256"])
        runs = []
        for entry in index["runs"]:
            directory = entry["directory"]
            require(isinstance(directory, str), "SOURCE_PATH_INVALID")
            manifest = checked_bytes(directory + "/manifest.json", entry["manifest_sha256"])
            events = checked_bytes(directory + "/events.jsonl", entry["events_sha256"])
            run = load_run_bytes(manifest, events, dataset)
            if "server_store_epoch" in entry:
                epoch = entry["server_store_epoch"]
                require(epoch is None or contract.matches(contract.ID, epoch), "SOURCE_EPOCH_INVALID")
                run["source_context"] = {"server_store_epoch": epoch}
            runs.append(run)
        return runs, {"index_sha256": hashlib.sha256(index_bytes).hexdigest(), **index}
    except contract.ExportError as error:
        raise AnalysisError(str(error)) from None
    except (OSError, UnicodeError):
        raise AnalysisError("INPUT_UNREADABLE") from None
    except (TypeError, KeyError, RecursionError):
        raise AnalysisError("SOURCE_INDEX_INVALID") from None


def utc_ms(value):
    """Integer milliseconds; do not subtract independently rounded epoch floats."""
    instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    epoch = datetime.fromisoformat("1970-01-01T00:00:00+00:00")
    delta = instant - epoch
    return delta.days * 86400000 + delta.seconds * 1000 + delta.microseconds / 1000


def monotonic_delta(start, end):
    if (start is None or end is None or start["origin"] != "ANDROID" or
            end["origin"] != "ANDROID" or not start["boot_session_id"] or
            start["boot_session_id"] != end["boot_session_id"] or
            start["device_alias"] != end["device_alias"]):
        return None
    value = end["elapsed_realtime_ms"] - start["elapsed_realtime_ms"]
    return value if value >= 0 else None


def clock_estimate(clock):
    """Return server-minus-Android offset and a conservative drift/error bound."""
    if not clock["controlled"] or clock["client_clock"] != "ANDROID":
        return None
    for phase in ("before", "after"):
        offset, uncertainty = clock[f"offset_{phase}_ms"], clock[f"uncertainty_{phase}_ms"]
        for sample in clock[f"{phase}_samples"]:
            sent, received = utc_ms(sample["client_send_utc"]), utc_ms(sample["client_receive_utc"])
            error = (received - sent) / 2 + sample["resolution_ms"]
            estimate = utc_ms(sample["server_utc"]) - (sent + received) / 2
            if uncertainty < error + abs(offset - estimate):
                return None
    if max(utc_ms(s["client_receive_utc"]) for s in clock["before_samples"]) > min(
            utc_ms(s["client_send_utc"]) for s in clock["after_samples"]):
        return None
    before, after = clock["offset_before_ms"], clock["offset_after_ms"]
    return ((before + after) / 2,
            max(clock["uncertainty_before_ms"], clock["uncertainty_after_ms"]) + abs(after - before) / 2)


def cross_clock_delta(server, android, clock):
    estimate = clock_estimate(clock)
    if server is None or android is None or estimate is None:
        return None
    offset, uncertainty = estimate
    value = utc_ms(android["timestamp_utc"]) + offset - utc_ms(server["timestamp_utc"])
    if value - uncertainty < 0:
        return None
    return {"estimate_ms": round(value, 3), "uncertainty_ms": round(uncertainty, 3)}


def server_time_on_android(event, estimate):
    """Return earliest/latest possible Android UTC for a server timestamp."""
    offset, uncertainty = estimate
    android_utc = utc_ms(event["timestamp_utc"]) - offset
    return android_utc - uncertainty, android_utc + uncertainty


def only(events):
    """An ambiguous join remains unknown instead of picking an arbitrary row."""
    return events[0] if len(events) == 1 else None


def group_identity(manifest, source_context=None):
    identity = {k: manifest[k] for k in ("data_kind", "run_phase", "case_id", "subscenario",
                "device_alias", "mode", "protocol_version", "event_schema_version", "intervention",
                "build", "device", "config")}
    if source_context is not None:
        identity["source_context"] = source_context
    return hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=True,
                                    separators=(",", ":")).encode()).hexdigest()


def e02_receipt_for_apply(applied, request, target_signals, receipts, location):
    """Find the target send's callback and the work attempt that applied it."""
    enqueued = only([e for e in request if e["event_type"] == "work_enqueued"])
    started = only([e for e in request if e["event_type"] == "work_started" and
                    e["work_attempt"] == applied["work_attempt"]])
    if (enqueued is None or started is None or
            location(enqueued) not in {"window", "late"} or
            location(started) not in {"window", "late"} or monotonic_delta(started, applied) is None):
        return None
    signals = target_signals.intersection(enqueued["signal_ids"], started["signal_ids"], applied["signal_ids"])
    # The app logs enqueue acknowledgement after submitting work. A worker can start first.
    return only([e for e in receipts if e["signal_ids"][0] in signals and
                 location(e) in {"window", "late"} and monotonic_delta(e, enqueued) is not None and
                 monotonic_delta(e, started) is not None])


def e03_doze_phase_flag(observation):
    """Check elapsed durations on the observation clock, independent of server UTC."""
    idle_start, idle_exit = (observation["milestones"][key] for key in ("idle_start_utc", "idle_exit_utc"))
    bounds = (observation["start_utc"], idle_start, idle_exit, observation["end_utc"])
    start_elapsed, end_elapsed = (observation[key] for key in
                                  ("start_elapsed_realtime_ms", "end_elapsed_realtime_ms"))
    if not all(bounds) or not contract.uint(start_elapsed) or not contract.uint(end_elapsed):
        return "E03_DOZE_PHASES_UNVERIFIED"
    start, enter, leave, end = map(utc_ms, bounds)
    if not start <= enter <= leave <= end:
        return "E03_DOZE_PHASE_ORDER_INVALID"
    if abs((end - start) - (end_elapsed - start_elapsed)) > 1000:
        return "E03_DOZE_PHASES_UNVERIFIED"
    if enter - start < 300000 or leave - enter < 1200000 or end - leave < 600000:
        return "E03_DOZE_PHASE_TOO_SHORT"
    return None


def e04_reconnect_elapsed(manifest, android, estimate):
    """Map declared Android UTC milestones only after checking same-boot anchors."""
    obs = manifest["observation"]
    offline, reconnect = (obs["milestones"][k] for k in ("offline_utc", "reconnect_utc"))
    if estimate is None or not all((obs["start_utc"], obs["end_utc"], offline, reconnect,
                                    obs["boot_session_id"])):
        return None, "E04_RECOVERY_CLOCK_UNVERIFIED"
    start, end = obs["start_elapsed_realtime_ms"], obs["end_elapsed_realtime_ms"]
    anchors = [utc_ms(e["timestamp_utc"]) - e["elapsed_realtime_ms"] for e in android
               if e["boot_session_id"] == obs["boot_session_id"]]
    if not anchors or not contract.uint(start) or not contract.uint(end):
        return None, "E04_RECOVERY_CLOCK_UNVERIFIED"
    utc_start, utc_end = utc_ms(obs["start_utc"]), utc_ms(obs["end_utc"])
    before = max(utc_ms(s["client_receive_utc"]) for s in manifest["clock"]["before_samples"])
    after = min(utc_ms(s["client_send_utc"]) for s in manifest["clock"]["after_samples"])
    tolerance = 2 * estimate[1]
    if (before > utc_start or after < utc_end or
            any(abs(anchor - boundary) > tolerance for anchor in anchors
                for boundary in (utc_start - start, utc_end - end))):
        return None, "E04_RECOVERY_CLOCK_UNVERIFIED"
    offline_ms, reconnect_ms = utc_ms(offline), utc_ms(reconnect)
    if not utc_start <= offline_ms <= reconnect_ms <= utc_end or reconnect_ms - offline_ms < 120000:
        return None, "E04_OFFLINE_INTERVAL_INVALID"
    recovery_ms = 1800000 if manifest["mode"] == "PERIODIC" else 300000
    if utc_end - reconnect_ms < recovery_ms:
        return None, "E04_RECOVERY_WINDOW_SHORT"
    return start + reconnect_ms - utc_start, None


def e04_target_update_flag(milestones, updated, estimate):
    """Check the target commit against the verified Android UTC offline interval."""
    if updated is None:
        return "E04_TARGET_UPDATE_TIME_UNVERIFIED"
    earliest, latest = server_time_on_android(updated, estimate)
    offline, reconnect = (utc_ms(milestones[k]) for k in ("offline_utc", "reconnect_utc"))
    if latest < offline or earliest >= reconnect:
        return "E04_TARGET_UPDATE_OUTSIDE_OFFLINE"
    if earliest < offline or latest >= reconnect:
        return "E04_TARGET_UPDATE_TIME_UNVERIFIED"
    return None


def e06_fetch_verified(applied, requests, fetches):
    """Require a successful target fetch in the applying periodic work attempt."""
    key = tuple(applied[k] for k in ("request_id", "work_id", "work_attempt"))
    started = only([e for e in requests[applied["request_id"]] if e["event_type"] == "work_started"
                    and e["work_attempt"] == applied["work_attempt"]])
    for group in fetches.values():
        began = only([e for e in group if e["event_type"] == "snapshot_fetch_started"])
        finished = only([e for e in group if e["event_type"] == "snapshot_fetch_completed"])
        if began is None or finished is None:
            continue
        if (tuple(finished[k] for k in ("request_id", "work_id", "work_attempt")) == key and
                all(e["source"] == "PERIODIC" for e in (began, finished, applied)) and
                finished["outcome"] == "success" and finished["http_status"] == 200 and
                finished["data_version"] == applied["data_version"] and
                monotonic_delta(started, began) is not None and
                monotonic_delta(began, finished) is not None and
                monotonic_delta(finished, applied) is not None):
            return True
    return False


def analyze_run(run):
    """One run remains one sample. Counts are evidence, never invented DB writes."""
    m, events = run["manifest"], run["events"]
    obs, flags = m["observation"], set()
    start, end, boot = (obs[k] for k in ("start_elapsed_realtime_ms", "end_elapsed_realtime_ms", "boot_session_id"))
    has_window = (contract.uint(start) and contract.uint(end) and end >= start and bool(boot))
    if not has_window:
        flags.add("MONOTONIC_WINDOW_UNAVAILABLE")
    else:
        minimum = {"E01": 5400, "E02": 120, "E03": 2100, "E05": 900, "E06": 2700}
        required = minimum.get(m["case_id"], 0)
        if m["case_id"] == "E04":
            required = 1920 if m["mode"] == "PERIODIC" else 420
        planned, actual = obs["planned_window_seconds"], obs["actual_duration_ms"]
        if (planned is None or actual is None or planned < required or end - start < planned * 1000 or
                actual < planned * 1000):
            flags.add("WINDOW_SHORT_OR_UNDECLARED")
        if actual is not None and abs(actual - (end - start)) > 1000:
            flags.add("WINDOW_DURATION_CONFLICT")

    def location(e):
        if e["origin"] != "ANDROID":
            return "server"
        if not has_window or e["boot_session_id"] != boot:
            return "unknown"
        return ("setup" if e["elapsed_realtime_ms"] < start else
                "late" if e["elapsed_realtime_ms"] > end else "window")

    buckets = defaultdict(list)
    for event in events:
        buckets[location(event)].append(event)
    if buckets["unknown"]:
        flags.add("ANDROID_WINDOW_OR_BOOT_UNKNOWN")
    window_verified = has_window and not buckets["unknown"]
    inside = buckets["window"]
    if any(e["source"] == "MANUAL" for e in inside):
        flags.add("MANUAL_IN_WINDOW")
    expected_source = {"E01": "PERIODIC", "E02": "PUSH", "E05": "PUSH", "E06": "PERIODIC"}.get(m["case_id"])
    expected_mode = {"E01": "PERIODIC", "E02": "PUSH", "E05": "PUSH", "E06": "HYBRID"}.get(m["case_id"])
    if expected_mode and m["mode"] != expected_mode:
        flags.add("CASE_MODE_MISMATCH")
    if m["case_id"] in {"E03", "E04"} and m["mode"] not in {"PERIODIC", "PUSH"}:
        flags.add("CASE_MODE_MISMATCH")
    if m["case_id"] == "E03" and m["execution_status"] != "NOT_RUN":
        config = m["config"]
        if config["deep_idle_during"] != "IDLE":
            flags.add("E03_DEEP_DOZE_NOT_CONFIRMED")
        if any(config[key] in {"IDLE", "IDLE_MAINTENANCE"} for key in ("deep_idle_before", "deep_idle_after")):
            flags.add("E03_DOZE_STATE_CONFLICT")
        phase_flag = e03_doze_phase_flag(obs)
        if phase_flag:
            flags.add(phase_flag)
    if expected_source and any(e["source"] not in {expected_source, None} and
                               e["event_type"] != "trigger_rejected" for e in inside):
        flags.add("UNEXPECTED_BACKGROUND_SOURCE")
    reopen = obs["milestones"]["user_reopen_utc"]
    if (reopen and obs["start_utc"] and obs["end_utc"] and
            utc_ms(obs["start_utc"]) <= utc_ms(reopen) <= utc_ms(obs["end_utc"])):
        flags.add("USER_REOPEN_IN_WINDOW")

    # A request is one logical cycle with stable work/source; work_id alone is not a cycle.
    requests, fetches = defaultdict(list), defaultdict(list)
    for event in events:
        if event["request_id"] and event["origin"] == "ANDROID":
            requests[event["request_id"]].append(event)
        if event["network_call_id"]:
            fetches[event["network_call_id"]].append(event)
    for group in requests.values():
        require(len({(e["work_id"], e["source"]) for e in group}) == 1, "REQUEST_CORRELATION_CONFLICT")
    fetch_details = []
    for network_id, group in sorted(fetches.items()):
        require(len({(e["request_id"], e["work_id"], e["work_attempt"]) for e in group}) == 1,
                "FETCH_CORRELATION_CONFLICT")
        began = [e for e in group if e["event_type"] == "snapshot_fetch_started"]
        finished = [e for e in group if e["event_type"] == "snapshot_fetch_completed"]
        require(len(began) <= 1 and len(finished) <= 1, "NETWORK_CALL_ID_REUSED")
        duration = monotonic_delta(only(began), only(finished))
        fetch_details.append({"network_call_id": network_id, "request_id": group[0]["request_id"],
                              "location": location(group[0]), "duration_ms": duration,
                              "outcome": finished[0]["outcome"] if finished else None})

    clock, clock_reason = m["clock"], None
    estimate = clock_estimate(clock)
    android = [e for e in events if e["origin"] == "ANDROID"]
    if estimate and android:
        before_end = max(utc_ms(s["client_receive_utc"]) for s in clock["before_samples"])
        after_start = min(utc_ms(s["client_send_utc"]) for s in clock["after_samples"])
        if before_end > min(utc_ms(e["timestamp_utc"]) for e in android) or after_start < max(
                utc_ms(e["timestamp_utc"]) for e in android):
            clock_reason = "CLOCK_SAMPLES_DO_NOT_BRACKET_EVENTS"
        anchors = {}
        for e in android:
            if e["boot_session_id"]:
                value = utc_ms(e["timestamp_utc"]) - e["elapsed_realtime_ms"]
                anchor = anchors.setdefault(e["boot_session_id"], value)
                if abs(value - anchor) > 2 * estimate[1]:
                    clock_reason = "ANDROID_UTC_DISCONTINUITY"
        if clock_reason:
            estimate = None
    if estimate is None:
        clock_reason = clock_reason or "CLOCK_NOT_USABLE"
        clock = {"controlled": False}

    target = obs["target_version"]
    updated = only([e for e in events if e["event_type"] == "server_updated" and e["data_version"] == target])
    def target_apply(e):
        return (e["event_type"] == "snapshot_applied" and e["data_version"] == target and
                target is not None and e["source"] != "MANUAL" and
                (expected_source is None or e["source"] == expected_source))

    recovery_verified = True
    reconnect_elapsed = None
    e04_update_verified = True
    if m["case_id"] == "E04":
        reconnect_elapsed, recovery_flag = e04_reconnect_elapsed(m, android, estimate)
        recovery_verified = recovery_flag is None
        if recovery_flag:
            flags.add(recovery_flag)
        else:
            update_flag = e04_target_update_flag(obs["milestones"], updated, estimate)
            if update_flag:
                flags.add(update_flag)
                recovery_verified = False
                e04_update_verified = False

    applied = sorted([e for e in inside if target_apply(e)],
                     key=lambda e: (e["elapsed_realtime_ms"], e["event_id"]))
    late = [e for e in buckets["late"] if target_apply(e)]
    if m["case_id"] == "E04":
        tolerance = 2 * estimate[1] if estimate else 0
        if reconnect_elapsed is not None:
            if any(e["elapsed_realtime_ms"] < reconnect_elapsed - tolerance for e in applied):
                flags.add("E04_APPLIED_BEFORE_RECONNECT")
            if any(abs(e["elapsed_realtime_ms"] - reconnect_elapsed) <= tolerance for e in applied):
                flags.add("E04_APPLY_TIME_UNVERIFIED")
                recovery_verified = False
        applied = [e for e in applied if reconnect_elapsed is not None and e04_update_verified and
                   e["elapsed_realtime_ms"] > reconnect_elapsed + tolerance]
        late = [e for e in late if reconnect_elapsed is not None and e04_update_verified and
                e["elapsed_realtime_ms"] > reconnect_elapsed + tolerance]
    e02_receipts = {}
    e02_chain_unverified = False
    if m["case_id"] == "E02":
        # The loader already enforces the common run_id and device_alias for all events.
        target_signals = {e["signal_ids"][0] for e in buckets["server"] if updated is not None and
                          e["event_type"] in {"push_send_accepted", "push_send_unknown"} and
                          e["update_id"] == updated["update_id"] and e["data_version"] == target and
                          utc_ms(e["timestamp_utc"]) >= utc_ms(updated["timestamp_utc"])}
        callbacks = [e for e in android if e["event_type"] == "push_received"]
        e02_receipts = {e["event_id"]: e02_receipt_for_apply(e, requests[e["request_id"]], target_signals,
                                                          callbacks, location) for e in applied + late}
        if updated is not None and estimate is not None:
            earliest_update, _ = server_time_on_android(updated, estimate)
            for apply_event in applied + late:
                event_id = apply_event["event_id"]
                callback = e02_receipts[event_id]
                # Provider response logging can follow the callback. The target commit cannot.
                if callback is not None and earliest_update > min(utc_ms(callback["timestamp_utc"]),
                                                                 utc_ms(apply_event["timestamp_utc"])):
                    e02_receipts[event_id] = None
                    if location(apply_event) == "window":
                        flags.add("E02_PUSH_CLOCK_ORDER_CONFLICT")
        e02_chain_unverified = any(e02_receipts[e["event_id"]] is None for e in applied)
        applied = [e for e in applied if e02_receipts[e["event_id"]] is not None]
        late = [e for e in late if e02_receipts[e["event_id"]] is not None]
        if e02_chain_unverified or (m["execution_status"] == "COMPLETED" and m["outcome"] == "SUCCESS"
                                    and not applied):
            flags.add("E02_PUSH_CHAIN_UNVERIFIED")
            recovery_verified = False
            e02_chain_unverified = True
    if m["case_id"] == "E06":
        verified_ids = {e["event_id"] for e in applied + late if e06_fetch_verified(e, requests, fetches)}
        if len(verified_ids) != len(applied) + len(late):
            flags.add("E06_FETCH_CHAIN_UNVERIFIED")
            recovery_verified = False
        applied = [e for e in applied if e["event_id"] in verified_ids]
        late = [e for e in late if e["event_id"] in verified_ids]
    completion = applied[0] if applied else None
    if target is None:
        flags.add("TARGET_UNDECLARED")
    queue_ms = sync_ms = receipt_enqueue_ms = None
    if completion:
        request = requests[completion["request_id"]]
        began = only([e for e in request if e["event_type"] == "work_started" and
                      e["work_attempt"] == completion["work_attempt"]])
        if began is None or location(began) != "window":
            flags.add("TARGET_START_NOT_IN_WINDOW")
        sync_ms = monotonic_delta(began, completion)
        if sync_ms is None:
            flags.add("TARGET_START_UNVERIFIED")
        enqueued = only([e for e in request if e["event_type"] == "work_enqueued"])
        first = only([e for e in request if e["event_type"] == "work_started" and e["work_attempt"] == 0])
        queue_ms = monotonic_delta(enqueued, first)
        if m["case_id"] == "E02":
            receipt_enqueue_ms = monotonic_delta(e02_receipts[completion["event_id"]], enqueued)
        elif enqueued:
            receipts = [e for e in events if e["event_type"] == "push_received" and
                        set(e["signal_ids"]) & set(enqueued["signal_ids"]) and
                        monotonic_delta(e, enqueued) is not None]
            receipt_enqueue_ms = monotonic_delta(only(receipts), enqueued)
    if m["execution_status"] == "COMPLETED" and ((m["outcome"] == "SUCCESS") != bool(applied)):
        flags.add("OUTCOME_EVIDENCE_UNVERIFIED" if not applied and
                  (not window_verified or not recovery_verified) else
                  "OUTCOME_EVIDENCE_CONFLICT")

    if m["case_id"] == "E06":
        target_events = {e["event_type"] for e in buckets["server"] if updated is not None and
                         e["update_id"] == updated["update_id"] and e["data_version"] == target}
        if "push_send_skipped" not in target_events:
            flags.add("FAULT_SKIP_EVIDENCE_MISSING")
        if target_events & {"push_send_accepted", "push_send_rejected", "push_send_unknown"}:
            flags.add("E06_FAULT_SKIP_CONFLICTING_SEND")
    end_to_end = cross_clock_delta(updated, completion, clock)
    receipts = []
    if updated:
        signals = {s for e in events if e["origin"] == "SERVER" and e["source"] == "PUSH" and
                   e["data_version"] == target and e["update_id"] == updated["update_id"] for s in e["signal_ids"]}
        receipts = [e for e in inside if e["event_type"] == "push_received" and
                    set(e["signal_ids"]) & signals]
    receipt = e02_receipts[completion["event_id"]] if m["case_id"] == "E02" and completion else only(receipts)
    receive_delta = (cross_clock_delta(updated, receipt, clock) if e04_update_verified and
                     not e02_chain_unverified else None)

    counts = Counter(e["event_type"] for e in inside if e["source"] != "MANUAL")
    natural_cycles = {e["request_id"] for e in inside if e["event_type"] == "work_started" and
                      e["source"] == "PERIODIC" and e["work_attempt"] == 0}
    natural_cycles -= {e["request_id"] for e in events if e["event_type"] == "work_started" and
                       e["source"] == "PERIODIC" and e["work_attempt"] == 0 and location(e) != "window"}
    attempts = {(e["request_id"], e["work_id"], e["work_attempt"]) for e in inside
                if e["event_type"] == "work_started" and e["source"] != "MANUAL"}
    row = {k: m[k] for k in ("run_id", "data_kind", "run_phase", "case_id", "subscenario", "repetition",
                            "device_alias", "mode", "execution_status", "outcome", "validity", "intervention")}
    source_context = run.get("source_context")
    row.update({"analysis_version": VERSION, "group_id": group_identity(m, source_context),
                "server_store_epoch": (source_context or {}).get("server_store_epoch"),
                **{k: m["build"][k] for k in ("app_commit", "server_commit", "apk_sha256")},
                "manifest_sha256": run["manifest_sha256"], "events_sha256": run["events_sha256"],
                "target_version": target, "declared_cached_version_after": obs["cached_version_after"],
                "declared_natural_periodic_cycles": obs["natural_periodic_cycles"],
                "window_basis": "ANDROID_MONOTONIC" if has_window else "UNAVAILABLE",
                "window_events_verified": bool(window_verified),
                "observed_completion": ("NOT_RUN" if m["execution_status"] == "NOT_RUN" else
                                        "APPLIED_TARGET" if applied else "LATE_TARGET" if late else
                                        "NO_TARGET_EVIDENCE" if window_verified and recovery_verified else
                                        "UNCERTAIN_WINDOW"),
                "eligible": (m["data_kind"] == "OBSERVED" and m["run_phase"] == "main" and
                             m["validity"] == "VALID" and m["execution_status"] == "COMPLETED" and not flags),
                "target_applied_in_window": bool(applied) if
                                            (window_verified and recovery_verified) or applied else None,
                "late_target_applied_count": len(late) if window_verified and recovery_verified else None,
                "natural_periodic_cycles": len(natural_cycles) if window_verified else None,
                "work_attempt_count": len(attempts) if window_verified else None,
                "get_started_count": len({e["network_call_id"] for e in inside if
                                          e["event_type"] == "snapshot_fetch_started" and e["source"] != "MANUAL"})
                                     if window_verified else None,
                "retry_event_count": counts["sync_retrying"] if window_verified else None,
                "applied_event_count": counts["snapshot_applied"] if window_verified else None,
                **{kind + "_event_count_all": sum(e["event_type"] == kind for e in events) for kind in
                   ("server_updated", "push_send_accepted", "push_send_skipped", "push_received",
                    "work_enqueued", "work_started", "snapshot_fetch_started", "snapshot_applied")},
                "db_write_count": None, "received_to_enqueue_ms": receipt_enqueue_ms,
                "queue_ms": queue_ms, "sync_ms": sync_ms,
                "update_to_applied_ms": end_to_end["estimate_ms"] if end_to_end else None,
                "update_to_applied_uncertainty_ms": end_to_end["uncertainty_ms"] if end_to_end else None,
                "update_to_received_ms": receive_delta["estimate_ms"] if receive_delta else None,
                "update_to_received_uncertainty_ms": receive_delta["uncertainty_ms"] if receive_delta else None,
                "flags": "|".join(sorted(flags))})
    return {"row": row, "event_counts": dict(sorted(Counter(e["event_type"] for e in events).items())),
            "window_event_counts": dict(sorted(counts.items())), "fetches": fetch_details,
            "bucket_counts": {k: len(buckets[k]) for k in ("setup", "window", "late", "unknown", "server")},
            "duplicates_ignored": run["duplicates"], "clock_estimate": estimate, "clock_reason": clock_reason,
            "declared_reason_codes": m["reason_codes"], "group_identity": {
                **{k: m[k] for k in ("build", "device", "config", "protocol_version", "event_schema_version")},
                "source_context": source_context}}


def summarize(analyses):
    groups = defaultdict(list)
    for analysis in analyses:
        groups[analysis["row"]["group_id"]].append(analysis)
    result = []
    for group_id, group in sorted(groups.items()):
        rows = [a["row"] for a in group]
        eligible = [r for r in rows if r["eligible"]]
        complete = [r for r in eligible if r["outcome"] == "SUCCESS" and r["target_applied_in_window"]]
        metrics = {}
        for key in ("update_to_applied_ms", "update_to_received_ms", "received_to_enqueue_ms", "queue_ms", "sync_ms"):
            values = [r[key] for r in complete if r[key] is not None]
            metrics[key] = {"n_measured": len(values), "n_missing": len(complete) - len(values),
                            "median": statistics.median(values) if values else None,
                            "min": min(values) if values else None, "max": max(values) if values else None}
        result.append({"group_id": group_id, **{k: rows[0][k] for k in
                       ("data_kind", "run_phase", "case_id", "subscenario", "device_alias", "mode", "intervention")},
                       **group[0]["group_identity"], "n_input": len(rows), "n_eligible": len(eligible),
                       "n_excluded": len(rows) - len(eligible), "n_complete": len(complete),
                       "n_not_run": sum(r["execution_status"] == "NOT_RUN" for r in rows),
                       "declared_outcomes": dict(sorted(Counter(r["outcome"] for r in rows).items())),
                       "valid_completed_declared_outcomes": dict(sorted(Counter(r["outcome"] for r in rows
                           if r["validity"] == "VALID" and r["execution_status"] == "COMPLETED").items())),
                       "eligible_outcomes": dict(sorted(Counter(r["outcome"] for r in eligible).items())),
                       "completion_rate": len(complete) / len(eligible) if eligible else None,
                       "metrics": metrics})
    return result


def csv_text(analyses):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(analyses[0]["row"]), lineterminator="\n")
    writer.writeheader()
    for analysis in analyses:
        writer.writerow({k: str(v).lower() if type(v) is bool else v for k, v in analysis["row"].items()})
    return output.getvalue()


def publish(directories, dataset, output_base, batch_id, source_index=None):
    require(contract.matches(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", batch_id), "BATCH_ID_INVALID")
    require(bool(directories) or source_index is not None, "RUN_REQUIRED")
    require(not directories or source_index is None, "RUN_INPUT_CONFLICT")
    source = None
    if source_index is not None:
        runs, source = load_source_index(source_index, dataset)
    else:
        runs = [load_run(directory, dataset) for directory in directories]
    analyses, seen = [], set()
    for run in runs:
        identity = (run["manifest"]["run_id"], run["manifest"]["device_alias"])
        require(identity not in seen, "DUPLICATE_RUN_INPUT")
        seen.add(identity)
        analyses.append(analyze_run(run))
    analyses.sort(key=lambda a: (a["row"]["run_id"], a["row"]["device_alias"]))
    summary = {"analysis_version": VERSION, "dataset": dataset, "groups": summarize(analyses)}
    payloads = {"results.csv": csv_text(analyses),
                "summary.json": json.dumps(summary, ensure_ascii=True, sort_keys=True, indent=2) + "\n"}
    report = {"status": "COMPLETED", "analysis_version": VERSION, "dataset": dataset,
              "batch_id": batch_id, "runtime_experiment_performed": False,
              "analyzer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "validator_sha256": hashlib.sha256(Path(contract.__file__).read_bytes()).hexdigest(),
              "outputs_sha256": {name: hashlib.sha256(value.encode("utf-8")).hexdigest()
                                 for name, value in payloads.items()}, "runs": analyses}
    if source is not None:
        report["source"] = source
    payloads["analysis_report.json"] = json.dumps(report, ensure_ascii=True, sort_keys=True, indent=2) + "\n"
    directory = Path(output_base) / f"{dataset}_analysis" / batch_id
    # All validation and analysis must succeed before creating an output batch.
    try:
        directory.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        raise AnalysisError("OUTPUT_EXISTS") from None
    except OSError:
        raise AnalysisError("OUTPUT_UNWRITABLE") from None
    try:
        for name, value in payloads.items():
            # Explicit UTF-8/LF makes CSV, JSON and checksums reproducible on Windows.
            with (directory / name).open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(value)
    except OSError:
        # A batch without the final COMPLETED report must not be consumed.
        raise AnalysisError("OUTPUT_WRITE_FAILED") from None
    return {"status": "COMPLETED", "dataset": dataset, "batch_id": batch_id, "runs": len(analyses)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--run", type=Path, action="append",
                        help="Directory containing canonical manifest.json and events.jsonl; repeat per run")
    inputs.add_argument("--source-index", type=Path,
                        help="JSON index of exact Git source commit, paths and SHA-256 hashes")
    parser.add_argument("--dataset", choices=("fixture", "pilot", "main"), default="main")
    parser.add_argument("--output-base", type=Path, default=ROOT / "experiments")
    parser.add_argument("--batch-id", required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(publish(args.run, args.dataset, args.output_base, args.batch_id,
                                 args.source_index), sort_keys=True))
        return 0
    except AnalysisError as error:
        print(f"SEM45_ANALYSIS_ERROR:{error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
