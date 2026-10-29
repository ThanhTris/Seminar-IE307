# SEM-29 — Chạy pilot periodic E01 trên hai thiết bị

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-29 16:22:16 UTC.
- Người thực hiện duy nhất: **Vinh** (`Vinh5905`).
- Hạn: **2026-11-02** (UTC+7).
- Công sức: 2/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-05](SEM-05.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-16](SEM-16.md), [SEM-24](SEM-24.md), [SEM-30](SEM-30.md)
- **Hoàn tất còn cần:** [SEM-31](SEM-31.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Protocol cốt lõi](../../docs/EXPERIMENT_PROTOCOL.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-16 — Lập ma trận lifecycle và protocol E01–E06](SEM-16.md) | Vinh | `experiments/PROTOCOL.md`<br>`experiments/RUN_SCHEDULE.md` | `docs/evidence/SEM-16/CHECKS.md` | Todo |
| Bắt đầu | [SEM-24 — Chuẩn bị bộ xuất log và run manifest](SEM-24.md) | Vinh | `experiments/RUN_MANIFEST_TEMPLATE.json`<br>`experiments/scripts/export_logs.*`<br>`experiments/README.md` | `docs/evidence/SEM-24/CHECKS.md` | Todo |
| Bắt đầu | [SEM-30 — Triển khai unique periodic work](SEM-30.md) | Trung | `android/ (periodic scheduler)` | `docs/evidence/SEM-30/CHECKS.md` | Todo |
| Hoàn tất | [SEM-31 — Bàn giao chẩn đoán và tài liệu periodic](SEM-31.md) | Trung | `docs/PERIODIC.md`<br>`docs/evidence/SEM-31/SCHEDULER_CHECKS.md` | `docs/evidence/SEM-31/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-29 16:22:16 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Vinh cần làm

1. Nhận scheduler hoạt động và chạy pilot tự nhiên có phase=pilot/development.
2. Quan sát ít nhất hai lần chạy trong pilot; giữ đăng ký lịch ổn định và kiểm trigger PERIODIC.
3. Xuất manifest/log, ghi timeout/thiếu quan sát và lỗi cần sửa; không thay dữ liệu main.

## Đầu ra bắt buộc

- `experiments/runs/<periodic-pilot-run>/manifest.json`
- `experiments/runs/<periodic-pilot-run>/events.jsonl`
- `docs/evidence/SEM-29/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Không force-run để bù lần chạy và không gọi pilot là tập chính.
- [ ] Hoàn tất sau khi có hướng dẫn chẩn đoán SEM-31 và ghi commit/config thật.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-36](SEM-36.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Vinh thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
