#!/usr/bin/env python3
"""SEM-45: offline analysis of canonical SEM-24 exports. Python 3.9+."""

import hashlib
from pathlib import Path

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
