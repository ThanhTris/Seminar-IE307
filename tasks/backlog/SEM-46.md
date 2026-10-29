# SEM-46 — Viết phần mở bài và bàn giao lời dẫn thao tác demo

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Trí** (`ThanhTris`).
- Hạn: **2026-11-08** (UTC+7).
- Công sức: 1/100 — Nghiên cứu/lập luận.
- Tách từ nhóm cũ: [SEM-09](SEM-09.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** [SEM-14](SEM-14.md), [SEM-37](SEM-37.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Trí cần làm

1. Viết nội dung mở bài/câu hỏi trigger-to-cache và thao tác thiết bị cho demo.
2. Liên kết bản ứng viên, mode/reset và phương án mở log/video trong đúng phần nói.
3. Bàn giao file nội dung riêng; không chỉnh deck chính của Tuấn.

## Đầu ra bắt buộc

- `slides/inputs/TRI.md`
- `docs/evidence/SEM-46/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Lời dẫn khớp scope/candidate thật, ghi rõ live và playback.
- [ ] Không thêm tính năng hoặc lời hứa độ trễ chưa được evidence hỗ trợ.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-51](SEM-51.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Trí thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
