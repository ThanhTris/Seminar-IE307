#!/usr/bin/env python3
"""SEM-24: export one run without synthesizing measurements. Python 3.9+."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from uuid import UUID

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / "experiments/RUN_MANIFEST_TEMPLATE.json"
MAX_INT = 2**53 - 1
ID = r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}"
CODE = r"[A-Z][A-Z0-9_]{0,63}"
SEMVER = r"\d+\.\d+\.\d+"
MODES = {"PERIODIC", "PUSH", "HYBRID"}
FIELDS = (
    "schema_version event_id event_type origin run_id mode source device_alias "
    "timestamp_utc elapsed_realtime_ms boot_session_id data_version cached_version "
    "version_hint request_id work_id work_attempt network_call_id update_id "
    "signal_ids send_attempt_id message_id ttl_ms http_status provider_code outcome reason"
).split()
EVENTS = {
    "server_updated": ("SERVER", {None}, {"updated"}),
    "push_send_accepted": ("SERVER", {"PUSH"}, {"accepted"}),
    "push_send_rejected": ("SERVER", {"PUSH"}, {"rejected"}),
    "push_send_failed_local": ("SERVER", {"PUSH"}, {"failure"}),
    "push_send_unknown": ("SERVER", {"PUSH"}, {"unknown"}),
    "push_send_skipped": ("SERVER", {"PUSH"}, {"skipped"}),
    "push_received": ("ANDROID", {"PUSH"}, {"received"}),
    "trigger_rejected": ("ANDROID", {"MANUAL", "PERIODIC", "PUSH"}, {"rejected"}),
    "periodic_registered": ("ANDROID", {"PERIODIC"}, {"registered"}),
    "work_enqueued": ("ANDROID", {"MANUAL", "PUSH"}, {"enqueued"}),
    "work_started": ("ANDROID", {"MANUAL", "PERIODIC", "PUSH"}, {"started"}),
    "snapshot_fetch_started": ("ANDROID", {"MANUAL", "PERIODIC", "PUSH"}, {"started"}),
    "snapshot_fetch_completed": ("ANDROID", {"MANUAL", "PERIODIC", "PUSH"}, {"success", "not_modified", "failure"}),
    "snapshot_applied": ("ANDROID", {"MANUAL", "PERIODIC", "PUSH"}, {"applied"}),
    "snapshot_unchanged": ("ANDROID", {"MANUAL", "PERIODIC", "PUSH"}, {"unchanged"}),
    "snapshot_stale": ("ANDROID", {"MANUAL", "PERIODIC", "PUSH"}, {"stale"}),
    "sync_retrying": ("ANDROID", {"MANUAL", "PERIODIC", "PUSH"}, {"retry"}),
    "sync_failed": ("ANDROID", {"MANUAL", "PERIODIC", "PUSH"}, {"failure"}),
}
# Known signatures are a second check, not a replacement for local deny values.
SECRET = re.compile(
    r"emulator-\d{4,}|AIza[\w-]{20,}|ya29\.[\w.-]+|gh[pousr]_[\w]{20,}|"
    r"-----BEGIN [^-]*PRIVATE KEY|Bearer\s+\S+|"
    r"[\w-]{20,}:[\w-]{40,}|eyJ[\w-]+\.[\w-]+\.[\w-]+|"
    r"\b(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)\b"
)


class ExportError(Exception):
    """Messages contain static codes/field names only, never source values."""


def require(condition, code):
    if not condition:
        raise ExportError(code)


def matches(pattern, value):
    return isinstance(value, str) and re.fullmatch(pattern, value) is not None


def uint(value, maximum=MAX_INT):
    return type(value) is int and 0 <= value <= maximum


def utc(value):
    if not matches(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z", value):
        return False
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
        return True
    except ValueError:
        return False


def uuid_string(value, v4=False):
    try:
        parsed = UUID(value)
        return str(parsed) == value.lower() and (not v4 or parsed.version == 4)
    except (ValueError, TypeError, AttributeError):
        return False


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, "DUPLICATE_JSON_KEY")
        obj[key] = value
    return obj


def parse_json(text):
    def reject_constant(_):
        raise ExportError("NONFINITE_JSON")

    try:
        return json.loads(text, object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except (ValueError, RecursionError):
        raise ExportError("INVALID_JSON") from None


def read_text(path):
    try:
        return Path(path).read_bytes().decode("utf-8")
    except (OSError, UnicodeError):
        raise ExportError("INPUT_UNREADABLE") from None


def public_safe(value, deny_values):
    """Fail rather than change any retained value, including opaque message IDs."""
    if isinstance(value, dict):
        for item in value.values():
            public_safe(item, deny_values)
    elif isinstance(value, list):
        for item in value:
            public_safe(item, deny_values)
    elif isinstance(value, str):
        try:
            value.encode("utf-8")
        except UnicodeError:
            raise ExportError("INVALID_UNICODE") from None
        require(not SECRET.search(value), "SENSITIVE_PUBLIC_VALUE")
        require(not any(secret in value for secret in deny_values), "DENIED_PUBLIC_VALUE")
        require(all(ord(c) >= 32 for c in value), "CONTROL_CHARACTER")


def project_shape(value, template):
    """Keep only declared fields recursively; do not copy diagnostic/free text."""
    require(isinstance(value, dict), "MANIFEST_OBJECT_REQUIRED")
    require(set(template) <= set(value), "MANIFEST_FIELDS_MISSING")
    projected = {}
    for key, sample in template.items():
        if isinstance(sample, dict):
            projected[key] = project_shape(value[key], sample)
        else:
            require(not isinstance(value[key], dict), "MANIFEST_LEAF_OBJECT_INVALID")
            projected[key] = value[key]
    return projected


def validate_manifest(raw, run_id, alias, fixture):
    manifest = project_shape(raw, parse_json(read_text(TEMPLATE)))
    require(manifest["manifest_version"] == "1.0.0", "MANIFEST_VERSION_UNSUPPORTED")
    require(manifest["data_kind"] == ("FIXTURE" if fixture else "OBSERVED"), "DATA_KIND_MISMATCH")
    require(manifest["run_id"] == run_id and manifest["device_alias"] == alias, "MANIFEST_ID_MISMATCH")
    require(manifest["run_phase"] in {"development", "pilot", "main"}, "PHASE_INVALID")
    require(not fixture or manifest["run_phase"] == "development", "FIXTURE_PHASE_INVALID")
    require(manifest["mode"] in MODES, "MODE_INVALID")
    require(manifest["execution_status"] in {"NOT_RUN", "RUNNING", "COMPLETED", "ABORTED"}, "EXECUTION_INVALID")
    require(manifest["outcome"] in {"NOT_RUN", "SUCCESS", "FAILURE", "TIMEOUT", "UNKNOWN"}, "OUTCOME_INVALID")
    require(manifest["validity"] in {"NOT_ASSESSED", "VALID", "INVALID"}, "VALIDITY_INVALID")
    require(manifest["intervention"] in {"NONE", "INJECTED"}, "INTERVENTION_INVALID")
    require(manifest["case_id"] in {"E01", "E02", "E03", "E04", "E05", "E06", "M1", "CONTROL", "PROCESS_DEATH", "RECENT_SWIPE", "FORCE_STOP"}, "CASE_INVALID")
    require(manifest["event_schema_version"] == "2.0.0" and manifest["build"]["api_version"] == "2.0.0", "CONTRACT_VERSION_UNSUPPORTED")

    # Every leaf has a type; null means not measured, never a placeholder value.
    boolean_keys = {"candidate_gate_passed", "powered", "battery_saver", "package_stopped_before", "controlled", "work_drained", "idle_restored", "network_restored", "package_stopped_cleared"}
    integer_keys = {"repetition", "version_code", "compile_sdk", "target_sdk", "min_sdk", "api_level", "page_size_bytes", "battery_percent", "periodic_interval_minutes", "periodic_flex_minutes", "periodic_initial_delay_ms", "ttl_ms", "connect_timeout_ms", "read_timeout_ms", "retry_max_attempts", "retry_backoff_ms", "planned_window_seconds", "actual_duration_ms", "start_elapsed_realtime_ms", "end_elapsed_realtime_ms", "server_version_before", "cached_version_before", "target_version", "cached_version_after", "natural_periodic_cycles"}

    def leaves(obj):
        for key, value in obj.items():
            if isinstance(value, dict):
                leaves(value)
            elif key in {"before_samples", "after_samples"}:
                require(isinstance(value, list), "CLOCK_SAMPLES_INVALID")
                for sample in value:
                    require(isinstance(sample, dict) and set(sample) == {"client_send_utc", "server_utc", "client_receive_utc", "resolution_ms"}, "CLOCK_SAMPLE_FIELDS_INVALID")
                    require(all(utc(sample[k]) for k in ("client_send_utc", "server_utc", "client_receive_utc")) and uint(sample["resolution_ms"]), "CLOCK_SAMPLE_INVALID")
                    require(datetime.fromisoformat(sample["client_send_utc"].replace("Z", "+00:00")) <= datetime.fromisoformat(sample["client_receive_utc"].replace("Z", "+00:00")), "CLOCK_SAMPLE_REVERSED")
            elif key in {"reason_codes", "network_transports", "evidence_files"}:
                require(isinstance(value, list), "MANIFEST_LIST_INVALID")
                pattern = r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}" if key == "evidence_files" else CODE
                require(all(matches(pattern, x) for x in value), "MANIFEST_LIST_ITEM_INVALID")
            elif value is not None:
                if key in boolean_keys:
                    require(type(value) is bool, "MANIFEST_BOOLEAN_INVALID")
                elif key in {"offset_before_ms", "offset_after_ms"}:
                    require(type(value) is int and abs(value) <= MAX_INT, "CLOCK_OFFSET_INVALID")
                elif key in {"uncertainty_before_ms", "uncertainty_after_ms"}:
                    require(uint(value), "CLOCK_UNCERTAINTY_INVALID")
                elif key in integer_keys:
                    require(uint(value), "MANIFEST_INTEGER_INVALID")
                elif key.endswith("_utc"):
                    require(utc(value), "MANIFEST_TIMESTAMP_INVALID")
                else:
                    require(isinstance(value, str) and 1 <= len(value) <= 512, "MANIFEST_STRING_INVALID")
    leaves(manifest)
    for key in ("protocol_version", "event_schema_version"):
        require(matches(SEMVER, manifest[key]), "MANIFEST_SEMVER_INVALID")
    for key in ("app_commit", "server_commit", "apk_sha256"):
        value = manifest["build"][key]
        require(value is None or matches(r"[0-9a-f]{64}" if key == "apk_sha256" else r"[0-9a-f]{40}", value), "BUILD_HASH_INVALID")
    require(matches(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+", manifest["build"]["package_name"]), "PACKAGE_INVALID")
    require(manifest["config"]["battery_percent"] is None or manifest["config"]["battery_percent"] <= 100, "BATTERY_INVALID")
    require(manifest["config"]["ttl_ms"] is None or manifest["config"]["ttl_ms"] <= 2419200000, "TTL_INVALID")
    require(manifest["cleanup"]["status"] in {"NOT_RUN", "PASS", "FAIL"}, "CLEANUP_INVALID")
    for key in ("subscenario", "operator_alias"):
        require(manifest[key] is None or matches(ID, manifest[key]), "MANIFEST_ALIAS_INVALID")
    require(manifest["clock"]["method_code"] is None or matches(CODE, manifest["clock"]["method_code"]), "CLOCK_METHOD_INVALID")
    require(manifest["clock"]["client_clock"] in {None, "HOST", "ANDROID"}, "CLOCK_REFERENCE_INVALID")
    obs = manifest["observation"]
    if obs["start_utc"] is not None and obs["end_utc"] is not None:
        require(datetime.fromisoformat(obs["end_utc"].replace("Z", "+00:00")) >= datetime.fromisoformat(obs["start_utc"].replace("Z", "+00:00")), "WINDOW_REVERSED")
    if manifest["outcome"] == "NOT_RUN" or manifest["execution_status"] == "NOT_RUN":
        require(manifest["outcome"] == "NOT_RUN" and manifest["execution_status"] == "NOT_RUN" and manifest["validity"] == "NOT_ASSESSED", "NOT_RUN_INCONSISTENT")
    if manifest["validity"] == "INVALID" or manifest["outcome"] in {"FAILURE", "TIMEOUT", "UNKNOWN"}:
        require(bool(manifest["reason_codes"]), "REASON_REQUIRED")
    if manifest["run_phase"] == "main" and manifest["validity"] == "VALID":
        require(all(manifest["build"][k] is not None for k in ("app_commit", "server_commit", "apk_sha256")) and manifest["build"]["candidate_gate_passed"] is True, "MAIN_CANDIDATE_REQUIRED")
        require(all(manifest["device"][k] is not None for k in ("kind", "model", "android_release", "api_level")), "MAIN_DEVICE_REQUIRED")
        require(all(obs[k] is not None for k in ("start_utc", "end_utc", "planned_window_seconds", "actual_duration_ms")), "MAIN_WINDOW_REQUIRED")
    if manifest["clock"]["controlled"]:
        require(all(len(manifest["clock"][k]) >= 3 for k in ("before_samples", "after_samples")) and all(manifest["clock"][k] is not None for k in ("method_code", "client_clock", "offset_before_ms", "offset_after_ms", "uncertainty_before_ms", "uncertainty_after_ms")), "CLOCK_EVIDENCE_REQUIRED")
    return manifest


def validate_event(raw):
    require(isinstance(raw, dict) and all(k in raw for k in FIELDS), "EVENT_FIELDS_MISSING")
    e = {key: raw[key] for key in FIELDS}
    require(e["schema_version"] == "2.0.0", "EVENT_VERSION_UNSUPPORTED")
    require(uuid_string(e["event_id"], v4=True), "EVENT_ID_INVALID")
    for key in ("run_id", "device_alias"):
        require(matches(ID, e[key]), "EVENT_ID_FIELD_INVALID")
    for key in ("request_id", "update_id", "send_attempt_id", "boot_session_id"):
        require(e[key] is None or matches(ID, e[key]), "EVENT_CORRELATION_INVALID")
    for key in ("work_id", "network_call_id"):
        require(e[key] is None or uuid_string(e[key]), "EVENT_UUID_INVALID")
    for key in ("elapsed_realtime_ms", "data_version", "cached_version", "version_hint", "work_attempt"):
        require(e[key] is None or uint(e[key]), "EVENT_INTEGER_INVALID")
    require(utc(e["timestamp_utc"]), "EVENT_TIMESTAMP_INVALID")
    require(e["mode"] in MODES, "EVENT_MODE_INVALID")
    require(isinstance(e["signal_ids"], list) and all(matches(ID, x) for x in e["signal_ids"]) and len(set(e["signal_ids"])) == len(e["signal_ids"]), "SIGNAL_IDS_INVALID")
    require(e["message_id"] is None or isinstance(e["message_id"], str) and 1 <= len(e["message_id"]) <= 512, "MESSAGE_ID_INVALID")
    require(e["ttl_ms"] is None or uint(e["ttl_ms"], 2419200000), "EVENT_TTL_INVALID")
    require(e["http_status"] is None or type(e["http_status"]) is int and 100 <= e["http_status"] <= 599, "HTTP_STATUS_INVALID")
    require(e["reason"] is None or matches(CODE, e["reason"]), "REASON_INVALID")
    require(e["provider_code"] is None or matches(CODE + r"|messaging/[a-z][a-z0-9-]{0,63}", e["provider_code"]), "PROVIDER_CODE_INVALID")
    require(isinstance(e["event_type"], str) and e["event_type"] in EVENTS, "EVENT_TYPE_UNSUPPORTED")
    origin, sources, outcomes = EVENTS[e["event_type"]]
    require(e["origin"] == origin and e["source"] in sources and e["outcome"] in outcomes, "EVENT_SEMANTICS_INVALID")
    require(e["outcome"] not in {"failure", "rejected", "unknown", "retry", "skipped", "stale"} or e["reason"] is not None, "EVENT_REASON_REQUIRED")
    if origin == "SERVER":
        require(e["elapsed_realtime_ms"] is None and e["boot_session_id"] is None, "SERVER_CLOCK_INVALID")
    else:
        require(uint(e["elapsed_realtime_ms"]), "ANDROID_CLOCK_REQUIRED")
    kind = e["event_type"]
    if kind not in {"push_received", "trigger_rejected"}:
        require(not (e["source"] == "PERIODIC" and e["mode"] == "PUSH" or e["source"] == "PUSH" and e["mode"] == "PERIODIC"), "SOURCE_DISABLED")
    if kind == "server_updated":
        require(e["update_id"] is not None and e["data_version"] is not None, "UPDATE_FIELDS_REQUIRED")
    if kind in {"push_send_accepted", "push_send_rejected", "push_send_unknown", "push_received"}:
        require(len(e["signal_ids"]) == 1, "ONE_SIGNAL_REQUIRED")
    if kind in {"push_send_accepted", "push_send_rejected", "push_send_unknown"}:
        require(e["send_attempt_id"] is not None and e["ttl_ms"] is not None, "SEND_FIELDS_REQUIRED")
    if kind == "push_send_accepted":
        require(e["message_id"] is not None and e["data_version"] is not None, "ACCEPTED_FIELDS_REQUIRED")
    if kind == "push_received":
        require(e["data_version"] is None, "RECEIPT_NOT_DATA")
    if kind in {"push_send_failed_local", "push_send_skipped"}:
        require(e["send_attempt_id"] is None and e["message_id"] is None, "UNSENT_HAS_PROVIDER_ID")
    if kind == "push_send_failed_local":
        require(e["provider_code"] is None and e["http_status"] is None and len(e["signal_ids"]) <= 1, "LOCAL_FAILURE_FIELDS_INVALID")
    if kind == "push_send_skipped":
        require(e["reason"] == "FAULT_INJECTION_SKIP" and e["data_version"] is not None, "SKIP_FIELDS_INVALID")
    if kind == "periodic_registered":
        require(e["work_id"] is not None and e["request_id"] is None, "PERIODIC_FIELDS_INVALID")
    work_events = {"work_started", "snapshot_fetch_started", "snapshot_fetch_completed", "snapshot_applied", "snapshot_unchanged", "snapshot_stale", "sync_retrying", "sync_failed"}
    if kind in work_events or kind == "work_enqueued":
        require(e["request_id"] is not None and e["work_id"] is not None, "WORK_IDS_REQUIRED")
    if kind in work_events:
        require(e["work_attempt"] is not None, "WORK_ATTEMPT_REQUIRED")
    if kind in {"work_started", "snapshot_fetch_started"}:
        require(e["data_version"] is None, "START_NOT_DATA")
    if kind in {"snapshot_fetch_started", "snapshot_fetch_completed"}:
        require(e["network_call_id"] is not None, "FETCH_ID_REQUIRED")
    else:
        require(e["network_call_id"] is None, "FETCH_ID_OUTSIDE_FETCH")
    if kind == "snapshot_fetch_completed":
        if e["outcome"] == "success":
            require(e["http_status"] == 200 and e["data_version"] is not None, "FETCH_SUCCESS_INVALID")
        elif e["outcome"] == "not_modified":
            require(e["http_status"] == 304 and e["data_version"] is None, "FETCH_304_INVALID")
    if kind == "snapshot_applied":
        require(e["data_version"] is not None and e["data_version"] == e["cached_version"], "APPLIED_VERSION_INVALID")
    if kind == "snapshot_unchanged":
        require(e["cached_version"] is not None and e["data_version"] in {None, e["cached_version"]}, "UNCHANGED_VERSION_INVALID")
    if kind == "snapshot_stale":
        require(e["data_version"] is not None and e["cached_version"] is not None and e["data_version"] < e["cached_version"] and e["reason"] == "VERSION_STALE", "STALE_VERSION_INVALID")
    return e


def select_events(sources, manifest, fixture):
    selected, seen, reports = [], {}, []
    for origin, text in sources:
        report = {"origin": origin, "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "lines": 0, "selected": 0, "other_run_or_device": 0, "duplicates": 0, "extra_fields_omitted": 0}
        for line in text.splitlines():
            report["lines"] += 1
            require(bool(line.strip()), "BLANK_JSONL_LINE")
            raw = parse_json(line)
            require(isinstance(raw, dict) and "run_id" in raw and "device_alias" in raw, "EVENT_ROUTING_MISSING")
            if raw["run_id"] != manifest["run_id"] or raw["device_alias"] != manifest["device_alias"]:
                report["other_run_or_device"] += 1
                continue
            require("fixture" not in raw or type(raw["fixture"]) is bool, "FIXTURE_MARKER_INVALID")
            require(fixture or raw.get("fixture") is not True, "FIXTURE_INPUT_FOR_OBSERVED")
            e = validate_event(raw)
            require(fixture or e["message_id"] is None or not e["message_id"].startswith("<fixture"), "FIXTURE_MESSAGE_ID_FOR_OBSERVED")
            require(e["origin"] == origin and e["mode"] == manifest["mode"], "SOURCE_MANIFEST_MISMATCH")
            report["extra_fields_omitted"] += len(set(raw) - set(FIELDS))
            if e["event_id"] in seen:
                require(seen[e["event_id"]] == e, "CONFLICTING_EVENT_ID")
                report["duplicates"] += 1
            else:
                seen[e["event_id"]] = e
                selected.append(e)
                report["selected"] += 1
        reports.append(report)
    require(manifest["execution_status"] != "NOT_RUN" or fixture or not selected, "NOT_RUN_HAS_EVENTS")
    return selected, reports


def capture_adb(adb, serial, package, alias, run_id):
    """Read-only contract for the Android producer; never raw logcat fallback."""
    try:
        result = subprocess.run([adb, "-s", serial, "exec-out", "run-as", package, "cat", "files/experiment-events.jsonl"], capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        raise ExportError("ADB_CAPTURE_FAILED") from None
    require(result.returncode == 0, "ADB_CAPTURE_FAILED")
    try:
        text = result.stdout.decode("utf-8")
    except UnicodeError:
        raise ExportError("ADB_UTF8_INVALID") from None
    private = ROOT / "experiments/private/captures" / alias / run_id
    private.mkdir(parents=True, exist_ok=True, mode=0o700)
    capture = Path(tempfile.mkdtemp(prefix="capture-", dir=private))
    target = capture / "android.raw.jsonl"
    with target.open("xb") as handle:
        target.chmod(0o600)
        handle.write(result.stdout)
    return text


def export(args):
    require(matches(ID, args.run_id) and args.run_id not in {".", ".."} and matches(ID, args.device_alias) and args.device_alias not in {".", ".."}, "SELECTION_ID_INVALID")
    deny = []
    if args.deny_values:
        deny = parse_json(read_text(args.deny_values))
        require(isinstance(deny, list) and all(isinstance(x, str) and len(x) >= 4 for x in deny), "DENY_VALUES_INVALID")
    require(args.fixture or args.deny_values is not None, "DENY_VALUES_REQUIRED_FOR_OBSERVED")
    manifest_input = read_text(args.manifest)
    manifest = validate_manifest(parse_json(manifest_input), args.run_id, args.device_alias, args.fixture)
    sources = []
    if args.adb:
        require(args.device_map is not None, "DEVICE_MAP_REQUIRED")
        mapping = parse_json(read_text(args.device_map))
        require(isinstance(mapping, dict) and args.device_alias in mapping and all(isinstance(x, str) and x for x in mapping.values()), "DEVICE_MAP_INVALID")
        deny.extend(mapping.values())
        sources.append(("ANDROID", capture_adb(args.adb, mapping[args.device_alias], manifest["build"]["package_name"], args.device_alias, args.run_id)))
    elif args.android_log:
        sources.append(("ANDROID", read_text(args.android_log)))
    if args.server_log:
        sources.append(("SERVER", read_text(args.server_log)))
    require(sources or manifest["execution_status"] == "NOT_RUN", "SOURCE_REQUIRED")
    events, reports = select_events(sources, manifest, args.fixture)
    report = {"exporter_version": "1.0.0", "data_kind": manifest["data_kind"], "run_id": args.run_id, "device_alias": args.device_alias, "manifest_input_sha256": hashlib.sha256(manifest_input.encode("utf-8")).hexdigest(), "sources": reports, "events_exported": len(events), "ordering": "INPUT_ORDER_NOT_CAUSAL", "analysis_performed": False}
    public_safe([manifest, events, report], deny)
    base = Path(args.output_base) if args.output_base else ROOT / "experiments"
    output = base / ("fixture_exports" if args.fixture else "runs") / args.run_id
    # All parsing/validation/privacy checks finish before creating public artifacts.
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir(exist_ok=False)
    try:
        for name, obj in (("manifest.json", manifest), ("export_report.json", report)):
            (output / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        (output / "events.jsonl").write_text("".join(json.dumps(e, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n" for e in events), encoding="utf-8")
    except (OSError, UnicodeError):
        shutil.rmtree(output)
        raise
    return {"status": "EXPORTED", "data_kind": manifest["data_kind"], "events": len(events)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--device-alias", required=True)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--android-log", help="Canonical UTF-8 JSONL file, not logcat/Room v1")
    source.add_argument("--adb", metavar="ADB_EXECUTABLE", help="Read files/experiment-events.jsonl via run-as")
    parser.add_argument("--device-map", help="Private JSON alias-to-serial mapping; never exported")
    parser.add_argument("--server-log", help="Canonical SERVER JSONL file")
    parser.add_argument("--deny-values", help="Private JSON array of serial/token/credential strings")
    parser.add_argument("--output-base", help="Output base directory; retains fixture_exports/ versus runs/ separation")
    parser.add_argument("--fixture", action="store_true", help="Require FIXTURE/development and export outside runs/")
    args = parser.parse_args(argv)
    try:
        result = export(args)
    except ExportError as error:
        print("ERROR " + str(error), file=sys.stderr)
        return 2
    except (OSError, UnicodeError):
        print("ERROR IO_FAILED_OR_OUTPUT_EXISTS", file=sys.stderr)
        return 2
    except (TypeError, ValueError, KeyError, RecursionError):
        print("ERROR INVALID_INPUT_SHAPE", file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
