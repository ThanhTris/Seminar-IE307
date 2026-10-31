# SEM-34 — Chạy pilot push E02 và xác nhận cache nền

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-31 12:44:19 UTC.
- Người thực hiện duy nhất: **Vinh** (`Vinh5905`).
- Hạn: **03/11/2026 22:00 (UTC+7)**.
- Công sức: 1/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-06](SEM-06.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-16](SEM-16.md), [SEM-24](SEM-24.md), [SEM-32](SEM-32.md), [SEM-35](SEM-35.md)
- **Hoàn tất còn cần:** [SEM-33](SEM-33.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Protocol cốt lõi](../../docs/EXPERIMENT_PROTOCOL.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-16 — Lập ma trận lifecycle và protocol E01–E06](SEM-16.md) | Vinh | `experiments/PROTOCOL.md`<br>`experiments/RUN_SCHEDULE.md` | `docs/evidence/SEM-16/CHECKS.md` | Todo |
| Bắt đầu | [SEM-24 — Chuẩn bị bộ xuất log và run manifest](SEM-24.md) | Vinh | `experiments/RUN_MANIFEST_TEMPLATE.json`<br>`experiments/scripts/export_logs.*`<br>`experiments/README.md` | `docs/evidence/SEM-24/CHECKS.md` | Todo |
| Bắt đầu | [SEM-32 — Triển khai callback FCM và enqueue sync](SEM-32.md) | Trang | `android/ (messaging callback và enqueue adapter)` | `docs/evidence/SEM-32/CHECKS.md` | Todo |
| Bắt đầu | [SEM-35 — Làm CLI gửi FCM data-only normal priority](SEM-35.md) | Tâm | `server/ (FCM sender CLI)`<br>`docs/setup/FCM_SENDER.md` | `docs/evidence/SEM-35/CHECKS.md` | Todo |
| Hoàn tất | [SEM-33 — Xử lý token refresh và bàn giao PUSH.md](SEM-33.md) | Trang | `android/ (token lifecycle)`<br>`docs/PUSH.md` | `docs/evidence/SEM-33/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-31 12:44:19 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Vinh cần làm

1. Tắt periodic và gửi data-only khi app ở background; ghi trước/sau từng event.
2. Xác nhận snapshot_applied trước khi mở lại UI và không có notification do demo tạo.
3. Lưu run pilot/recording đã loại token và lỗi còn thiếu để owner module sửa.

## Đầu ra bắt buộc

- `experiments/runs/<push-pilot-run>/manifest.json`
- `experiments/runs/<push-pilot-run>/events.jsonl`
- `docs/evidence/SEM-34/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Không coi accepted là delivered và không dùng UI auto-refresh để tạo kết quả.
- [ ] Ghi điều kiện thiết bị/window/timeout thật; bản PUSH/token lifecycle đã được bàn giao.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-36](SEM-36.md) cần đầu ra này để **bắt đầu**.
- [SEM-47](SEM-47.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Vinh thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
