# SEM-34 — Chạy pilot push E02 và xác nhận cache nền

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Vinh** (`Vinh5905`).
- Hạn: **2026-11-03** (UTC+7).
- Công sức: 1/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-06](SEM-06.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-16](SEM-16.md), [SEM-24](SEM-24.md), [SEM-32](SEM-32.md), [SEM-35](SEM-35.md)
- **Hoàn tất còn cần:** [SEM-33](SEM-33.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

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
