# SEM-25 — Xây Room, SyncRepository và SyncWorker dùng chung

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-29 16:22:16 UTC.
- Người thực hiện duy nhất: **Trung** (`TrungNQ2645`).
- Hạn: **2026-10-31** (UTC+7).
- Công sức: 4/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-04](SEM-04.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-23](SEM-23.md), [SEM-26](SEM-26.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-23 — Tạo scaffold Android và UI cache/timeline](SEM-23.md) | Trí | `android/ (build, manifest, ui, config)`<br>`docs/setup/ANDROID.md` | `docs/evidence/SEM-23/CHECKS.md` | Todo |
| Bắt đầu | [SEM-26 — Chốt hợp đồng API và event schema](SEM-26.md) | Tâm | `docs/API.md`<br>`docs/EVENT_SCHEMA.md` | `docs/evidence/SEM-26/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-29 16:22:16 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trung cần làm

1. Tạo data/cache và sync core; GET snapshot rồi transaction chỉ áp dụng version mới.
2. Cung cấp enqueue API chung cho MANUAL/PERIODIC/PUSH với run/source/mode/correlation.
3. Ghi event UTC/monotonic, kết quả applied/unchanged/failure; bàn giao interface dùng được cho hai trigger.

## Đầu ra bắt buộc

- `android/ (data và sync core)`
- `docs/SYNC_CORE_API.md`
- `docs/evidence/SEM-25/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Manual enqueue chạy được worker, cache sống qua mở lại/offline và version không giảm.
- [ ] Periodic/push gọi cùng worker; UI không tạo engine hoặc auto-fetch riêng.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-28](SEM-28.md) cần đầu ra này để **bắt đầu**.
- [SEM-30](SEM-30.md) cần đầu ra này để **bắt đầu**.
- [SEM-32](SEM-32.md) cần đầu ra này để **bắt đầu**.
- [SEM-39](SEM-39.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trung thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
