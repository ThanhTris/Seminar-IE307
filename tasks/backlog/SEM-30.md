# SEM-30 — Triển khai unique periodic work

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-30 01:48:21 UTC.
- Người thực hiện duy nhất: **Trung** (`TrungNQ2645`).
- Hạn: **01/11/2026 18:00 (UTC+7)**.
- Công sức: 4/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-05](SEM-05.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-17](SEM-17.md), [SEM-25](SEM-25.md), [SEM-28](SEM-28.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-17 — Giải thích periodic WorkManager và constraints](SEM-17.md) | Trung | `docs/mechanisms/PERIODIC_FETCH.md` | `docs/evidence/SEM-17/CHECKS.md` | Todo |
| Bắt đầu | [SEM-25 — Xây Room, SyncRepository và SyncWorker dùng chung](SEM-25.md) | Trung | `android/ (data và sync core)`<br>`docs/SYNC_CORE_API.md` | `docs/evidence/SEM-25/CHECKS.md` | Todo |
| Bắt đầu | [SEM-28 — Ghép manual sync đầu cuối và chốt hướng dẫn setup](SEM-28.md) | Trí | `docs/SETUP.md`<br>`docs/ENVIRONMENT.md`<br>`docs/evidence/SEM-28/M1.md` | `docs/evidence/SEM-28/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-30 01:48:21 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trung cần làm

1. Tạo periodic scheduler với network constraint, unique work và chu kỳ hợp lệ.
2. Gọi worker chung, ghi đăng ký/start/finish với source PERIODIC.
3. Cung cấp thao tác bật/tắt/query lịch cho mode controller; không tạo engine sync thứ hai.

## Đầu ra bắt buộc

- `android/ (periodic scheduler)`
- `docs/evidence/SEM-30/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Đăng ký lặp chỉ có một lịch active; tắt periodic không để lịch cũ tiếp tục gây nhiễu.
- [ ] Kiểm scheduler logic không được dùng để kết luận thời điểm chạy tự nhiên.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-29](SEM-29.md) cần đầu ra này để **bắt đầu**.
- [SEM-31](SEM-31.md) cần đầu ra này để **bắt đầu**.
- [SEM-36](SEM-36.md) cần đầu ra này để **bắt đầu**.
- [SEM-39](SEM-39.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trung thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
