"""Audit collector interference without modifying any measured events/outcomes.

JobScheduler dumps are not assumed read-only: the dump's readiness evaluation can
satisfy/remove timing constraints without queuing the job. Only outside-window
snapshots are acceptable for an unbiased periodic observation.
"""

import hashlib
import json
from pathlib import Path
import re


def scheduler_collection(folder, record):
    folder = Path(folder)
    start, end = record.get("start_elapsed_realtime_ms"), record.get("end_elapsed_realtime_ms")
    if start is None or end is None:
        return {"status": "NOT_ASSESSED", "reason": "MEASUREMENT_NOT_STARTED", "in_window_dumps": []}
    dumps = []
    missing_clock = []
    for checkpoint in sorted(folder.glob("*-checkpoint.json")):
        state = json.loads(checkpoint.read_text())
        if type(state.get("elapsed_realtime_ms")) is not int:
            missing_clock.append(checkpoint.name)
            continue
        if not start <= state["elapsed_realtime_ms"] <= end:
            continue
        capture = checkpoint.with_name(checkpoint.name.replace("-checkpoint.json", "-jobs.txt"))
        if not capture.exists() and not state.get("scheduler_dump_performed", False):
            continue
        entry = {"checkpoint": checkpoint.name, "elapsed_realtime_ms": state["elapsed_realtime_ms"],
                 "capture_present": capture.exists(), "timer_transition_pattern": False}
        if capture.exists():
            text = capture.read_text()
            registered = text.split("Registered ", 1)[-1].split("PrefetchController:", 1)[0]
            controller = text.split("TimeController:", 1)[-1].split("IdleController:", 1)[0]
            entry.update(capture_file=capture.name, capture_sha256=hashlib.sha256(capture.read_bytes()).hexdigest(),
                         timing_delay_printed_unsatisfied=bool(re.search(r"Unsatisfied constraints:.*\bTIMING_DELAY\b", registered)),
                         ready_printed=bool(re.search(r"Ready: true", registered)),
                         time_controller_has_tracked_job=bool(re.search(r"#androidx\.work\.systemjobscheduler:", controller)))
            entry["timer_transition_pattern"] = entry["timing_delay_printed_unsatisfied"] and not entry["time_controller_has_tracked_job"]
        dumps.append(entry)
    return {"status": "FAIL" if dumps or missing_clock else "PASS",
            "reason": "IN_WINDOW_JOB_DUMP_CAN_REEVALUATE_TIMERS" if dumps else "SCHEDULER_OBSERVATION_CLOCK_MISSING" if missing_clock else "NO_IN_WINDOW_JOB_DUMP",
            "checkpoints_without_clock": missing_clock,
            "in_window_dump_count": len(dumps),
            "timer_transition_count": sum(entry["timer_transition_pattern"] for entry in dumps),
            "in_window_dumps": dumps, "events_or_outcomes_modified": False}
