# SEM-45 — Viết parser log và sinh results.csv

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Tuấn** (`mtuan2491`).
- Hạn: **2026-11-07** (UTC+7).
- Công sức: 2/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-08](SEM-08.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-24](SEM-24.md), [SEM-26](SEM-26.md)
- **Hoàn tất còn cần:** [SEM-41](SEM-41.md), [SEM-42](SEM-42.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Tuấn cần làm

1. Xây parser từ manifest/events sang outcome/timings/counts theo protocol; có thể chuẩn bị bằng fixture có nhãn.
2. Khi main logs bàn giao, chạy để sinh results.csv và lệnh tái lập.
3. Giữ timeout riêng, kiểm clock offset và nhóm theo case/device/mode/build.

## Đầu ra bắt buộc

- `experiments/scripts/analyze.*`
- `experiments/results.csv`
- `docs/evidence/SEM-45/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Tái sinh được CSV từ log; fixture không lẫn main, không gán latency timeout bằng 0.
- [ ] Accepted/received/queue/sync không bị gộp thành một mốc.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-43](SEM-43.md) cần đầu ra này để **bắt đầu**.
- [SEM-44](SEM-44.md) cần đầu ra này để **bắt đầu**.
- [SEM-48](SEM-48.md) cần đầu ra này để **hoàn tất**.
- [SEM-50](SEM-50.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Tuấn thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
