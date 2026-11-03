# Sync Core API — SEM-25

## Trách nhiệm

`SyncRepository.executeSync(SyncInput)` là đường đồng bộ chung: đọc version cache, gọi `SnapshotRemoteDataSource`, kiểm version lại trong Room transaction rồi trả `SyncResult`. Manual, periodic và push chỉ khác phần enqueue/input; không tự tạo nhánh ghi cache riêng.

`SyncWorker` giải mã `source`, `mode`, `run_id`, correlation IDs và `version_hint`. Input thiếu hoặc không hợp lệ bị từ chối; worker không tự tạo run giả. MANUAL được phép trong mọi mode; PERIODIC chỉ ở PERIODIC/HYBRID; PUSH chỉ ở PUSH/HYBRID. Worker nhận WorkManager `id`/`runAttemptCount`, gọi repository và ánh xạ applied/unchanged/stale thành success, lỗi tạm thời thành retry, lỗi cuối thành failure.

`SyncWorkEnqueuer.enqueue(SyncInput)` là API chung cho ba source: PERIODIC được chuyển sang unique periodic scheduler; MANUAL/PUSH tạo one-time request cùng worker, cùng network constraint và cùng correlation fields. API trả WorkManager ID thật sau khi Operation hoàn tất. Các producer SEM-23/32 hiện còn enqueue inline; có thể chuyển sang API này khi họ ghép module để tránh ghi `work_enqueued` hai lần.

## Kiểu dữ liệu

```kotlin
data class SyncInput(
    val source: SyncSource,
    val mode: SyncMode,
    val runId: String,
    val versionHint: Long? = null,
    val workAttempt: Int = 0,
    val correlation: CorrelationUi = CorrelationUi(),
)

enum class SyncOutcomeType { APPLIED, UNCHANGED, STALE, RETRY, FAILURE }

data class SyncResult(
    val outcome: SyncOutcomeType,
    val reason: String,
    val version: Long? = null,
)
```

`versionHint` chỉ là gợi ý; repository vẫn GET snapshot hiện hành. `requestId` nối các event của một logical sync; `workId` là UUID WorkManager; `messageId` chỉ được giữ nếu FCM thật cung cấp.

Manual/PUSH producer phải cấp request ID và giữ nó trong `WorkRequest` input qua retry. Periodic request có cùng `workId` qua các chu kỳ, nên worker lưu request ID chu kỳ hiện tại trong Room; retry đọc lại ID đó, lượt chu kỳ mới (`runAttemptCount == 0`) tạo ID mới. Đây là correlation local; runtime cần được kiểm chứng trên WorkManager bản đã pin trước run chính.

## Quy tắc cache và transaction

1. Cache version guard đọc giá trị lớn nhất hợp lệ giữa `sync_metadata.cachedVersion` và version lớn nhất của item rows. Cách này giữ được version của snapshot rỗng và tránh hạ cache khi metadata cũ hơn rows.
2. Gửi `If-None-Match: "v<cachedVersion>"` khi có version và gửi request ID trong header correlation. Client yêu cầu response API major 2; 304 phải giữ ETag đúng cached version.
3. HTTP 200: trong một `RoomDatabase.withTransaction`, đọc lại version mới nhất (metadata trước, rows sau). Nếu response mới hơn, thay item rows, cập nhật `cachedVersion`/`lastSyncAtUtc` và ghi applied event trong transaction.
4. Nếu bằng version, không ghi lại item rows; cập nhật thời điểm sync và ghi unchanged.
5. Nếu cũ hơn, không thay cache và ghi stale.
6. HTTP 304 chỉ được chấp nhận khi local cache có version; 304 nhưng chưa có cache là invalid response.
7. HTTP 200 chỉ được chấp nhận nếu body/header API version khớp, snapshot có đúng các trường hợp đồng, version là integer an toàn, ETag khớp body, item ID/version duy nhất, version sắp giảm dần và title/body trong giới hạn. Version 0 chỉ hợp lệ với items rỗng.
8. Room Flow là nguồn dữ liệu UI. Mở màn hình không cần tạo fetch engine riêng.

Compare-and-apply nằm sau network fetch trong transaction. Vì vậy hai worker có thể fetch song song, nhưng response cũ đến sau sẽ so với version đã commit mới nhất và không thể hạ cache.

## Lỗi và retry

- HTTP 408/429/5xx và lỗi I/O được phân loại transient; reason log dùng mã an toàn (`HTTP_ERROR`, `NETWORK_ERROR`), không chứa error body/exception.
- HTTP response không transient và payload không hợp lệ dừng bằng failure, không retry vô hạn. Error body, exception text và URL không được ghi vào timeline.
- Tối đa 3 lượt `Result.retry()` sau lượt đầu. WorkManager áp dụng backoff mặc định; khi hết lượt, timeline ghi failure với `RETRY_EXHAUSTED`.
- App/server có thể thay đổi response contract; payload sai schema không được apply.

## WorkManager API

| Thành phần | Hành vi |
|---|---|
| `SyncWorker.KEY_SOURCE` | `MANUAL`, `PERIODIC`, `PUSH` |
| `SyncWorker.KEY_MODE` | `PERIODIC`, `PUSH`, `HYBRID` |
| `SyncWorker.KEY_RUN_ID` | Run ID thật, bắt buộc |
| `SyncWorker.KEY_REQUEST_ID` | Logical request ID nếu producer đã có |
| `SyncWorker.KEY_MESSAGE_ID` | FCM ID opaque nếu có |
| `SyncWorker.KEY_VERSION_HINT` | Version hint từ push; không chứng minh applied |
| Result output | `outcome`, `version` |

Periodic lifecycle, unique name, interval validation, cancel/query: [`PeriodicSyncScheduler`](../android/app/src/main/java/com/thanhtris/seminarie307/sync/PeriodicSyncScheduler.kt). Scheduler request không đồng nghĩa worker start.

## Timestamps và event contract

Runtime timeline hiện giữ UTC (`Instant`) và Android monotonic `SystemClock.elapsedRealtime()` cho local event; Room transaction lưu event cùng với snapshot apply. Chi tiết periodic source/start/apply đọc ở [EVENT_SCHEMA.md](EVENT_SCHEMA.md).

**Tích hợp còn mở trước run main:** Room `TimelineEventEntity` hiện là dạng legacy 1.0 (event ID, source, type, UTC/epoch, run/version, outcome/reason, request/work/message ID, elapsed time). Chưa có serializer/runtime event đầy đủ cho schema phẳng 2.0.0, bao gồm `origin`, `device_alias`, `boot_session_id`, `work_attempt`, `network_call_id`, `signal_ids`, HTTP status/provider reason và cặp fetch started/completed. Không xuất/nhập log main như schema 2.0 cho tới khi adapter và migration của các producer/consumer được hoàn tất. Không điền placeholder thành dữ liệu thật. Snapshot client hiện yêu cầu API major 2; server trong checkout vẫn là v1 và cần SEM-27 nâng cấp trước khi end-to-end hoạt động.

## Kiểm chứng

Các sửa code hiện được rà soát tĩnh, nhưng build, migration và manual/offline runtime chưa chạy. Xem [SEM-25 CHECKS](evidence/SEM-25/CHECKS.md); đây không phải xác nhận runtime/schema v2 đã được nghiệm thu.
