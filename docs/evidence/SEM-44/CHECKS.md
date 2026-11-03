# SEM-44 CHECKS — Independent data audit

## Đầu ra

- [AUDIT.md](../../../experiments/AUDIT.md): đầu vào, assertions và trạng thái audit.
- [audit_main_runs.py](../../../experiments/scripts/audit_main_runs.py): kiểm schema 2.0, correlation, version và so khớp manifest/CSV khi artifacts đến.
- [AUDIT_RESULTS.md](../../../experiments/AUDIT_RESULTS.md): lần chạy hiện tại ghi `NOT_RUN`, 0 main runs, 0 CSV rows; hai đầu vào chính còn thiếu.

| Hạng mục | Expected | Actual | Trạng thái |
|---|---|---|---|
| Emulator main run | Manifest + JSONL thật của SEM-41 | Chưa có | Not run |
| OPPO main run | Manifest + JSONL thật của SEM-42 | Chưa có | Not run |
| Parser/results CSV | Đầu ra SEM-45, nối được run/build | Chưa có | Not run |
| Kiểm trigger, mẫu số, timeout, clock, applied/unchanged | Assertions trên artifacts thật | Chưa chạy do thiếu input | Not run |
| Auditor tái lập | Script chỉ đọc manifests/events/CSV, ghi báo cáo riêng | Đã chạy trên checkout hiện tại; tạo báo cáo NOT_RUN do không có runs directory/results.csv | Pass (no-input path); main audit Not run |

Commit main/run IDs: chưa có. Build/config/device: chưa có artifacts bàn giao. Blocker trực tiếp: SEM-41, SEM-42, SEM-45 chưa có output trong checkout. Không ký Pass và không đánh dấu Done khi thiếu dữ liệu.
