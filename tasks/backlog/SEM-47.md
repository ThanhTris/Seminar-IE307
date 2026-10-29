# SEM-47 — Viết phần silent push và lời dẫn demo 4 phút

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Trang** (`rosy179`).
- Hạn: **2026-11-08** (UTC+7).
- Công sức: 2/100 — Nghiên cứu/lập luận.
- Tách từ nhóm cũ: [SEM-09](SEM-09.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-15](SEM-15.md)
- **Hoàn tất còn cần:** [SEM-33](SEM-33.md), [SEM-34](SEM-34.md), [SEM-38](SEM-38.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Trang cần làm

1. Soạn nội dung cơ chế push, payload/TTL/token và giới hạn bằng evidence được bàn giao.
2. Viết một mạch lời dẫn demo cho cả push/periodic/Doze; đánh dấu phần live/playback.
3. Ghi ngưỡng 30 giây đổi video và câu trả lời accepted khác delivered.

## Đầu ra bắt buộc

- `slides/inputs/TRANG.md`
- `slides/DEMO_SCRIPT.md`
- `docs/evidence/SEM-47/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Nội dung demo nằm trong 4 phút và không coi 30 giây là bảo đảm FCM.
- [ ] Mỗi claim có nguồn/evidence hoặc ghi giả thuyết; chỉ giao file input riêng.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-51](SEM-51.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Trang thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
