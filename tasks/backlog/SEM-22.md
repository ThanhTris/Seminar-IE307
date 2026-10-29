# SEM-22 — Đối chiếu hai bài nghiên cứu với API push hiện hành

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Trang** (`rosy179`).
- Hạn: **2026-11-01** (UTC+7).
- Công sức: 2/100 — Nghiên cứu/lập luận.
- Tách từ nhóm cũ: [SEM-03](SEM-03.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** [SEM-15](SEM-15.md), [SEM-20](SEM-20.md), [SEM-21](SEM-21.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Trang cần làm

1. Chuẩn bị bảng documentation cho FCM v1/data-only/normal priority ngay.
2. Khi hai ghi chú paper có sẵn, đối chiếu claim push với API/OS version của demo.
3. Đánh dấu claim còn là giả thuyết và case cần evidence; ghi EAP khác baseline ở phụ lục.

## Đầu ra bắt buộc

- `research/notes/API_CROSSCHECK.md`
- `docs/evidence/SEM-22/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Mỗi dòng có nguồn/vị trí/version và giới hạn, không trộn kết quả paper với demo.
- [ ] Không yêu cầu paper hoàn tất mới bắt đầu đọc tài liệu API; chỉ gate bản đối chiếu cuối.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-50](SEM-50.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Trang thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
