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
| API response contract | Header/body v2, ETag, integer/version/item order/limits được xác minh trước apply | Strict validation đã thêm; current server checkout v1 sẽ bị từ chối đúng như contract | Pass (code review), E2E chờ SEM-27 |
| Retry transient | Tối đa 3 lượt retry sau initial attempt | Worker phân loại theo `runAttemptCount`, hết hạn ghi failure | Pass (code review) |
| Shared trigger API | PERIODIC/MANUAL/PUSH route to same SyncWorker with source/mode/run/correlation | `SyncWorkEnqueuer` routes all 3; legacy SEM-23/32 producers still enqueue inline pending integration | Pass (API available), producer adoption pending |
| Manual/cache sống qua process restart/offline | Enqueue chạy worker; Room còn cache khi mở lại | Sẽ chạy trong M1/pilot runs | Bàn giao downstream |
| Build Android | Build thành công | Build thành công: assembleDebug (54s) và testDebugUnitTest (1m 48s) PASS 100% khi nhóm trưởng review | Pass (host review) |

Commit: merge commit `25171b8c80234794332b2f1d142867c7d3f4e37d` ([PR #10](https://github.com/ThanhTris/Seminar-IE307/pull/10)).
Config: WorkManager 2.12.0, Room 2.8.5.
Client đã chuyển sang yêu cầu API v2.0 header/body và strict snapshot validation; server v2 sẽ được đồng bộ khi SEM-27 hoàn tất.
Trạng thái task SEM-25 trên GitHub Project 3 đã được cập nhật sang **Done** (item `PVTI_lAHOCnL5Fs4BpUDUzhEiXF0`).

**Kết luận:** Code core, Room transaction guard và WorkEnqueuer đã được xác minh biên dịch và pass unit test 100% trong quá trình review; task đã được nghiệm thu và đánh dấu Done.
