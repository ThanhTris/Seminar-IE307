#!/usr/bin/env python3
"""Read pending JobScheduler reasons without instrumentation or target app startup.

Diagnostic tool for debuggable API 36+ images, not an E01 observation runner.
The framework bootstrap uses a hidden API: fail closed if the image rejects it.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

PACKAGE = "com.thanhtris.seminarie307"
NAMESPACE = "androidx.work.systemjobscheduler"
SOURCE = Path(__file__).with_name("android") / "Sem41JobProbe.java"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(sdk, output):
    sdk, output = Path(sdk), Path(output)
    jar = sdk / "platforms/android-37.0/android.jar"
    if not jar.is_file():
        raise RuntimeError("ANDROID_37_PLATFORM_REQUIRED")
    output.mkdir(parents=True, exist_ok=False)
    (output / "classes").mkdir()
    (output / "dex").mkdir()
    for command in [
        ["javac", "--release", "17", "-cp", str(jar), "-d", str(output / "classes"), str(SOURCE)],
        [str(sdk / "build-tools/36.0.0/d8"), "--lib", str(jar), "--min-api", "36",
         "--output", str(output / "dex"), str(output / "classes/Sem41JobProbe.class")],
    ]:
        result = subprocess.run(command, capture_output=True, timeout=60)
        if result.returncode:
            (output / "build-error.private.txt").write_bytes(result.stdout + result.stderr)
            raise RuntimeError("PROBE_BUILD_FAILED")
    result = {"java_source_sha256": sha(SOURCE), "dex_sha256": sha(output / "dex/classes.dex"),
              "framework_bootstrap": "ACTIVITY_THREAD_SYSTEM_MAIN", "minimum_api": 36}
    (output / "build.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def adb_call(adb, serial, *args, data=None):
    try:
        result = subprocess.run([str(adb), "-s", serial, *args], input=data,
                                capture_output=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        raise RuntimeError("JOB_PROBE_ADB_FAILED") from None
    if result.returncode:
        # subprocess exceptions/ADB stderr can contain the private device identifier.
        raise RuntimeError("JOB_PROBE_ADB_FAILED")
    return result.stdout


def remote_directory(dex):
    return "files/sem41-job-probe/" + sha(dex)[:16]


def deploy(adb, serial, dex):
    directory = remote_directory(dex)
    adb_call(adb, serial, "shell", "run-as", PACKAGE, "mkdir", "-p", directory)
    # This content-addressed filename belongs exclusively to this diagnostic tool.
    command = "cat > " + shlex.quote(directory + "/probe.dex")
    adb_call(adb, serial, "shell", "run-as", PACKAGE, "sh", "-c", shlex.quote(command),
             data=Path(dex).read_bytes())
    adb_call(adb, serial, "shell", "run-as", PACKAGE, "chmod", "444", directory + "/probe.dex")
    actual = adb_call(adb, serial, "exec-out", "run-as", PACKAGE, "cat", directory + "/probe.dex")
    if hashlib.sha256(actual).hexdigest() != sha(dex):
        raise RuntimeError("DEPLOYED_DEX_HASH_MISMATCH")
    return {"deployed_dex_sha256": sha(dex)}


def validate(value):
    expected = {"probe_version", "sdk_int", "utc_epoch_ms", "elapsed_realtime_ms", "namespace",
                "package", "read_only", "jobs"}
    if not isinstance(value, dict) or set(value) != expected or value["probe_version"] != "1.0.0":
        raise RuntimeError("JOB_PROBE_SCHEMA_MISMATCH")
    if any(type(value[key]) is not int or value[key] < 0 for key in (
            "sdk_int", "utc_epoch_ms", "elapsed_realtime_ms")) or value["sdk_int"] < 36:
        raise RuntimeError("JOB_PROBE_SCHEMA_MISMATCH")
    if value["package"] != PACKAGE or value["namespace"] != NAMESPACE or value["read_only"] is not True:
        raise RuntimeError("JOB_PROBE_SCOPE_MISMATCH")
    if not isinstance(value["jobs"], list):
        raise RuntimeError("JOB_PROBE_SCHEMA_MISMATCH")
    job_keys = {"job_id", "service", "work_id", "generation", "system_job_is_periodic",
                "minimum_latency_ms", "pending_reasons", "history", "stats", "job_disappeared_during_query"}
    def reason(item):
        if not isinstance(item, dict) or set(item) != {"code", "name"} or type(item["code"]) is not int or not isinstance(item["name"], str) or not re.fullmatch(
                r"(?:PENDING_JOB_REASON_[A-Z_]+|UNKNOWN_-?\d+)", item["name"]):
            raise RuntimeError("JOB_PROBE_REASON_INVALID")
    for job in value["jobs"]:
        if not isinstance(job, dict) or set(job) != job_keys or job["service"] != "androidx.work.impl.background.systemjob.SystemJobService":
            raise RuntimeError("JOB_PROBE_JOB_SCOPE_MISMATCH")
        if type(job["job_id"]) is not int or job["job_id"] < 0 or not isinstance(job["work_id"], str) or not re.fullmatch(
                r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", job["work_id"]):
            raise RuntimeError("JOB_PROBE_WORK_ID_INVALID")
        if any(type(job[key]) is not int or job[key] < 0 for key in ("generation", "minimum_latency_ms")) or any(type(job[key]) is not bool for key in ("system_job_is_periodic", "job_disappeared_during_query")):
            raise RuntimeError("JOB_PROBE_SCHEMA_MISMATCH")
        if not all(isinstance(job[key], list) for key in ("pending_reasons", "history", "stats")):
            raise RuntimeError("JOB_PROBE_SCHEMA_MISMATCH")
        for item in job["pending_reasons"]:
            reason(item)
        for item in job["history"]:
            if not isinstance(item, dict) or set(item) != {"timestamp_ms", "reasons"} or type(item["timestamp_ms"]) is not int or item["timestamp_ms"] < 0 or not isinstance(item["reasons"], list):
                raise RuntimeError("JOB_PROBE_HISTORY_INVALID")
            for entry in item["reasons"]:
                reason(entry)
        for item in job["stats"]:
            if not isinstance(item, dict) or set(item) != {"reason", "duration_ms"} or type(item["duration_ms"]) is not int or item["duration_ms"] < 0:
                raise RuntimeError("JOB_PROBE_STATS_INVALID")
            reason(item["reason"])
    return value


def capture(adb, serial, dex):
    directory = remote_directory(dex)
    command = "CLASSPATH=" + shlex.quote(directory + "/probe.dex") + " app_process /system/bin Sem41JobProbe"
    raw = adb_call(adb, serial, "shell", "run-as", PACKAGE, "sh", "-c", shlex.quote(command))
    try:
        value = validate(json.loads(raw))
    except (ValueError, TypeError, KeyError):
        raise RuntimeError("JOB_PROBE_OUTPUT_INVALID") from None
    value["probe_dex_sha256"] = sha(dex)
    return value


def remove(adb, serial, dex):
    # Remove exactly the deployed file/directory; no recursive removal of app data.
    directory = remote_directory(dex)
    actual = adb_call(adb, serial, "exec-out", "run-as", PACKAGE, "cat", directory + "/probe.dex")
    if hashlib.sha256(actual).hexdigest() != sha(dex):
        raise RuntimeError("DEPLOYED_DEX_HASH_MISMATCH")
    adb_call(adb, serial, "shell", "run-as", PACKAGE, "rm", directory + "/probe.dex")
    adb_call(adb, serial, "shell", "run-as", PACKAGE, "rmdir", directory)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["build", "deploy", "capture", "remove"])
    parser.add_argument("--sdk", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--adb", type=Path)
    parser.add_argument("--device-map", type=Path)
    parser.add_argument("--dex", type=Path)
    args = parser.parse_args()
    if args.action == "build":
        if not args.sdk or not args.output:
            parser.error("build requires --sdk and a new --output directory")
        print(json.dumps(build(args.sdk, args.output)))
        return
    if not all([args.adb, args.device_map, args.dex]):
        parser.error("device actions require --adb, --device-map and --dex")
    serial = json.loads(args.device_map.read_text())["emulator-main"]
    if args.action == "deploy":
        print(json.dumps(deploy(args.adb, serial, args.dex)))
    elif args.action == "capture":
        if not args.output or args.output.exists():
            parser.error("capture requires a new --output file")
        args.output.write_text(json.dumps(capture(args.adb, serial, args.dex), indent=2) + "\n")
        print(json.dumps({"status": "CAPTURED", "device_alias": "emulator-main"}))
    else:
        remove(args.adb, serial, args.dex)
        print(json.dumps({"status": "REMOVED", "device_alias": "emulator-main"}))


if __name__ == "__main__":
    main()
