# SEM-35 — Làm CLI gửi FCM data-only normal priority

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Tâm** (`HoaiTam`).
- Hạn: **2026-11-01** (UTC+7).
- Công sức: 2/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-06](SEM-06.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-13](SEM-13.md), [SEM-18](SEM-18.md), [SEM-27](SEM-27.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Tâm cần làm

1. Hiện thực sender stable Firebase Admin với AndroidConfig v1/data-only/normal priority.
2. Ghi accepted/rejected, message correlation, TTL và run/version, không log token.
3. Bàn giao lệnh test cho client callback và hướng dẫn cấu hình local.

## Đầu ra bắt buộc

- `server/ (FCM sender CLI)`
- `docs/setup/FCM_SENDER.md`
- `docs/evidence/SEM-35/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] CLI gửi có response thật hoặc blocker; ID có thể null nếu API chưa cấp.
- [ ] Payload không có notification block và không trộn AndroidConfigV2 EAP.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-34](SEM-34.md) cần đầu ra này để **bắt đầu**.
- [SEM-36](SEM-36.md) cần đầu ra này để **bắt đầu**.
- [SEM-40](SEM-40.md) cần đầu ra này để **bắt đầu**.
- [SEM-49](SEM-49.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Tâm thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
