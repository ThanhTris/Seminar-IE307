#!/usr/bin/env python3
"""Render and check all six artifacts against committed canonical SHA-256."""

import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import subprocess
import sys

from render_results import HERE, ROOT, check_source_bytes, load

ARTIFACTS = ("pilot_inventory.csv", "main_coverage.csv", "pilot_inventory.svg",
             "main_coverage.svg", "pilot_inventory.png", "main_coverage.png")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-crlf", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        raise ValueError("OUTPUT_MUST_BE_EMPTY")
    index = load(HERE / "INPUTS.json")
    config = subprocess.run(["git", "config", "--get", "core.autocrlf"], cwd=ROOT,
                            capture_output=True, text=True, check=False).stdout.strip()
    normalized = 0
    for ref in index["sources"]:
        raw = (ROOT / ref["path"]).read_bytes()
        blob = subprocess.check_output(["git", "show", index["source_revision"] + ":" + ref["path"]], cwd=ROOT)
        check_source_bytes(raw, blob, ref["sha256"], ref["path"])
        normalized += raw != blob
    if args.require_crlf and (config != "true" or not normalized):
        raise ValueError("CRLF_CHECKOUT_NOT_EXERCISED")
    subprocess.run([sys.executable, "-B", str(HERE / "render_results.py"),
                    "--output", str(args.output)], cwd=ROOT, check=True)
    expected = {entry["path"]: entry["sha256"] for entry in
                load(ROOT / "docs/evidence/SEM-48/VERIFICATION.json")["output_files"]}
    results = []
    for name in ARTIFACTS:
        path = "slides/inputs/results/" + name
        blob = subprocess.check_output(["git", "show", "HEAD:" + path], cwd=ROOT)
        actual = (args.output / name).read_bytes()
        if digest(blob) != expected[path] or digest(actual) != expected[path]:
            raise ValueError("ARTIFACT_SHA256_MISMATCH: " + name +
                             " generated=" + digest(actual) + " expected=" + expected[path])
        if name.endswith((".csv", ".svg")) and b"\r\n" in actual:
            raise ValueError("OUTPUT_MUST_USE_LF: " + name)
        results.append({"file": name, "sha256": digest(actual), "matches_committed_sha256": True})
    code_paths = ["slides/inputs/results/" + path for path in
                  ("render_results.py", "verify_reproduction.py", "tests/test_source_validation.py")]
    code_hashes = {path: digest(subprocess.check_output(["git", "show", "HEAD:" + path], cwd=ROOT))
                   for path in code_paths}
    report = {"scope": "SEM48_CROSS_PLATFORM_REPRODUCTION_NOT_EXPERIMENTAL_DATA",
              "platform": platform.system(), "python_version": platform.python_version(),
              "tested_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "pull_request_head": os.environ.get("SEM48_PR_HEAD"), "code_sha256": code_hashes,
              "source_revision": index["source_revision"], "core_autocrlf": config,
              "source_files_checked": len(index["sources"]), "crlf_normalized_source_files": normalized,
              "artifacts": results, "outcome": "PASS"}
    (args.output / "reproduction-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
