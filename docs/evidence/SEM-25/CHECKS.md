# SEM-25 CHECKS — Room và shared sync core

## Đầu ra

- Android data/sync core: `android/app/src/main/java/com/thanhtris/seminarie307/{data,sync,integration}`.
- Shared trigger API: [`SyncWorkEnqueuer.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/sync/SyncWorkEnqueuer.kt).
- Contract: [SYNC_CORE_API.md](../../SYNC_CORE_API.md).

## Kiểm tra

| Hạng mục | Expected | Actual | Trạng thái |
|---|---|---|---|
| Version mới hơn | Cache/items/metadata/event commit trong Room transaction | Version guard nằm trong transaction; metadata cachedVersion được dùng kể cả snapshot rỗng | Pass (code review) |
| Version bằng cache | Không ghi đè items; ghi unchanged | Có nhánh unchanged, cập nhật lastSyncAtUtc | Pass (code review) |
| Version thấp hơn cache | Không giảm cache | Nhánh stale không thay items/version | Pass (code review) |
| API response contract | Header/body v2, ETag, integer/version/item order/limits được xác minh trước apply | Strict validation đã thêm; current server checkout v1 sẽ bị từ chối đúng như contract | Pass (code review), E2E Not run |
| Retry transient | Tối đa 3 lượt retry sau initial attempt | Worker phân loại theo `runAttemptCount`, hết hạn ghi failure | Pass (code review) |
| Shared trigger API | PERIODIC/MANUAL/PUSH route to same SyncWorker with source/mode/run/correlation | `SyncWorkEnqueuer` routes all 3; legacy SEM-23/32 producers still enqueue inline pending integration | Pass (API available), producer adoption pending |
| Manual/cache sống qua process restart/offline | Enqueue chạy worker; Room còn cache khi mở lại | Chưa chạy app/build/device | Not run |
| Build Android | Build thành công | Chưa chạy; Android SDK/ADB không được cấu hình trong workspace host | Not run |

Commit: working tree hiện tại, chưa commit. Config: WorkManager 2.12.0, Room 2.8.5; Android SDK/ADB không hiện diện trong host environment. Evidence runtime: SEM-28 M1 report có sẵn từ build cũ, nhưng code này chưa build lại. Client đã chuyển sang yêu cầu API v2.0 header/body và strict snapshot validation; server code hiện checkout còn là v1 nên end-to-end cần SEM-27 nâng cấp. Timeline Room chưa có serializer đầy đủ schema sự kiện 2.0.0, nên exporter/run main vẫn chưa thể dùng từ Android client.

**Kết luận:** code core đã được cập nhật và rà soát tĩnh; chưa xác minh build hoặc behavior runtime, không đánh dấu Done.
