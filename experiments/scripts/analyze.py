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
import sys

import export_logs as contract

VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parents[2]


class AnalysisError(Exception):
    """Static error codes only; never print raw logs, credentials or paths."""


def require(condition, code):
    if not condition:
        raise AnalysisError(code)


def load_run(directory, dataset):
    """Read one explicit dataset; reject mixed routes, legacy and fake observed data."""
    require(dataset in {"fixture", "pilot", "main"}, "DATASET_INVALID")
    directory = Path(directory)
    try:
        manifest_bytes = (directory / "manifest.json").read_bytes()
        event_bytes = (directory / "events.jsonl").read_bytes()
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


def only(events):
    """An ambiguous join remains unknown instead of picking an arbitrary row."""
    return events[0] if len(events) == 1 else None


def group_identity(manifest):
    identity = {k: manifest[k] for k in ("data_kind", "run_phase", "case_id", "subscenario",
                "device_alias", "mode", "protocol_version", "event_schema_version", "intervention",
                "build", "device", "config")}
    return hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=True,
                                    separators=(",", ":")).encode()).hexdigest()


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
    inside = buckets["window"]
    if any(e["source"] == "MANUAL" for e in inside):
        flags.add("MANUAL_IN_WINDOW")
    expected_source = {"E01": "PERIODIC", "E02": "PUSH", "E05": "PUSH", "E06": "PERIODIC"}.get(m["case_id"])
    expected_mode = {"E01": "PERIODIC", "E02": "PUSH", "E05": "PUSH", "E06": "HYBRID"}.get(m["case_id"])
    if expected_mode and m["mode"] != expected_mode:
        flags.add("CASE_MODE_MISMATCH")
    if m["case_id"] in {"E03", "E04"} and m["mode"] not in {"PERIODIC", "PUSH"}:
        flags.add("CASE_MODE_MISMATCH")
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

    target = obs["target_version"]
    def target_apply(e):
        return (e["event_type"] == "snapshot_applied" and e["data_version"] == target and
                target is not None and e["source"] != "MANUAL" and
                (expected_source is None or e["source"] == expected_source))

    applied = sorted([e for e in inside if target_apply(e)],
                     key=lambda e: (e["elapsed_realtime_ms"], e["event_id"]))
    late = [e for e in buckets["late"] if target_apply(e)]
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
        if enqueued:
            receipts = [e for e in events if e["event_type"] == "push_received" and
                        set(e["signal_ids"]) & set(enqueued["signal_ids"]) and
                        monotonic_delta(e, enqueued) is not None]
            receipt_enqueue_ms = monotonic_delta(only(receipts), enqueued)
    if m["execution_status"] == "COMPLETED" and ((m["outcome"] == "SUCCESS") != bool(applied)):
        flags.add("OUTCOME_EVIDENCE_CONFLICT")

    updated = only([e for e in events if e["event_type"] == "server_updated" and e["data_version"] == target])
    if m["case_id"] == "E06" and (updated is None or not any(
            e["event_type"] == "push_send_skipped" and e["data_version"] == target and
            e["update_id"] == updated["update_id"] for e in events)):
        flags.add("FAULT_SKIP_EVIDENCE_MISSING")
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
    end_to_end = cross_clock_delta(updated, completion, clock)
    receipts = []
    if updated:
        signals = {s for e in events if e["origin"] == "SERVER" and e["source"] == "PUSH" and
                   e["data_version"] == target and e["update_id"] == updated["update_id"] for s in e["signal_ids"]}
        receipts = [e for e in inside if e["event_type"] == "push_received" and
                    set(e["signal_ids"]) & signals]
    receive_delta = cross_clock_delta(updated, only(receipts), clock)

    counts = Counter(e["event_type"] for e in inside if e["source"] != "MANUAL")
    natural_cycles = {e["request_id"] for e in inside if e["event_type"] == "work_started" and
                      e["source"] == "PERIODIC" and e["work_attempt"] == 0}
    natural_cycles -= {e["request_id"] for e in events if e["event_type"] == "work_started" and
                       e["source"] == "PERIODIC" and e["work_attempt"] == 0 and location(e) != "window"}
    attempts = {(e["request_id"], e["work_id"], e["work_attempt"]) for e in inside
                if e["event_type"] == "work_started" and e["source"] != "MANUAL"}
    row = {k: m[k] for k in ("run_id", "data_kind", "run_phase", "case_id", "subscenario", "repetition",
                            "device_alias", "mode", "execution_status", "outcome", "validity", "intervention")}
    row.update({"analysis_version": VERSION, "group_id": group_identity(m),
                **{k: m["build"][k] for k in ("app_commit", "server_commit", "apk_sha256")},
                "manifest_sha256": run["manifest_sha256"], "events_sha256": run["events_sha256"],
                "target_version": target, "declared_cached_version_after": obs["cached_version_after"],
                "window_basis": "ANDROID_MONOTONIC" if has_window else "UNAVAILABLE",
                "observed_completion": ("NOT_RUN" if m["execution_status"] == "NOT_RUN" else
                                        "APPLIED_TARGET" if applied else "LATE_TARGET" if late else
                                        "NO_TARGET_EVIDENCE" if has_window else "UNCERTAIN_WINDOW"),
                "eligible": (m["data_kind"] == "OBSERVED" and m["run_phase"] == "main" and
                             m["validity"] == "VALID" and m["execution_status"] == "COMPLETED" and not flags),
                "target_applied_in_window": bool(applied), "late_target_applied_count": len(late),
                "natural_periodic_cycles": len(natural_cycles), "work_attempt_count": len(attempts),
                "get_started_count": len({e["network_call_id"] for e in inside if
                                          e["event_type"] == "snapshot_fetch_started" and e["source"] != "MANUAL"}),
                "retry_event_count": counts["sync_retrying"], "applied_event_count": counts["snapshot_applied"],
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
            "declared_reason_codes": m["reason_codes"], "group_identity": {k: m[k] for k in
                ("build", "device", "config", "protocol_version", "event_schema_version")}}


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


def publish(directories, dataset, output_base, batch_id):
    require(contract.matches(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", batch_id), "BATCH_ID_INVALID")
    require(bool(directories), "RUN_REQUIRED")
    analyses, seen = [], set()
    for directory in directories:
        run = load_run(directory, dataset)
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
    parser.add_argument("--run", type=Path, action="append", required=True,
                        help="Directory containing canonical manifest.json and events.jsonl; repeat per run")
    parser.add_argument("--dataset", choices=("fixture", "pilot", "main"), default="main")
    parser.add_argument("--output-base", type=Path, default=ROOT / "experiments")
    parser.add_argument("--batch-id", required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(publish(args.run, args.dataset, args.output_base, args.batch_id), sort_keys=True))
        return 0
    except AnalysisError as error:
        print(f"SEM45_ANALYSIS_ERROR:{error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
