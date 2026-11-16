#!/usr/bin/env python3
"""Render SEM-48 descriptive plots from pinned public artifacts, never latency.

This is a slide asset renderer, not the SEM-45 analyzer or SEM-44 auditor.
It refuses changed input and new main data until the presentation is reviewed.
"""

import argparse
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

# Keep font/config cache outside the source tree, including restricted hosts.
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "sem48-mpl"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CASES = ("E01", "E03", "E04", "E06")
BUCKETS = ("VALID_SUCCESS", "INVALID_SUCCESS", "INVALID_TIMEOUT", "INVALID_FAILURE")
COLORS = ("#17639b", "#b5bdc9", "#ecb04b", "#80669e")
LABELS = ("VALID · SUCCESS mới", "INVALID · SUCCESS cũ",
          "INVALID · TIMEOUT cũ", "INVALID · ABORTED cũ")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def inputs():
    index = load(HERE / "INPUTS.json")
    for ref in index["sources"]:
        raw = (ROOT / ref["path"]).read_bytes()
        blob = subprocess.check_output(["git", "show", index["source_revision"] + ":" + ref["path"]], cwd=ROOT)
        if raw != blob or hashlib.sha256(raw).hexdigest() != ref["sha256"]:
            raise ValueError("INPUT_CHANGED: " + ref["path"])
    for path in (ROOT / "experiments").rglob("manifest.json"):
        if load(path).get("run_phase") == "main":
            raise ValueError("MAIN_INPUT_REQUIRES_AUDITED_CSV_AND_PRESENTATION_UPDATE")
    inventory = load(ROOT / "docs/evidence/SEM-41/PILOT_RESULTS.json")
    summary = load(ROOT / "docs/evidence/SEM-43/EVIDENCE_INDEX.json")
    contexts = {r["run_id"]: r for r in summary["sem41_pilot"]["attempts_index"]}
    records = []
    for row in inventory["runs"]:
        folder = ROOT / row["artifact_directory"]
        manifest, audit = load(folder / "manifest.json"), load(folder / "audit.json")
        if not (manifest["run_id"] == row["run_id"] and
                manifest["run_phase"] == "pilot" and manifest["data_kind"] == "OBSERVED" and
                manifest["validity"] == audit["validity"] == row["validity"] and
                manifest["outcome"] == row["outcome"]):
            raise ValueError("PILOT_METADATA_MISMATCH")
        bucket = row["validity"] + "_" + row["outcome"]
        if bucket not in BUCKETS or row["case_id"] not in CASES:
            raise ValueError("NEW_OUTCOME_REQUIRES_PRESENTATION_UPDATE")
        records.append({"run_id": row["run_id"], "case_id": row["case_id"],
                        "mode": row["mode"], "run_phase": "pilot", "data_kind": "OBSERVED",
                        "validity": row["validity"], "execution_status": row["execution_status"],
                        "declared_outcome": row["outcome"], "bucket": bucket,
                        "app_commit": manifest["build"]["app_commit"],
                        "apk_sha256": manifest["build"]["apk_sha256"],
                        "server_commit": manifest["build"]["server_commit"],
                        "device_alias": manifest["device_alias"],
                        "intervention": manifest["intervention"],
                        "server_store_epoch": row["server_store_epoch"],
                        "observer_commit": row["observer_commit"],
                        "config_sha256": contexts[row["run_id"]]["config_sha256"],
                        "manifest_path": row["artifact_directory"] + "/manifest.json",
                        "events_path": row["artifact_directory"] + "/events.jsonl",
                        "audit_path": row["artifact_directory"] + "/audit.json"})
    if len(records) != 20 or Counter(r["bucket"] for r in records) != dict(zip(BUCKETS, (8, 5, 5, 2))):
        raise ValueError("INVENTORY_REQUIRES_PRESENTATION_UPDATE")
    if summary["main"]["observed_runs"] != 0:
        raise ValueError("SUMMARY_MAIN_STATUS_CHANGED")
    return index, records, summary["main"]


def csv_file(path, records):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def save(fig, output, name):
    fig.savefig(output / (name + ".svg"), metadata={"Date": None, "Creator": "SEM-48 / Matplotlib"})
    fig.savefig(output / (name + ".png"), dpi=120, metadata={"Software": "SEM-48 / Matplotlib"})
    plt.close(fig)


def pilot_plot(records, output):
    counts = Counter((r["case_id"], r["bucket"]) for r in records)
    fig = plt.figure(figsize=(16, 9), facecolor="white")
    fig.text(.065, .93, "Pilot emulator: 8 hợp lệ, 12 INVALID", fontsize=30, weight="bold", color="#172638")
    fig.text(.065, .872, "20 lần thử · outcome gốc được giữ · main n_complete/n_total = 0/0", fontsize=18, color="#475569")
    ax = fig.add_axes((.20, .34, .72, .44))
    ypos = [3, 2, 1, 0]
    left = [0] * 4
    for i, bucket in enumerate(BUCKETS):
        values = [counts[case, bucket] for case in CASES]
        bars = ax.barh(ypos, values, left=left, height=.52, color=COLORS[i],
                       edgecolor="#ffffff", hatch="//" if i else None)
        for bar, value in zip(bars, values):
            if value:
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_y()+bar.get_height()/2,
                        str(value), ha="center", va="center", fontsize=19, weight="bold",
                        color="white" if i in (0, 3) else "#172638")
        left = [a+b for a, b in zip(left, values)]
    ax.set_yticks(ypos, [case + (" · HYBRID" if case == "E06" else " · PERIODIC") for case in CASES], fontsize=17)
    ax.set_xlim(0, 7.3)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(axis="x", labelsize=15)
    ax.tick_params(axis="y", length=0, pad=12)
    ax.set_xlabel("Số run pilot (không phải số cycle)", fontsize=17, labelpad=10)
    for y, n in zip(ypos, left):
        ax.text(n+.12, y, "n_input="+str(n), va="center", fontsize=15, color="#475569")
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#cbd5e1")
    legend = [Patch(facecolor=c, label=l, hatch="//" if i else None) for i, (c, l) in enumerate(zip(COLORS, LABELS))]
    fig.legend(handles=legend, loc="lower left", bbox_to_anchor=(.065, .17), ncol=2,
               frameon=False, fontsize=16, columnspacing=3)
    fig.text(.065, .105, "INVALID khác collector/epoch; không gộp các nhóm để tính tỷ lệ hoặc latency.", fontsize=14, color="#475569")
    fig.text(.065, .063, "Android 17/API 37 · app 9e7e55b · Firebase chưa cấu hình · validity theo review SEM-41", fontsize=13, color="#475569")
    fig.text(.065, .027, "Nguồn: PILOT_RESULTS + SUMMARY fce39b0 · chưa có kiểm độc lập SEM-44 cho bộ mới", fontsize=12, color="#64748b")
    save(fig, output, "pilot_inventory")


def main_plot(main, output):
    fig = plt.figure(figsize=(16, 9), facecolor="white")
    fig.text(.065, .91, "Tập main chưa chạy trên cả hai thiết bị", fontsize=28, weight="bold", color="#172638")
    fig.text(.065, .84, "33 slot kế hoạch · run main đã nhận: 0 · NOT_RUN", fontsize=21, color="#475569")
    ax = fig.add_axes((.18, .38, .75, .32))
    planned = [main["planned_emulator_slots"], main["planned_oppo_slots"]]
    ax.barh([1, 0], planned, height=.47, color="#dce3eb", edgecolor="#8a98a8", hatch="//")
    for y, value in zip([1, 0], planned):
        ax.text(value+.5, y, str(value)+" slot kế hoạch", va="center", fontsize=19, color="#334155")
    ax.set_yticks([1, 0], ["Emulator", "OPPO"], fontsize=20)
    ax.tick_params(axis="y", length=0, pad=14)
    ax.tick_params(axis="x", labelsize=16)
    ax.set_xlim(0, 35)
    ax.set_xlabel("Số slot cần chạy theo protocol", fontsize=18, labelpad=12)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#cbd5e1")
    fig.text(.065, .245, "Main n_complete/n_total = 0/0 · median và completion rate: N/A", fontsize=21, color="#172638")
    fig.text(.065, .16, "Chưa quan sát không có nghĩa thất bại; pilot không thay thế main hoặc OPPO.", fontsize=18, color="#475569")
    fig.text(.065, .09, "Nguồn: EMULATOR_PLAN (27) + RUN_SCHEDULE/SUMMARY (6 OPPO) · snapshot fce39b0", fontsize=13, color="#64748b")
    fig.text(.065, .045, "Đây là độ phủ evidence, không phải biểu đồ tỷ lệ thành công hoặc thời gian chạy.", fontsize=14, color="#475569")
    save(fig, output, "main_coverage")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    index, records, main_status = inputs()
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none",
                         "svg.hashsalt": "SEM48-fce39b0-v1", "axes.unicode_minus": False})
    csv_file(args.output / "pilot_inventory.csv", records)
    main_rows = [{"device_alias": alias, "planned_slots": main_status[key], "observed_main_runs": 0,
                  "n_complete": 0, "n_total": 0, "completion_rate": "", "median_latency_ms": "",
                  "status": "NOT_RUN", "source_revision": index["source_revision"]}
                 for alias, key in [("emulator-main", "planned_emulator_slots"), ("oppo-find-x9", "planned_oppo_slots")]]
    csv_file(args.output / "main_coverage.csv", main_rows)
    pilot_plot(records, args.output)
    main_plot(main_status, args.output)
    print(json.dumps({"pilot_attempts": len(records), "valid": 8, "invalid": 12,
                      "main_runs": 0, "latency_statistics_computed": False}))


if __name__ == "__main__":
    main()
