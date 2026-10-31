# SEM-41 — Chạy tập chính E01–E06 trên emulator

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-31 16:46:06 UTC.
- Người thực hiện duy nhất: **Vinh** (`Vinh5905`).
- Hạn: **07/11/2026 13:00 (UTC+7)**.
- Công sức: 3/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-08](SEM-08.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-16](SEM-16.md), [SEM-24](SEM-24.md), [SEM-37](SEM-37.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Protocol cốt lõi](../../docs/EXPERIMENT_PROTOCOL.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-16 — Lập ma trận lifecycle và protocol E01–E06](SEM-16.md) | Vinh | `experiments/PROTOCOL.md`<br>`experiments/RUN_SCHEDULE.md` | `docs/evidence/SEM-16/CHECKS.md` | Todo |
| Bắt đầu | [SEM-24 — Chuẩn bị bộ xuất log và run manifest](SEM-24.md) | Vinh | `experiments/RUN_MANIFEST_TEMPLATE.json`<br>`experiments/scripts/export_logs.*`<br>`experiments/README.md` | `docs/evidence/SEM-24/CHECKS.md` | Todo |
| Bắt đầu | [SEM-37 — Chốt bản ứng viên và manifest phục vụ tập chính](SEM-37.md) | Trí | `release/CANDIDATE_MANIFEST.json`<br>`docs/evidence/SEM-37/CANDIDATE_GATE.md` | `docs/evidence/SEM-37/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-31 16:46:06 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Vinh cần làm

1. Chạy E01–E06 theo đủ số lượt/cửa sổ protocol trên bản ứng viên và run_phase=main.
2. Kiểm Doze trước/sau, tách trigger, reset/cleanup giữa run; giữ cả lỗi/timeout/NOT_RUN.
3. Xuất manifest/log theo run và chia nhóm đúng commit/config; sửa code phải chạy lại ca liên quan.

## Đầu ra bắt buộc

- `experiments/runs/<emulator-main-run>/manifest.json`
- `experiments/runs/<emulator-main-run>/events.jsonl`
- `docs/evidence/SEM-41/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Giữ E01 90 phút, E02 5 lượt/120 giây, E03 2/trigger, E04 3/trigger, E05 3/kịch bản, E06 2×45 phút.
- [ ] Không force-run cho kết quả tự nhiên, không trộn pilot/build hoặc loại timeout khỏi mẫu số.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-43](SEM-43.md) cần đầu ra này để **bắt đầu**.
- [SEM-44](SEM-44.md) cần đầu ra này để **bắt đầu**.
- [SEM-45](SEM-45.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Vinh thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
