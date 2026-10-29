# SEM-43 — Chốt SUMMARY và bộ evidence thực nghiệm

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Vinh** (`Vinh5905`).
- Hạn: **2026-11-07** (UTC+7).
- Công sức: 1/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-08](SEM-08.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-41](SEM-41.md), [SEM-42](SEM-42.md), [SEM-44](SEM-44.md), [SEM-45](SEM-45.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Vinh cần làm

1. Tổng hợp hypothesis → observation → explanation → limitation theo case/device/mode/build.
2. Liên kết CSV, logs, run_id và audit, ghi đủ mẫu thiếu/timeout/run bị nhiễu.
3. Chốt SUMMARY để report/slide dùng đúng evidence; chưa chạy ghi NOT_RUN.

## Đầu ra bắt buộc

- `experiments/SUMMARY.md`
- `docs/evidence/SEM-43/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Mọi bảng truy được run/manifest/build; không trộn tập khác version.
- [ ] Median kèm n_complete/n_total, không suy pin từ số request và không so latency thiếu kiểm soát.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-48](SEM-48.md) cần đầu ra này để **hoàn tất**.
- [SEM-50](SEM-50.md) cần đầu ra này để **hoàn tất**.
- [SEM-52](SEM-52.md) cần đầu ra này để **hoàn tất**.
- [SEM-55](SEM-55.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Vinh thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
