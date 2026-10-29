# SEM-49 — Viết phần kiến trúc và lập luận nghiên cứu thứ hai

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Tâm** (`HoaiTam`).
- Hạn: **2026-11-08** (UTC+7).
- Công sức: 1/100 — Nghiên cứu/lập luận.
- Tách từ nhóm cũ: [SEM-09](SEM-09.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-18](SEM-18.md)
- **Hoàn tất còn cần:** [SEM-21](SEM-21.md), [SEM-27](SEM-27.md), [SEM-35](SEM-35.md), [SEM-40](SEM-40.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Tâm cần làm

1. Soạn nội dung kiến trúc server/shared sync và giải thích fault injection.
2. Đối chiếu bài thứ hai với dữ liệu demo/phương pháp, ghi giới hạn áp dụng.
3. Bàn giao file riêng có nguồn và link contract/runtime.

## Đầu ra bắt buộc

- `slides/inputs/TAM.md`
- `docs/evidence/SEM-49/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Không đồng nhất skip-push với FCM mất tin hoặc accepted với delivered.
- [ ] Kiến trúc đúng code/contract đã bàn giao và lập luận paper được dẫn nguồn.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-51](SEM-51.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Tâm thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
