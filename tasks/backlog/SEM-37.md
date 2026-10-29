# SEM-37 — Chốt bản ứng viên và manifest phục vụ tập chính

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Trí** (`ThanhTris`).
- Hạn: **2026-11-05** (UTC+7).
- Công sức: 2/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-07](SEM-07.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-31](SEM-31.md), [SEM-33](SEM-33.md), [SEM-36](SEM-36.md), [SEM-38](SEM-38.md), [SEM-39](SEM-39.md), [SEM-40](SEM-40.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Trí cần làm

1. Pin app/server commit, APK SHA256, dependency/config và danh sách ca pilot trên bản ứng viên.
2. Build candidate, rà M1/hai trigger/hybrid và ghi cổng đủ để đo main.
3. Bàn giao đường dẫn artifact và quy tắc phải chạy lại ca khi code/config liên quan đổi.

## Đầu ra bắt buộc

- `release/CANDIDATE_MANIFEST.json`
- `docs/evidence/SEM-37/CANDIDATE_GATE.md`
- `docs/evidence/SEM-37/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Truy được artifact tới đúng source/config và pilot đã ghi; không chỉ gửi APK không metadata.
- [ ] Chốt cuối 05/11 để tập chính 06–07/11; nếu trễ ghi blocker và điều chỉnh ca mở rộng.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-41](SEM-41.md) cần đầu ra này để **bắt đầu**.
- [SEM-42](SEM-42.md) cần đầu ra này để **bắt đầu**.
- [SEM-46](SEM-46.md) cần đầu ra này để **hoàn tất**.
- [SEM-52](SEM-52.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trí thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
