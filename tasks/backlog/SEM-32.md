# SEM-32 — Triển khai callback FCM và enqueue sync

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Trang** (`rosy179`).
- Hạn: **2026-11-02** (UTC+7).
- Công sức: 4/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-06](SEM-06.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-15](SEM-15.md), [SEM-25](SEM-25.md), [SEM-28](SEM-28.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Trang cần làm

1. Thêm FirebaseMessagingService nhận data-only v1, ghi push_received rồi enqueue worker chung.
2. Parse run/version/message correlation, xử lý payload thiếu/sai; không sync dài ngay trong callback.
3. Giữ normal priority và không tạo thông báo hiển thị trong demo.

## Đầu ra bắt buộc

- `android/ (messaging callback và enqueue adapter)`
- `docs/evidence/SEM-32/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Callback dẫn tới work_enqueued/start/applied theo correlation khi đủ điều kiện.
- [ ] Không dùng high priority/EAP hoặc engine riêng để che độ trễ.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-33](SEM-33.md) cần đầu ra này để **bắt đầu**.
- [SEM-34](SEM-34.md) cần đầu ra này để **bắt đầu**.
- [SEM-36](SEM-36.md) cần đầu ra này để **bắt đầu**.
- [SEM-38](SEM-38.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trang thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
