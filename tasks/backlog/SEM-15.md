# SEM-15 — Giải thích cơ chế silent push và giới hạn FCM

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Trang** (`rosy179`).
- Hạn: **2026-10-30** (UTC+7).
- Công sức: 3/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-02](SEM-02.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Trang cần làm

1. Viết luồng server → FCM → callback → worker và giới hạn thực thi nền.
2. Phân biệt notification/data/mixed, normal priority và FCM accepted với app received.
3. Gắn nguồn chính thức và version áp dụng; EAP chỉ ghi phụ lục, không trộn với baseline v1.

## Đầu ra bắt buộc

- `docs/mechanisms/SILENT_PUSH.md`
- `docs/evidence/SEM-15/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Có thể giải thích vì sao data-only không đồng nghĩa một thông báo bị tắt tiếng.
- [ ] Chỉ ra trường hợp trì hoãn/không nhận và không hứa push tức thì.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-19](SEM-19.md) cần đầu ra này để **hoàn tất**.
- [SEM-22](SEM-22.md) cần đầu ra này để **hoàn tất**.
- [SEM-32](SEM-32.md) cần đầu ra này để **bắt đầu**.
- [SEM-47](SEM-47.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trang thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
