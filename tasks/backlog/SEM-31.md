# SEM-31 — Bàn giao chẩn đoán và tài liệu periodic

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-31 16:46:06 UTC.
- Người thực hiện duy nhất: **Trung** (`TrungNQ2645`).
- Hạn: **02/11/2026 12:00 (UTC+7)**.
- Công sức: 3/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-05](SEM-05.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-30](SEM-30.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-30 — Triển khai unique periodic work](SEM-30.md) | Trung | `android/ (periodic scheduler)` | `docs/evidence/SEM-30/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-31 16:46:06 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trung cần làm

1. Viết PERIODIC: config/constraints, cách query lịch, phân biệt debug với quan sát tự nhiên.
2. Kiểm re-register/cancel/network constraints trên đúng build và lưu lệnh chẩn đoán.
3. Ghi cách đọc periodic timeline để người chạy ca dùng độc lập.

## Đầu ra bắt buộc

- `docs/PERIODIC.md`
- `docs/evidence/SEM-31/SCHEDULER_CHECKS.md`
- `docs/evidence/SEM-31/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Có bằng chứng một lịch active và hành vi constraint/cancel, không chỉ tên hàm.
- [ ] Tài liệu nêu scheduler không bảo đảm chạy đúng từng mốc, giữ các giới hạn OS.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-29](SEM-29.md) cần đầu ra này để **hoàn tất**.
- [SEM-37](SEM-37.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trung thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
