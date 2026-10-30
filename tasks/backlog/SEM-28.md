# SEM-28 — Ghép manual sync đầu cuối và chốt hướng dẫn setup

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-30 12:33:46 UTC.
- Người thực hiện duy nhất: **Trí** (`ThanhTris`).
- Hạn: **31/10/2026 22:00 (UTC+7)**.
- Công sức: 1/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-05](SEM-05.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-23](SEM-23.md), [SEM-24](SEM-24.md), [SEM-25](SEM-25.md), [SEM-27](SEM-27.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-23 — Tạo scaffold Android và UI cache/timeline](SEM-23.md) | Trí | `android/ (build, manifest, ui, config)`<br>`docs/setup/ANDROID.md` | `docs/evidence/SEM-23/CHECKS.md` | Todo |
| Bắt đầu | [SEM-24 — Chuẩn bị bộ xuất log và run manifest](SEM-24.md) | Vinh | `experiments/RUN_MANIFEST_TEMPLATE.json`<br>`experiments/scripts/export_logs.*`<br>`experiments/README.md` | `docs/evidence/SEM-24/CHECKS.md` | Todo |
| Bắt đầu | [SEM-25 — Xây Room, SyncRepository và SyncWorker dùng chung](SEM-25.md) | Trung | `android/ (data và sync core)`<br>`docs/SYNC_CORE_API.md` | `docs/evidence/SEM-25/CHECKS.md` | Todo |
| Bắt đầu | [SEM-27 — Triển khai server snapshot và CLI cập nhật](SEM-27.md) | Tâm | `server/ (API, snapshot store, update CLI)`<br>`docs/setup/SERVER.md` | `docs/evidence/SEM-27/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-30 12:33:46 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trí cần làm

1. Nhận app/server/core/exporter đã bàn giao và nối nút manual với enqueue.
2. Chạy một luồng update → manual worker → Room → UI/timeline, mở lại offline.
3. Tổng hợp SETUP và ENVIRONMENT dạng chỉ mục từ ba hồ sơ môi trường cùng tài liệu Android/server; ghi M1 và revision đã ghép.

## Đầu ra bắt buộc

- `docs/SETUP.md`
- `docs/ENVIRONMENT.md`
- `docs/evidence/SEM-28/M1.md`
- `docs/evidence/SEM-28/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Build debug/server chạy; MANUAL có nhãn và UI mở lại không phát sinh GET.
- [ ] M1 chỉ Pass khi có run thật; thiếu credential/mạng ghi blocker, không tự nghiệm thu từ tài liệu.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-30](SEM-30.md) cần đầu ra này để **bắt đầu**.
- [SEM-32](SEM-32.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trí thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
