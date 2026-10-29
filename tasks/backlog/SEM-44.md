# SEM-44 — Kiểm độc lập trigger và phép tính dữ liệu main

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Trung** (`TrungNQ2645`).
- Hạn: **2026-11-07** (UTC+7).
- Công sức: 1/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-08](SEM-08.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-41](SEM-41.md), [SEM-42](SEM-42.md), [SEM-45](SEM-45.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Trung cần làm

1. Đối chiếu CSV với log/manifest, kiểm trigger PERIODIC/PUSH/MANUAL và phase/build.
2. Kiểm mẫu số, timeout, clock offset/monotonic và các ca applied/unchanged.
3. Ghi lỗi dữ liệu theo run để task producer sửa, không sửa số đo cho khớp giả thuyết.

## Đầu ra bắt buộc

- `experiments/AUDIT.md`
- `docs/evidence/SEM-44/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Có case/input/expected/actual/assertion và run_id/commit thật.
- [ ] Không tự ký Pass cho run chưa thực hiện hoặc chưa đủ log.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-43](SEM-43.md) cần đầu ra này để **bắt đầu**.
- [SEM-48](SEM-48.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Trung thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
