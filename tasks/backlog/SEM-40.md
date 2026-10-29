# SEM-40 — Thêm fault injection cố ý bỏ gửi push

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Tâm** (`HoaiTam`).
- Hạn: **2026-11-04** (UTC+7).
- Công sức: 1/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-07](SEM-07.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-27](SEM-27.md), [SEM-35](SEM-35.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Tâm cần làm

1. Thêm lệnh update snapshot với tùy chọn không gửi push và nhãn fault injection.
2. Ghi run/version và lý do skip để chứng minh server đã cập nhật nhưng không gửi tín hiệu.
3. Bàn giao lệnh chạy E06; không giả định FCM đã làm mất tin.

## Đầu ra bắt buộc

- `server/ (skip-push CLI)`
- `docs/evidence/SEM-40/FAULT_INJECTION.md`
- `docs/evidence/SEM-40/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Update vẫn persist đúng version, log không có accepted cho lần đã skip.
- [ ] Phân biệt bỏ gửi có kiểm soát với delivery failure thật.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-36](SEM-36.md) cần đầu ra này để **hoàn tất**.
- [SEM-37](SEM-37.md) cần đầu ra này để **bắt đầu**.
- [SEM-49](SEM-49.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Tâm thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
