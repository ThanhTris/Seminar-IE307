# SEM-42 — Chạy đối chiếu OPPO E01/E02 và ghi giới hạn OEM

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Vinh** (`Vinh5905`).
- Hạn: **2026-11-07** (UTC+7).
- Công sức: 3/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-08](SEM-08.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-12](SEM-12.md), [SEM-16](SEM-16.md), [SEM-24](SEM-24.md), [SEM-37](SEM-37.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Vinh cần làm

1. Chạy E01 phiên 90 phút và E02 5 lượt/120 giây trên OPPO với bản ứng viên.
2. Ghi cấu hình pin/OS/mạng thật; nếu thử process death/recent-swipe/force-stop thì gắn nhãn riêng.
3. Xuất manifest/log và lý do ca không chạy; hoàn tác cấu hình đã đổi theo protocol.

## Đầu ra bắt buộc

- `experiments/runs/<oppo-main-run>/manifest.json`
- `experiments/runs/<oppo-main-run>/events.jsonl`
- `docs/evidence/SEM-42/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Không lấy phiên bản OS từ tên model; phân biệt baseline với cấu hình pin thay đổi.
- [ ] Không suy rộng mọi Android từ OPPO; force-stop có mốc mở lại và không tuyên bố hybrid vượt giới hạn.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-43](SEM-43.md) cần đầu ra này để **bắt đầu**.
- [SEM-44](SEM-44.md) cần đầu ra này để **bắt đầu**.
- [SEM-45](SEM-45.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Vinh thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
