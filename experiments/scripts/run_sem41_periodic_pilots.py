#!/usr/bin/env python3
"""Observe Firebase-independent SEM-41 pilots sequentially. Python 3.9+, ADB, Node.

Uses the installed, hash-verified development APK. All outputs remain private until
review/export. This runner never produces phase=main or forces WorkManager jobs.
"""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import signal
import socket
import sqlite3
import subprocess
import tarfile
import time
import urllib.request
import uuid
import xml.etree.ElementTree as ET
import os

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "com.thanhtris.seminarie307"
CONTROL = PACKAGE + ".experiments.PeriodicPilotControl#control"
RUNNER = PACKAGE + ".test/androidx.test.runner.AndroidJUnitRunner"


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


class PilotBatch:
    def __init__(self, args):
        self.args = args
        self.serial = json.loads(args.device_map.read_text())["emulator-main"]
        self.identity = json.loads(args.preflight.read_text())["build_check"]
        self.folder = args.private_output.resolve()
        self.folder.mkdir(parents=True, exist_ok=False)
        self.folder.chmod(0o700)
        self.server = None
        self.current = None
        self.network_changed = False
        self.idle_changed = False
        self.baseline = {}

    def adb(self, *args, timeout=60):
        result = subprocess.run([str(self.args.adb), "-s", self.serial, *args],
                                capture_output=True, timeout=timeout)
        if result.returncode:
            raise RuntimeError("ADB_COMMAND_FAILED")
        return result.stdout.decode("utf-8")

    def shell(self, *args, timeout=60):
        return self.adb("shell", *args, timeout=timeout).strip()

    def capture(self, name, *args):
        text = self.shell(*args)
        (self.current / (name + ".txt")).write_text(text + "\n")
        return text

    def checkpoint(self, label):
        idle = self.capture(label + "-idle", "dumpsys", "deviceidle")
        activity = self.capture(label + "-activity", "dumpsys", "activity", "activities")
        package = self.capture(label + "-package", "dumpsys", "package", PACKAGE)
        self.capture(label + "-jobs", "dumpsys", "jobscheduler", PACKAGE)
        self.capture(label + "-battery", "dumpsys", "battery")
        state = {"utc": utc(), "elapsed_realtime_ms": self.elapsed(),
                 "idle": re.search(r"\bmState=(\w+)", idle).group(1),
                 "network_connected": "mNetworkConnected=true" in idle,
                 "screen_on": "mScreenOn=true" in idle,
                 "package_stopped": "stopped=true" in package,
                 "app_resumed": any(PACKAGE in line for line in activity.splitlines()
                                    if "topResumedActivity=" in line)}
        write_json(self.current / (label + "-checkpoint.json"), state)
        if self.baseline.get("boot_hash") and hashlib.sha256(self.shell("cat", "/proc/sys/kernel/random/boot_id").encode()).hexdigest() != self.baseline["boot_hash"]:
            raise RuntimeError("DEVICE_REBOOTED_DURING_BATCH")
        return state

    def elapsed(self):
        return round(float(self.shell("cat", "/proc/uptime").split()[0]) * 1000)

    def database(self, label):
        destination = self.current / label
        destination.mkdir(exist_ok=False)
        result = subprocess.run([str(self.args.adb), "-s", self.serial, "exec-out", "run-as",
                                 PACKAGE, "tar", "-cf", "-", "databases"], capture_output=True, timeout=60)
        if result.returncode:
            raise RuntimeError("DATABASE_CAPTURE_FAILED")
        (destination / "databases.tar").write_bytes(result.stdout)
        with tarfile.open(fileobj=io.BytesIO(result.stdout)) as archive:
            for member in archive.getmembers():
                name = Path(member.name).name
                if member.isfile() and name in {"seminar_bulletin.db", "seminar_bulletin.db-wal", "seminar_bulletin.db-shm"}:
                    (destination / name).write_bytes(archive.extractfile(member).read())
        connection = sqlite3.connect(str(destination / "seminar_bulletin.db"))
        connection.row_factory = sqlite3.Row
        metadata = dict(connection.execute("SELECT key,value FROM sync_metadata WHERE key IN ('cachedVersion','mode','activeRunId','deviceAlias','fcmTokenStatus')").fetchall())
        rows = [dict(row) for row in connection.execute(
            "SELECT * FROM timeline_events WHERE runId=? ORDER BY occurredAtEpochMillis,eventId",
            (self.record["run_id"],))]
        connection.close()
        write_json(self.current / (label + "-summary.json"), {"metadata": metadata, "events": rows})
        return metadata, rows

    def ui(self, label):
        self.shell("uiautomator", "dump", "/sdcard/sem41-pilot-ui.xml", timeout=40)
        raw = self.adb("exec-out", "cat", "/sdcard/sem41-pilot-ui.xml")
        (self.current / (label + "-ui.xml")).write_text(raw)
        return ET.fromstring(raw)

    def tap(self, node):
        left, top, right, bottom = map(int, re.findall(r"\d+", node.get("bounds")))
        if right <= left or bottom <= top:
            raise RuntimeError("UI_TARGET_NOT_VISIBLE")
        self.shell("input", "tap", str((left + right) // 2), str((top + bottom) // 2))

    def configure(self, mode, run):
        self.shell("input", "keyevent", "KEYCODE_WAKEUP")
        self.shell("am", "start", "-W", "-n", PACKAGE + "/.MainActivity")
        ui = self.ui("before-configure")
        fields = [node for node in ui.iter("node") if node.get("class") == "android.widget.EditText"]
        if len(fields) != 2:
            raise RuntimeError("RUN_CONFIGURATION_FIELDS_UNAVAILABLE")
        for node, value in zip(fields, [run, "emulator-main"]):
            self.tap(node)
            self.shell("input", "keyevent", "KEYCODE_MOVE_END")
            self.shell("input", "keyevent", "--delay", "0", *(["KEYCODE_DEL"] * 140))
            self.shell("input", "text", value)
            self.shell("input", "keyevent", "KEYCODE_BACK")
        ui = self.ui("filled-configure")
        filled = [node.get("text") for node in ui.iter("node") if node.get("class") == "android.widget.EditText"]
        if filled != [run, "emulator-main"]:
            raise RuntimeError("RUN_CONFIGURATION_TEXT_NOT_CONFIRMED")
        buttons = [node for node in ui.iter("node") if node.get("text") == mode
                   and int(re.findall(r"\d+", node.get("bounds"))[1]) > 900]
        if len(buttons) != 1:
            raise RuntimeError("MODE_BUTTON_UNAVAILABLE")
        self.tap(buttons[0])
        self.ui("after-configure")
        self.shell("input", "keyevent", "KEYCODE_HOME")
        metadata, rows = self.database("setup-db")
        if metadata.get("mode") != mode or metadata.get("activeRunId") != run or metadata.get("deviceAlias") != "emulator-main":
            raise RuntimeError("MODE_CONFIGURATION_NOT_ACCEPTED")
        registered = [row for row in rows if row["eventType"] == "periodic_registered"]
        if len(registered) != 1 or not registered[0]["workId"]:
            raise RuntimeError("PERIODIC_REGISTRATION_NOT_CONFIRMED")
        self.record["work_id"] = registered[0]["workId"]
        self.record["cached_version_before"] = int(metadata["cachedVersion"]) if metadata.get("cachedVersion") else None
        checkpoint = self.checkpoint("background")
        if checkpoint["app_resumed"] or checkpoint["package_stopped"] or not checkpoint["network_connected"]:
            raise RuntimeError("BACKGROUND_BASELINE_INVALID")

    def instrument(self, action):
        run = self.record["run_id"]
        output = self.adb("shell", "am", "instrument", "-w", "-r", "-e", "class", CONTROL,
                          "-e", "sem29_action", action, "-e", "sem29_run_id", run, RUNNER, timeout=180)
        (self.current / (action + "-instrument.txt")).write_text(output)
        if "OK (1 test)" not in output:
            raise RuntimeError("PILOT_CONTROL_FAILED")
        if action == "export-v2":
            for name in ["events-v2.jsonl", "events-v2-export-report.json", "export-v2-events-legacy.jsonl", "export-v2-state.json"]:
                raw = self.adb("exec-out", "run-as", PACKAGE, "cat", "files/sem29/" + run + "/" + name)
                (self.current / name).write_text(raw)

    def persist(self, stage):
        self.record["stage"] = stage
        self.record["last_updated_utc"] = utc()
        write_json(self.current / "observation.json", self.record)
        write_json(self.folder / "status.json", {"run_id": self.record["run_id"], "case_id": self.record["case_id"],
                   "stage": stage, "utc": utc(), "execution_status": self.record["execution_status"]})
        print(json.dumps({"case": self.record["case_id"], "repetition": self.record["repetition"], "stage": stage, "utc": utc()}), flush=True)

    def observe(self, seconds, stage, idle_required=None):
        self.persist(stage)
        deadline = time.monotonic() + seconds
        last_checkpoint = time.monotonic()
        while time.monotonic() < deadline:
            time.sleep(min(30, max(0, deadline - time.monotonic())))
            if time.monotonic() - last_checkpoint >= 300:
                state = self.checkpoint(stage + "-" + str(self.elapsed()))
                if state["app_resumed"] or state["package_stopped"]:
                    raise RuntimeError("APP_STATE_CHANGED_DURING_WINDOW")
                if idle_required is not None and state["idle"] != idle_required:
                    raise RuntimeError("IDLE_STATE_CHANGED_DURING_WINDOW")
                last_checkpoint = time.monotonic()
            write_json(self.folder / "heartbeat.json", {"run_id": self.record["run_id"], "stage": stage,
                       "utc": utc(), "remaining_seconds": max(0, round(deadline - time.monotonic()))})
        if idle_required is not None:
            state = self.checkpoint(stage + "-end")
            if state["idle"] != idle_required:
                raise RuntimeError("IDLE_STATE_INVALID_AT_WINDOW_END")

    def update(self, mode, skip=False):
        run = self.record["run_id"]
        command = ["node", "server/bin/update-cli.js", "--update-id", "update-" + run, "--run", run,
                   "--mode", mode, "--device", "emulator-main", "--title", "SEM-41 pilot target",
                   "--body", "Firebase-independent periodic observation"]
        if skip:
            command += ["--skip-push", "--events", str(self.folder / "skip-events.jsonl")]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=25)
        (self.current / "update-output.json").write_bytes(result.stdout)
        if result.returncode:
            raise RuntimeError("SERVER_UPDATE_NOT_CONFIRMED")
        response = json.loads(result.stdout)
        self.record["target_version"] = response["version"]
        self.record["update_id"] = response["update_id"]
        self.record["update_received_utc"] = utc()
        server_events_path = self.folder / "store/events.jsonl"
        (self.current / "server-events.jsonl").write_bytes(server_events_path.read_bytes())
        event = next(event for event in map(json.loads, server_events_path.read_text().splitlines()) if event["update_id"] == response["update_id"])
        self.record["update_utc"] = event["timestamp_utc"]
        if skip:
            (self.current / "skip-events.jsonl").write_bytes((self.folder / "skip-events.jsonl").read_bytes())
            self.record["skip_confirmed"] = response.get("push") == "skipped"
            if not self.record["skip_confirmed"]:
                raise RuntimeError("SKIP_EVENT_NOT_CONFIRMED")

    def restore_network(self):
        self.shell("cmd", "connectivity", "airplane-mode", "disable")
        self.shell("cmd", "phone", "data", "enable" if self.baseline["mobile_data"] == "1" else "disable")
        self.shell("cmd", "wifi", "set-wifi-enabled", "enabled" if self.baseline["wifi_on"] == "1" else "disabled")
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            if self.reachable():
                self.network_changed = False
                return
            time.sleep(2)
        raise RuntimeError("NETWORK_RESTORE_NOT_CONFIRMED")

    def reachable(self):
        result = subprocess.run([str(self.args.adb), "-s", self.serial, "shell",
            "printf 'GET /health HTTP/1.0\\r\\nHost: localhost\\r\\n\\r\\n' | nc -w 4 10.0.2.2 3000"],
            capture_output=True, timeout=10)
        return result.returncode == 0 and b"200 OK" in result.stdout

    def restore_idle(self):
        self.shell("dumpsys", "deviceidle", "unforce")
        self.shell("dumpsys", "battery", "reset")
        self.shell("input", "keyevent", "KEYCODE_WAKEUP")
        if self.shell("dumpsys", "deviceidle", "get", "deep") == "IDLE":
            raise RuntimeError("IDLE_RESTORE_NOT_CONFIRMED")
        self.idle_changed = False

    def run_one(self, case, repetition):
        day = datetime.now(timezone(timedelta(hours=7))).strftime("%Y%m%d")
        run = "run-sem41-pilot-" + case.lower() + "-" + str(repetition) + "-" + day + "-" + uuid.uuid4().hex[:6]
        self.current = self.folder / run
        self.current.mkdir()
        self.record = {"run_id": run, "case_id": case, "repetition": repetition, "run_phase": "pilot",
                       "execution_status": "RUNNING", "outcome": "UNKNOWN", "candidate_gate_passed": False,
                       "app_source_commit": self.identity["app_source_commit"], "server_source_commit": self.identity["server_source_commit"],
                       "apk_sha256": self.identity["apk_artifacts"]["application_apk"]["sha256"],
                       "reason_codes": [], "mode": "HYBRID" if case == "E06" else "PERIODIC"}
        self.persist("SETUP")
        try:
            self.configure(self.record["mode"], run)
            self.record.update(start_utc=utc(), start_elapsed_realtime_ms=self.elapsed())
            if case == "E01":
                self.update("PERIODIC")
                self.observe(5400, "NATURAL_PERIODIC", "ACTIVE")
            elif case == "E03":
                self.observe(300, "BASELINE", "ACTIVE")
                self.idle_changed = True
                self.shell("dumpsys", "battery", "unplug")
                self.shell("input", "keyevent", "KEYCODE_SLEEP")
                self.shell("dumpsys", "deviceidle", "force-idle")
                if self.shell("dumpsys", "deviceidle", "get", "deep") != "IDLE":
                    raise RuntimeError("DOZE_NOT_CONFIRMED")
                self.record.update(idle_start_utc=utc(), idle_start_elapsed_realtime_ms=self.elapsed())
                self.update("PERIODIC")
                self.observe(1200, "CONFIRMED_DOZE", "IDLE")
                self.restore_idle()
                self.record.update(idle_exit_utc=utc(), idle_exit_elapsed_realtime_ms=self.elapsed())
                self.observe(600, "POST_DOZE", "ACTIVE")
            elif case == "E04":
                self.network_changed = True
                self.shell("cmd", "connectivity", "airplane-mode", "enable")
                self.shell("cmd", "phone", "data", "disable")
                self.shell("cmd", "wifi", "set-wifi-enabled", "disabled")
                time.sleep(5)
                network = self.capture("offline-network", "dumpsys", "connectivity")
                if self.reachable() or not re.search(r"Active default network:\s*(?:none|null|\(none\))", network, re.I):
                    raise RuntimeError("GUEST_OFFLINE_NOT_CONFIRMED")
                self.record.update(offline_utc=utc(), offline_elapsed_realtime_ms=self.elapsed())
                self.update("PERIODIC")
                self.observe(120, "CONFIRMED_OFFLINE")
                self.restore_network()
                self.record.update(reconnect_utc=utc(), reconnect_elapsed_realtime_ms=self.elapsed())
                self.observe(1800, "POST_RECONNECT", "ACTIVE")
            elif case == "E06":
                self.update("HYBRID", skip=True)
                self.observe(2700, "CONTROLLED_SKIP_PERIODIC_RECOVERY", "ACTIVE")
            self.record.update(end_utc=utc(), end_elapsed_realtime_ms=self.elapsed(), execution_status="COMPLETED")
            self.checkpoint("window-end")
            metadata, rows = self.database("window-end-db")
            target = self.record.get("target_version")
            within = [row for row in rows if self.record["start_elapsed_realtime_ms"] <= row["elapsedRealtimeMillis"] <= self.record["end_elapsed_realtime_ms"]]
            applied = [row for row in within if row["eventType"] == "snapshot_applied" and row["version"] == target and row["source"] == "PERIODIC"]
            self.record["cached_version_after"] = int(metadata["cachedVersion"]) if metadata.get("cachedVersion") else None
            self.record["outcome"] = "SUCCESS" if applied else "TIMEOUT"
            setup_ids = {row["requestId"] for row in rows if row["eventType"] == "work_started" and row["elapsedRealtimeMillis"] < self.record["start_elapsed_realtime_ms"]}
            self.record["new_periodic_cycles"] = len({row["requestId"] for row in within if row["eventType"] == "work_started"} - setup_ids)
            if not applied:
                self.record["reason_codes"].append("TARGET_NOT_APPLIED_IN_WINDOW")
            if case == "E01" and self.record["new_periodic_cycles"] < 3:
                self.record["reason_codes"].append("NATURAL_CYCLE_TARGET_NOT_MET")
        except Exception as error:
            self.record.update(execution_status="ABORTED", outcome="FAILURE", end_utc=utc(), end_elapsed_realtime_ms=self.elapsed())
            self.record["reason_codes"].append(str(error) if isinstance(error, RuntimeError) else type(error).__name__.upper())
            raise
        finally:
            self.persist("CLEANUP")
            if self.idle_changed:
                self.restore_idle()
            if self.network_changed:
                self.restore_network()
            self.instrument("cancel")
            self.instrument("export-v2")
            self.shell("am", "start", "-W", "-n", PACKAGE + "/.MainActivity")
            self.shell("input", "keyevent", "KEYCODE_HOME")
            self.checkpoint("cleanup")
            self.record["cleanup_passed"] = True
            self.persist("FINISHED")

    def run(self):
        path = self.adb("shell", "pm", "path", PACKAGE).strip().removeprefix("package:")
        installed = subprocess.check_output([str(self.args.adb), "-s", self.serial, "exec-out", "cat", path], timeout=60)
        if hashlib.sha256(installed).hexdigest() != self.identity["apk_artifacts"]["application_apk"]["sha256"]:
            raise RuntimeError("INSTALLED_APK_HASH_MISMATCH")
        self.baseline = {key: self.shell("settings", "get", "global", key) for key in ["wifi_on", "mobile_data", "airplane_mode_on"]}
        self.baseline["boot_hash"] = hashlib.sha256(self.shell("cat", "/proc/sys/kernel/random/boot_id").encode()).hexdigest()
        if self.baseline["airplane_mode_on"] != "0" or self.shell("dumpsys", "deviceidle", "get", "deep") != "ACTIVE":
            raise RuntimeError("INITIAL_DEVICE_BASELINE_INVALID")
        write_json(self.folder / "baseline.json", self.baseline)
        self.current = self.folder / "preflight"
        self.current.mkdir()
        self.record = {"run_id": "sem41-pilot-setup"}
        metadata, _ = self.database("baseline-db")
        cached = int(metadata.get("cachedVersion") or 0)
        if cached > 90:
            raise RuntimeError("CACHE_TOO_HIGH_FOR_DEDICATED_STORE_CAPACITY")
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 3000))
        server_log = (self.folder / "server-output.txt").open("wb")
        environment = dict(os.environ, PORT="3000", HOST="127.0.0.1", STORE_DIR=str(self.folder / "store"))
        self.server = subprocess.Popen(["node", "dist/server.js"], cwd=ROOT / "server", env=environment, stdout=server_log, stderr=subprocess.STDOUT)
        try:
            for _ in range(20):
                if self.server.poll() is not None:
                    raise RuntimeError("DEDICATED_SERVER_START_FAILED")
                try:
                    with urllib.request.urlopen("http://127.0.0.1:3000/health", timeout=2) as response:
                        if response.status == 200:
                            break
                except OSError:
                    time.sleep(0.5)
            else:
                raise RuntimeError("SERVER_HEALTH_NOT_CONFIRMED")
            # Bring the dedicated store to the existing cache baseline before measuring.
            for index in range(1, cached + 1):
                result = subprocess.run(["node", "server/bin/update-cli.js", "--update-id", "sem41-pilot-seed-" + str(index),
                    "--run", "sem41-pilot-setup", "--mode", "PERIODIC", "--device", "emulator-main",
                    "--title", "SEM-41 pilot baseline", "--body", "Dedicated store baseline"], cwd=ROOT, capture_output=True, timeout=20)
                if result.returncode:
                    raise RuntimeError("BASELINE_UPDATE_FAILED")
            for case, count in [("E01", 1), ("E03", 2), ("E04", 3), ("E06", 2)]:
                for repetition in range(1, count + 1):
                    try:
                        self.run_one(case, repetition)
                    except RuntimeError as error:
                        if str(error) == "GUEST_OFFLINE_NOT_CONFIRMED":
                            write_json(self.folder / "e04-blocker.json", {"case_id": "E04", "execution_status": "NOT_RUN",
                                       "reason": str(error), "remaining_repetitions": count - repetition})
                            break
                        raise
            write_json(self.folder / "batch-complete.json", {"utc": utc(), "status": "COMPLETED_WITH_RECORDED_OUTCOMES", "phase": "pilot"})
        finally:
            self.server.terminate()
            self.server.wait(timeout=20)
            server_log.close()
            write_json(self.folder / "server-cleanup.json", {"utc": utc(), "stopped": True,
                       "store_lock_released": not (self.folder / "store/state.json.lock").exists()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adb", type=Path, required=True)
    parser.add_argument("--device-map", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, default=ROOT / "docs/evidence/SEM-41/PREFLIGHT.json")
    parser.add_argument("--private-output", type=Path, required=True)
    args = parser.parse_args()
    def interrupted(_signum, _frame):
        raise RuntimeError("BATCH_INTERRUPTED")
    signal.signal(signal.SIGINT, interrupted)
    signal.signal(signal.SIGTERM, interrupted)
    PilotBatch(args).run()


if __name__ == "__main__":
    main()
