# SEM-45 — Kiểm parser và bàn giao từng bước

- Người thực hiện: Tuấn (`mtuan2491`), ngày 08/11/2026 (UTC+7).
- Nhánh: `codex/SEM-45-log-parser`, tạo từ main `d29532ac19a2fba402d2d1c6d25dfb63a306a87a`.
- Phạm vi hiện tại: hoàn thành phần công cụ bằng fixture; chưa có dữ liệu chính SEM-41/42, chưa nghiệm thu toàn task. Không push hoặc đổi Status Project trong lần làm này.

## Bốn bước và điều kiện thực hiện

| Bước | Đầu ra / kiểm chứng | Trạng thái |
|---|---|---|
| 1. Nhận contract, đọc và kiểm dữ liệu | Loader JSONL/manifest canonical; test routing, duplicate, version, phân loại dataset | **Hoàn tất — commit bước 1** |
| 2. Tính chỉ số và kiểm trường hợp biên | Correlation, cửa sổ/timeout/late, clock, counts; test bằng fixture | Đủ đầu vào để làm |
| 3. Xuất CSV và hướng dẫn bàn giao | CLI tái lập, nhóm thống kê, provenance/hash, hướng dẫn và kiểm tích hợp | Đủ đầu vào để làm |
| 4. Chạy trên tập chính và chốt SEM-45 | Nhận SEM-41/42 + CHECKS, sinh `experiments/results.csv`, đối chiếu SEM-44 | **Chờ SEM-41/42; Not run** |

Mỗi bước thực hiện xong có một commit riêng. SHA tra bằng `git log --oneline -- docs/evidence/SEM-45/CHECKS.md`, tránh tự ghi SHA của commit đang tạo.

## Đầu vào đã nhận

| Nguồn | Artifact / evidence | Cách dùng |
|---|---|---|
| SEM-24 — Done | [Template](../../../experiments/RUN_MANIFEST_TEMPLATE.json), [exporter](../../../experiments/scripts/export_logs.py), [README](../../../experiments/README.md), [CHECKS](../SEM-24/CHECKS.md) | Manifest 1.0.0, exporter 1.0.0; tái sử dụng validator đọc, không sửa module nguồn |
| SEM-26 — Done | [API](../../API.md), [EVENT_SCHEMA](../../EVENT_SCHEMA.md), [CHECKS](../SEM-26/CHECKS.md) | Contract 2.0.0, 27 key/event; ID và timestamp giữ nguyên |
| SEM-16 | [PROTOCOL](../../../experiments/PROTOCOL.md), [protocol cốt lõi](../../EXPERIMENT_PROTOCOL.md) | Cửa sổ, nguồn/case, clock và mẫu số thống kê |
| SEM-29 — pilot | [CHECKS](../SEM-29/CHECKS.md) | Android `legacy-room-v1` được nghiệm thu cho pilot; không đổi thành canonical v2 hoặc tập chính |
| SEM-41/42 — Todo | Chưa có bộ run chính/CHECKS trên main nền | Chỉ chặn bước 4; không tạo `results.csv` đo thật từ fixture |

## Kết quả kiểm

Máy kiểm Windows, Python **3.12.14**, standard library. Python alias của Windows không chạy được nên dùng Python có sẵn trong runtime của Codex; không thêm dependency. Sandbox không cho ghi temp mặc định; đặt TEMP/TMP/TMPDIR của tiến trình kiểm vào `.local/sem45-temp` (Git bỏ qua), sau đó chạy đạt.

| Check | Expected | Actual | Kết quả |
|---|---|---|---|
| Loader canonical | Không suy trường thiếu, không trộn route/schema/dataset, giữ giá trị và hash | 8 test đạt: fixture SEM-24 giữ nguyên, legacy bị từ chối, replay dedup, conflict/duplicate key/NaN/blank/future field/type sai bị chặn | Pass — synthetic/offline |

Lệnh bước 1: `python -B -m unittest discover -s experiments/scripts/tests -p test_analyze.py -v`. Runtime Android/server/FCM/OPPO và tập chính **Not run**.
