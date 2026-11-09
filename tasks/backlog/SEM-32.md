# SEM-32 — Triển khai callback FCM và enqueue sync

- Trạng thái: **Done** (Project).
- Trạng thái đầu vào: **Đã hoàn thành**.
- Đối chiếu Project: 2026-11-09 15:41:01 UTC.
- Người thực hiện duy nhất: **Trang** (`rosy179`).
- Hạn: **02/11/2026 18:00 (UTC+7)**.
- Công sức: 4/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-06](SEM-06.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-15](SEM-15.md), [SEM-25](SEM-25.md), [SEM-28](SEM-28.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-15 — Giải thích cơ chế silent push và giới hạn FCM](SEM-15.md) | Trang | `docs/mechanisms/SILENT_PUSH.md` | `docs/evidence/SEM-15/CHECKS.md` | Done |
| Bắt đầu | [SEM-25 — Xây Room, SyncRepository và SyncWorker dùng chung](SEM-25.md) | Trung | `android/ (data và sync core)`<br>`docs/SYNC_CORE_API.md` | `docs/evidence/SEM-25/CHECKS.md` | Done |
| Bắt đầu | [SEM-28 — Ghép manual sync đầu cuối và chốt hướng dẫn setup](SEM-28.md) | Trí | `docs/SETUP.md`<br>`docs/ENVIRONMENT.md`<br>`docs/evidence/SEM-28/M1.md` | `docs/evidence/SEM-28/CHECKS.md` | Done |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-11-09 15:41:01 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trang cần làm

1. Thêm FirebaseMessagingService nhận data-only v1, ghi push_received rồi enqueue worker chung.
2. Parse run/version/message correlation, xử lý payload thiếu/sai; không sync dài ngay trong callback.
3. Giữ normal priority và không tạo thông báo hiển thị trong demo.

## Đầu ra bắt buộc

- `android/ (messaging callback và enqueue adapter)`
- `docs/evidence/SEM-32/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [x] Callback dẫn tới work_enqueued/start/applied theo correlation khi đủ điều kiện.
- [x] Không dùng high priority/EAP hoặc engine riêng để che độ trễ.
- [x] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Đầu ra đã soát ngày 08/11/2026

- `android/app/src/main/java/com/thanhtris/seminarie307/fcm/BulletinFirebaseMessagingService.kt`
- `android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushSyncEnqueueAdapter.kt`
- `android/app/src/main/java/com/thanhtris/seminarie307/sync/SyncWorkEnqueuer.kt`
- `android/app/src/test/java/com/thanhtris/seminarie307/fcm/PushSyncEnqueueAdapterTest.kt`
- [CHECKS SEM-32](../../docs/evidence/SEM-32/CHECKS.md)

## Task được mở khóa

- [SEM-33](SEM-33.md) cần đầu ra này để **bắt đầu**.
- [SEM-34](SEM-34.md) cần đầu ra này để **bắt đầu**.
- [SEM-36](SEM-36.md) cần đầu ra này để **bắt đầu**.
- [SEM-38](SEM-38.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trang thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
