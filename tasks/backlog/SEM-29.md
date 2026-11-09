# SEM-29 — Chạy pilot periodic E01 trên hai thiết bị

- Trạng thái: **Done** (Project).
- Trạng thái đầu vào: **Đã hoàn thành**.
- Đối chiếu Project: 2026-11-09 13:58:31 UTC.
- Người thực hiện duy nhất: **Vinh** (`Vinh5905`).
- Hạn: **02/11/2026 22:00 (UTC+7)**.
- Công sức: 2/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-05](SEM-05.md); nhóm cũ chỉ còn lưu lịch sử.

## Phạm vi nghiệm thu cập nhật ngày 08/11/2026

Theo phản hồi của Trí trên PR #19, SEM-29 nghiệm thu pilot E01 trên emulator. Phần thiết bị OPPO được bàn giao sang [SEM-42](SEM-42.md) do Trí phụ trách. Bộ log `legacy-room-v1` cùng manifest đã được chấp nhận làm đầu vào SEM-36 của Trung để nâng cấp producer lên schema 2.0. [Phản hồi nghiệm thu](https://github.com/ThanhTris/Seminar-IE307/pull/19#issuecomment-6721019303)

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-16](SEM-16.md), [SEM-24](SEM-24.md), [SEM-30](SEM-30.md)
- **Hoàn tất còn cần:** [SEM-31](SEM-31.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Protocol cốt lõi](../../docs/EXPERIMENT_PROTOCOL.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-16 — Lập ma trận lifecycle và protocol E01–E06](SEM-16.md) | Vinh | `experiments/PROTOCOL.md`<br>`experiments/RUN_SCHEDULE.md` | `docs/evidence/SEM-16/CHECKS.md` | Done |
| Bắt đầu | [SEM-24 — Chuẩn bị bộ xuất log và run manifest](SEM-24.md) | Vinh | `experiments/RUN_MANIFEST_TEMPLATE.json`<br>`experiments/scripts/export_logs.*`<br>`experiments/README.md` | `docs/evidence/SEM-24/CHECKS.md` | Done |
| Bắt đầu | [SEM-30 — Triển khai unique periodic work](SEM-30.md) | Trung | `android/ (periodic scheduler)` | `docs/evidence/SEM-30/CHECKS.md` | Done |
| Hoàn tất | [SEM-31 — Bàn giao chẩn đoán và tài liệu periodic](SEM-31.md) | Trung | `docs/PERIODIC.md`<br>`docs/evidence/SEM-31/SCHEDULER_CHECKS.md` | `docs/evidence/SEM-31/CHECKS.md` | Done |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-11-09 13:58:31 UTC**; mở link task nguồn để xem cập nhật mới hơn.
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

- [x] Không force-run để bù lần chạy và không gọi pilot là tập chính.
- [x] Hoàn tất sau khi có hướng dẫn chẩn đoán SEM-31 và ghi commit/config thật.
- [x] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Thực hiện ngày 07/11/2026

- [CHECKS](../../docs/evidence/SEM-29/CHECKS.md), [tái lập](../../docs/evidence/SEM-29/REPRODUCE.md), [preflight](../../docs/evidence/SEM-29/PREFLIGHT.json), [OS/cleanup](../../docs/evidence/SEM-29/OS_CHECKS.json).
- [Lượt đầu](../../experiments/runs/run-sem29-periodic-emulator-20261107/manifest.json) ABORTED vì lỗi quyền mạng Android 17, giữ log và lỗi thật.
- [Pilot emulator r2](../../experiments/runs/run-sem29-periodic-emulator-20261107-r2/manifest.json) đủ 90 phút, 5 chu kỳ periodic mới và 1 recovery setup riêng, cache nhận version 3 ở background, cleanup đạt.
- Bổ sung quyền mạng qua entrypoint app và harness androidTest để nhận/snapshot/hủy scheduler đã bàn giao.
- Android log `legacy-room-v1` được chấp nhận bàn giao SEM-36 theo phản hồi ngày 08/11. Producer canonical v2 thuộc phần tích hợp tiếp theo của Trung, OPPO thuộc SEM-42 của Trí.
- Đã đủ điều kiện nghiệm thu SEM-29 theo phạm vi cập nhật. PR chuyển Ready for review, Project sẽ được nhóm cập nhật sau merge.

## Task được mở khóa

- [SEM-36](SEM-36.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Vinh thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
