"""SEM-41 baseline verification. Never changes captured cache or server data."""

import hashlib
import json
from pathlib import Path
import sqlite3


def payload_digest(items):
    normalized = sorted(items, key=lambda item: item["id"])
    return hashlib.sha256(json.dumps(normalized, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode()).hexdigest()


def compare_capture(database, snapshot, epoch_alias, source):
    connection = sqlite3.connect(str(database))
    connection.row_factory = sqlite3.Row
    try:
        value = connection.execute("SELECT value FROM sync_metadata WHERE key='cachedVersion'").fetchone()
        cached = int(value[0]) if value and value[0] is not None else None
        items = [dict(row) for row in connection.execute(
            "SELECT id,title,body,version FROM bulletin_items ORDER BY id")]
    finally:
        connection.close()
    cached_hash, server_hash = payload_digest(items), payload_digest(snapshot["items"])
    equal = cached == snapshot["version"] and cached_hash == server_hash
    return {"status": "PASS" if equal else "FAIL",
            "reason": "BASELINE_MATCH" if equal else "BASELINE_VERSION_MISMATCH" if cached != snapshot["version"] else "BASELINE_PAYLOAD_MISMATCH",
            "cache_version": cached, "server_version": snapshot["version"],
            "cache_item_count": len(items), "server_item_count": len(snapshot["items"]),
            "cache_items_sha256": cached_hash, "server_items_sha256": server_hash,
            "server_store_epoch": epoch_alias, "source": source,
            "normalization": "SORT_ID_JSON_SORT_KEYS_COMPACT_UTF8"}


def historical_baseline(folder, record):
    """Use the retained idempotency ledger, not today's snapshot for an old run."""
    folder = Path(folder)
    if record.get("target_version") is None:
        path = folder / "baseline-content-proof.json"
        return json.loads(path.read_text()) if path.exists() else {
            "status": "NOT_ASSESSED", "reason": "MEASUREMENT_NOT_STARTED"}
    try:
        store = folder.parent / "store"
        state = json.loads((store / "state.json").read_text())
        version = record["target_version"] - 1
        snapshots = [entry["response"] for entry in state["ledger"].values()
                     if entry["response"]["version"] == version]
        if len(snapshots) != 1:
            return {"status": "NOT_ASSESSED", "reason": "BASELINE_LEDGER_PROOF_UNAVAILABLE"}
        return compare_capture(folder / "setup-db/seminar_bulletin.db", snapshots[0],
                               store.resolve().parent.name, "CAPTURED_SQLITE_AND_RETAINED_LEDGER")
    except (OSError, ValueError, KeyError, sqlite3.Error):
        return {"status": "NOT_ASSESSED", "reason": "BASELINE_PROOF_UNAVAILABLE"}


def attach_store(folder, cached_version, retained_store=None):
    """Keep ETags bound to their original payload/ledger across batch restarts."""
    target = Path(folder) / "store"
    if retained_store is None:
        if cached_version != 0:
            raise RuntimeError("RETAINED_STORE_REQUIRED_FOR_EXISTING_CACHE")
        return target
    retained_store = Path(retained_store).resolve()
    state = json.loads((retained_store / "state.json").read_text())
    if state["snapshot"]["version"] < cached_version:
        raise RuntimeError("RETAINED_SERVER_BEHIND_CACHE")
    target.symlink_to(retained_store, target_is_directory=True)
    return target
