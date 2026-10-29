# SEM-53 — Tái lập runbook và quay video dự phòng

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Vinh** (`Vinh5905`).
- Hạn: **2026-11-12** (UTC+7).
- Công sức: 2/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-10](SEM-10.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-52](SEM-52.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Vinh cần làm

1. Làm theo runbook trên thiết bị, ghi bước tái lập được và blocker/sai lệch để task SEM-52 sửa.
2. Quay video thật của đúng build; gắn nhãn playback và run/commit/checksum.
3. Xuất video manifest/link artifact; không commit media quá lớn hoặc lộ token/serial.

## Đầu ra bắt buộc

- `release/VIDEO_MANIFEST.json`
- `docs/evidence/SEM-53/REPRODUCTION.md`
- `Video demo/fallback có liên kết tải`
- `docs/evidence/SEM-53/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Video có metadata thật và không thay evidence thực nghiệm bằng mô phỏng.
- [ ] Runbook tái lập được hoặc chỉ rõ phần cần hỗ trợ; dữ liệu nhạy cảm đã được loại.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-54](SEM-54.md) cần đầu ra này để **hoàn tất**.
- [SEM-55](SEM-55.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Vinh thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
