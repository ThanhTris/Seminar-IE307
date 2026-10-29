# SEM-39 — Củng cố version guard, retry và race trong core

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Trung** (`TrungNQ2645`).
- Hạn: **2026-11-05** (UTC+7).
- Công sức: 2/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-07](SEM-07.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-25](SEM-25.md), [SEM-30](SEM-30.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Trung cần làm

1. Hoàn thiện concurrency/transaction/idempotence, retry hữu hạn cho transient và failure cho permanent.
2. Kiểm snapshot cũ/trùng, trigger đến khi worker kết thúc và phục hồi mạng.
3. Giữ worker/enqueue contract tương thích, ghi core behavior riêng cho task tích hợp nhận.

## Đầu ra bắt buộc

- `android/ (sync robustness và logic checks)`
- `docs/evidence/SEM-39/CORE_CASES.md`
- `docs/evidence/SEM-39/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Version không giảm, không ghi trùng, không mất bản mới trong race.
- [ ] Logic checks có ý nghĩa chạy thật; retry không vô hạn, có lý do dừng.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-36](SEM-36.md) cần đầu ra này để **hoàn tất**.
- [SEM-37](SEM-37.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trung thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
