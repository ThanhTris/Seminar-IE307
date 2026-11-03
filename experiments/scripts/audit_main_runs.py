#!/usr/bin/env python3
"""SEM-44: audit exported main-run manifests/events against results.csv.

Read-only for all inputs. Writes a Markdown audit report; it never edits logs or CSV.
Python 3.9+. This script does not create observations or infer missing events.
"""

import argparse
import csv
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
EXPORTER_PATH = ROOT / "experiments/scripts/export_logs.py"
spec = importlib.util.spec_from_file_location("sem24_export_logs", EXPORTER_PATH)
exporter = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = exporter
spec.loader.exec_module(exporter)

CSV_REQUIRED = {"run_id", "device_alias", "mode"}
CSV_COMPARE = (
    "run_id", "device_alias", "mode", "case_id", "run_phase", "app_commit",
    "server_commit", "apk_sha256", "outcome", "cached_version_after",
)
LATENCY_COLUMNS = {"latency_ms", "latency_first_applied_ms", "time_to_apply_ms"}
COUNT_COLUMNS = {
    "push_send_accepted_count": "push_send_accepted",
    "work_started_count": "work_started",
    "work_enqueued_count": "work_enqueued",
    "push_received_count": "push_received",
    "snapshot_applied_count": "snapshot_applied",
    "snapshot_unchanged_count": "snapshot_unchanged",
    "snapshot_stale_count": "snapshot_stale",
    "sync_retrying_count": "sync_retrying",
    "sync_failed_count": "sync_failed",
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def audit_run(run_dir):
    issues = []
    manifest_path = run_dir / "manifest.json"
    events_path = run_dir / "events.jsonl"
    if not manifest_path.is_file() or not events_path.is_file():
        return None, [], ["RUN_ARTIFACT_MISSING"]
    try:
        manifest = load_json(manifest_path)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None, [], ["MANIFEST_INVALID_JSON"]
    if not isinstance(manifest, dict):
        return None, [], ["MANIFEST_SHAPE_INVALID"]
    run_id = manifest.get("run_id")
    alias = manifest.get("device_alias")
    try:
        manifest = exporter.validate_manifest(manifest, run_id, alias, fixture=False)
    except (exporter.ExportError, TypeError, ValueError, KeyError):
        return None, [], ["MANIFEST_CONTRACT_INVALID"]
    if manifest["run_phase"] != "main":
        issues.append("NON_MAIN_RUN_IN_RUNS_DIRECTORY")
    if manifest["execution_status"] == "NOT_RUN" and manifest["outcome"] != "NOT_RUN":
        issues.append("NOT_RUN_OUTCOME_CONFLICT")

    events = []
    seen = {}
    try:
        lines = events_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return manifest, [], issues + ["EVENTS_UNREADABLE"]
    for number, line in enumerate(lines, 1):
        try:
            raw = exporter.parse_json(line)
            event = exporter.validate_event(raw)
        except (exporter.ExportError, TypeError, ValueError, KeyError):
            issues.append(f"EVENT_INVALID_LINE_{number}")
            continue
        if event["run_id"] != run_id or event["device_alias"] != alias:
            issues.append(f"EVENT_RUN_OR_DEVICE_MISMATCH_LINE_{number}")
            continue
        if event["mode"] != manifest["mode"]:
            issues.append(f"EVENT_MODE_MISMATCH_LINE_{number}")
        previous = seen.get(event["event_id"])
        if previous is not None:
            if previous != event:
                issues.append(f"EVENT_ID_CONFLICT_LINE_{number}")
            else:
                issues.append(f"DUPLICATE_EVENT_LINE_{number}")
                continue
        seen[event["event_id"]] = event
        events.append(event)

    if manifest["execution_status"] == "NOT_RUN" and events:
        issues.append("NOT_RUN_CONTAINS_EVENTS")
    if manifest["execution_status"] == "COMPLETED" and not events:
        issues.append("COMPLETED_RUN_WITHOUT_EVENTS")
    before = manifest["observation"].get("cached_version_before")
    after = manifest["observation"].get("cached_version_after")
    target = manifest["observation"].get("target_version")
    if before is not None and after is not None and after < before:
        issues.append("CACHE_VERSION_DECREASED")
    applied = [e for e in events if e["event_type"] == "snapshot_applied"]
    if target is not None and any(e["data_version"] != target for e in applied):
        issues.append("APPLIED_VERSION_DIFFERS_FROM_TARGET")
    work_starts = {}
    for event in events:
        if event["event_type"] == "work_started":
            key = (event["request_id"], event["work_id"], event["work_attempt"])
            work_starts[key] = event
    terminal_types = {"snapshot_applied", "snapshot_unchanged", "snapshot_stale", "sync_retrying", "sync_failed"}
    for event in events:
        if event["event_type"] not in terminal_types:
            continue
        key = (event["request_id"], event["work_id"], event["work_attempt"])
        start = work_starts.get(key)
        if start is None:
            issues.append("SYNC_RESULT_WITHOUT_MATCHING_WORK_START")
        elif event["elapsed_realtime_ms"] < start["elapsed_realtime_ms"]:
            issues.append("SYNC_RESULT_MONOTONICALLY_PRECEDES_START")
    return manifest, events, issues


def audit_csv(csv_path, runs):
    issues = []
    rows = []
    if not csv_path.is_file():
        return rows, ["RESULTS_CSV_MISSING"]
    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = set(reader.fieldnames or [])
            missing = CSV_REQUIRED - headers
            if missing:
                return rows, ["CSV_REQUIRED_COLUMNS_MISSING"]
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error):
        return rows, ["RESULTS_CSV_UNREADABLE"]

    known_run_ids = {manifest["run_id"] for manifest, _, _ in runs if manifest}
    row_by_run = {}
    for row_number, row in enumerate(rows, 2):
        run_id = str(row.get("run_id") or "")
        if not run_id:
            issues.append(f"CSV_RUN_ID_EMPTY_ROW_{row_number}")
            continue
        row_by_run.setdefault(run_id, []).append((row_number, row))
        if run_id not in known_run_ids:
            issues.append(f"CSV_RUN_WITHOUT_MANIFEST_ROW_{row_number}")
        if str(row.get("outcome") or "").upper() in {"TIMEOUT", "NOT_OBSERVED", "UNKNOWN"}:
            for key in LATENCY_COLUMNS & row.keys():
                raw = str(row.get(key) or "").strip()
                if raw in {"0", "0.0", "0.00"}:
                    issues.append(f"TIMEOUT_ZERO_LATENCY_ROW_{row_number}")

    for manifest, _, _ in runs:
        if manifest and manifest["run_id"] not in row_by_run:
            issues.append("MANIFEST_WITHOUT_CSV_ROW_" + manifest["run_id"])
    for manifest, _, _ in runs:
        if not manifest:
            continue
        entries = row_by_run.get(manifest["run_id"], [])
        run_events = next((events for run_manifest, events, _ in runs if run_manifest and run_manifest["run_id"] == manifest["run_id"]), [])
        for row_number, row in entries:
            for field in CSV_COMPARE:
                expected = manifest.get(field)
                if field in {"app_commit", "server_commit", "apk_sha256", "cached_version_after"}:
                    if field in {"app_commit", "server_commit", "apk_sha256"}:
                        expected = manifest["build"].get(field)
                    elif field == "cached_version_after":
                        expected = manifest["observation"].get(field)
                if expected is not None and str(row.get(field) or "").strip() not in {"", str(expected)}:
                    issues.append(f"CSV_MANIFEST_MISMATCH_{field.upper()}_ROW_{row_number}")
            for column, event_type in COUNT_COLUMNS.items():
                raw_count = str(row.get(column) or "").strip()
                if not raw_count:
                    continue
                try:
                    csv_count = int(raw_count)
                except ValueError:
                    issues.append(f"CSV_COUNT_INVALID_{column.upper()}_ROW_{row_number}")
                else:
                    actual_count = sum(1 for event in run_events if event["event_type"] == event_type)
                    if csv_count != actual_count:
                        issues.append(f"CSV_EVENT_COUNT_MISMATCH_{column.upper()}_ROW_{row_number}")
    return rows, issues


def render_report(runs, csv_path, csv_rows, issues):
    report_issues = list(issues)
    run_count = len(runs)
    event_count = sum(len(events) for _, events, _ in runs)
    background = sum(
        1 for _, events, _ in runs for e in events
        if e["event_type"] == "work_started" and e["source"] in {"PERIODIC", "PUSH"}
    )
    manual = sum(
        1 for _, events, _ in runs for e in events
        if e["event_type"] == "work_started" and e["source"] == "MANUAL"
    )
    status = "NOT_RUN" if not run_count or not csv_rows else ("REVIEW_REQUIRED" if report_issues else "AUDIT_READY")
    lines = [
        "# SEM-44 — Automated main-run audit", "",
        f"- Audit status: **{status}**", f"- Runs inspected: {run_count}",
        f"- CSV rows: {len(csv_rows)}", f"- Valid events parsed: {event_count}",
        f"- Background worker starts (PERIODIC/PUSH): {background}",
        f"- Manual worker starts (excluded from background count): {manual}",
        f"- Generated at UTC: {datetime.utcnow().isoformat(timespec='seconds')}Z", "",
        "The report reads input artifacts and does not rewrite logs or CSV. `AUDIT_READY` means structural cross-checks found no listed issue; it does not certify the physical procedure or replace owner review.", "",
        "## Runs", "", "| Run | Device | Mode | Phase | Outcome | Event count | Issues |", "|---|---|---|---|---|---:|---|",
    ]
    for manifest, events, run_issues in runs:
        if not manifest:
            lines.append(f"| `{(events[0] if events else 'unknown')}` | — | — | — | — | {len(events)} | `{', '.join(run_issues)}` |")
            continue
        lines.append(
            f"| `{manifest['run_id']}` | `{manifest['device_alias']}` | {manifest['mode']} | {manifest['run_phase']} | {manifest['outcome']} | {len(events)} | `{', '.join(run_issues) or 'none'}` |"
        )
    lines.extend(["", "## Audit issues", ""])
    if report_issues:
        lines.extend(f"- `{issue}`" for issue in sorted(set(report_issues)))
    else:
        lines.append("No structural issues found in the available inputs.")
    lines.extend([
        "", "## Interpretation", "",
        "- A `work_started` with source `MANUAL` is reported separately and must not enter background success rates.",
        "- A `push_send_accepted` does not count as receipt or application; only `snapshot_applied` confirms cache application.",
        "- Missing events remain unobserved; this audit never infers delivery or success from event absence.",
        "- Timeout latency must remain blank/null, not zero.",
        "- This script does not calculate latency across devices. Apply clock-offset uncertainty and same-boot monotonic rules from `docs/EXPERIMENT_PROTOCOL.md`.",
        "- Record run-specific producer corrections without editing original event data; rerun the audit after source artifacts change.",
        "",
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=ROOT / "experiments/runs")
    parser.add_argument("--csv", type=Path, default=ROOT / "experiments/results.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "experiments/AUDIT_RESULTS.md")
    args = parser.parse_args(argv)
    runs = []
    top_issues = []
    if args.runs.is_dir():
        for run_dir in sorted(p for p in args.runs.iterdir() if p.is_dir()):
            manifest, events, issues = audit_run(run_dir)
            runs.append((manifest, events, issues))
            top_issues.extend(issues)
    else:
        top_issues.append("RUNS_DIRECTORY_MISSING")
    csv_rows, csv_issues = audit_csv(args.csv, runs)
    top_issues.extend(csv_issues)
    report = render_report(runs, args.csv, csv_rows, top_issues)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(report)
    print(json.dumps({"status": "NOT_RUN" if not runs or not csv_rows else "AUDIT_WRITTEN", "runs": len(runs), "csv_rows": len(csv_rows), "issues": len(set(top_issues)), "output": str(args.output)}))
    return 0 if runs and csv_rows and not top_issues else 2


if __name__ == "__main__":
    sys.exit(main())
