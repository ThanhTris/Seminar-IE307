# SEM-44 — Main run data audit

**Status: NOT RUN — dữ liệu đầu vào chưa được bàn giao.** Không có main-run artifacts hoặc `results.csv` trong workspace tại thời điểm audit này. Không có run_id/commit main để ký pass; không suy ra số liệu từ fixture hoặc kế hoạch. Lần chạy auditor hiện tại ghi 0 runs/0 CSV rows tại [AUDIT_RESULTS.md](AUDIT_RESULTS.md).

Khi SEM-41/42/45 bàn giao artifacts, chạy auditor chỉ đọc đầu vào:

```powershell
python experiments/scripts/audit_main_runs.py
```

Mặc định script đọc `experiments/runs/*/{manifest.json,events.jsonl}` và `experiments/results.csv`, sau đó ghi báo cáo vào `experiments/AUDIT_RESULTS.md`. Có thể truyền `--runs`, `--csv` và `--output` để chỉ định đường dẫn khác. Script kiểm schema bằng SEM-24 exporter, nối các event work theo request/work/attempt, đối chiếu metadata CSV và phát hiện timeout bị gán latency 0. `AUDIT_READY` chỉ là kiểm tra cấu trúc; owner vẫn phải xác nhận protocol, thiết bị và run thật.

## Đầu vào cần nhận

- `experiments/runs/<emulator-main-run>/manifest.json` và `events.jsonl` (SEM-41).
- `experiments/runs/<oppo-main-run>/manifest.json` và `events.jsonl` (SEM-42).
- `experiments/results.csv` và parser/logic sinh file (SEM-45).
- Mỗi run phải nêu build/commit, device alias, mode, phase, cửa sổ đo, version schema và trạng thái thực chạy.

## Các assertion khi nhận dữ liệu

| Kiểm tra | Expected | Actual | Trạng thái |
|---|---|---|---|
| Manifest ↔ CSV | Mỗi dòng trỏ tới run_id, device, mode, phase, commit/build có thật | Chưa có input | Not run |
| Trigger | PERIODIC/PUSH/MANUAL khớp event và cấu hình mode; manual loại khỏi background stats | Chưa có input | Not run |
| Event lifecycle | Enqueue/received/start/fetch/apply là mốc riêng; không suy missing event thành success | Chưa có input | Not run |
| Version outcome | Applied chỉ khi version mới commit; equal unchanged; lower stale | Chưa có input | Not run |
| Mẫu số/timeout | Timeout và no-observation giữ trong mẫu số theo protocol; không gán latency 0 | Chưa có input | Not run |
| Clock | Duration Android dùng monotonic cùng boot session; liên thiết bị cần offset | Chưa có input | Not run |
| CSV reproducibility | Tính lại từ event gốc cho cùng kết quả, không sửa số đo bằng tay | Chưa có input | Not run |

## Phiếu lỗi theo run

Chưa thể điền lỗi vì không có run artifacts. Khi đầu vào đến, ghi từng lỗi dưới dạng `run_id / file:line hoặc event_id / expected / actual / assertion / producer owner`; gửi lại đúng owner để sửa nguồn, giữ nguyên log gốc và ghi parser/csv được tái sinh. Không sửa số đo để khớp giả thuyết.

Tài liệu quy tắc nguồn: [EXPERIMENT_PROTOCOL.md](../docs/EXPERIMENT_PROTOCOL.md), [EVENT_SCHEMA.md](../docs/EVENT_SCHEMA.md). Bằng chứng hiện có trong repo chỉ là fixture test, không phải main-run.
