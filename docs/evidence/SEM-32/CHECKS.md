# SEM-32 — CHECKS Kiểm tra và Bàn giao FCM Callback & Enqueue Sync

## 1. Nhận dạng Lần kiểm

- **Người thực hiện:** Trang (`rosy179`).
- **Nhiệm vụ:** [SEM-32](../../../tasks/backlog/SEM-32.md) — Triển khai callback FCM và enqueue sync.
- **Thuộc đề tài:** Seminar IE307 (Chủ đề 12: *Xử lý việc tìm nạp nền và thông báo đẩy im lặng, minh họa trên Android*).
- **Ngày lập và kiểm tra:** **08/11/2026 – 09/11/2026 (UTC+7)**.
- **Hạn được giao trong kế hoạch:** **02/11/2026 18:00 (UTC+7)**.
- **Base commit được kiểm:** `923da834c9c228833946eb2491a133465b0c9502` (`main`, sau khi merge SEM-29 PR #19).
- **Nhánh làm việc:** `codex/SEM-32-fcm-callback`.
- **Pull Request liên kết:** [PR #20](https://github.com/ThanhTris/Seminar-IE307/pull/20).
- **Môi trường máy host:**
  - OS: Windows 11 x64 (Build 26100).
  - JDK: Java 23 (`C:\Program Files\Java\jdk-23`), JVM bytecode target 17.
  - Gradle: `9.6.0` (Gradle Wrapper, checksum khóa trong `gradle-wrapper.properties`).
  - AGP: `9.4.1`, Kotlin: `2.4.10`, Compose Compiler: `2.4.10`.
  - Android SDK: API 37 (`compileSdk = 37`, `targetSdk = 37`, `minSdk = 24`).
  - Thư viện cốt lõi: WorkManager `2.12.0`, Room `2.8.5`, Firebase Android BoM `35.1.0` (`firebase-messaging`).
- **Đầu ra bàn giao:**
  - `android/app/src/main/java/com/thanhtris/seminarie307/fcm/BulletinFirebaseMessagingService.kt`
  - `android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushSyncEnqueueAdapter.kt`
  - `android/app/src/main/java/com/thanhtris/seminarie307/sync/SyncWorkEnqueuer.kt`
  - `android/app/src/test/java/com/thanhtris/seminarie307/fcm/PushSyncEnqueueAdapterTest.kt`
  - `android/app/build.gradle.kts`
  - `android/app/src/main/AndroidManifest.xml`
  - Hồ sơ kiểm tra & nghiệm thu: `docs/evidence/SEM-32/CHECKS.md`

---

## 2. Đầu vào Đã nhận và Đối chiếu

Theo [nhiệm vụ SEM-32](../../../tasks/backlog/SEM-32.md), task cần nhận đủ 3 đầu ra nền tảng trước khi bắt đầu và hoàn tất:

1. **[SEM-15](../../../tasks/backlog/SEM-15.md) (Trang bàn giao):** [SILENT_PUSH.md](../../../docs/mechanisms/SILENT_PUSH.md) và [CHECKS SEM-15](../SEM-15/CHECKS.md) — Đặc tả cơ chế Silent Push, mô hình Ingest & Offload, nguyên tắc cấm notification UI, giới hạn thực thi nền (< 50ms callback) và blueprint triển khai FirebaseMessagingService.
2. **[SEM-25](../../../tasks/backlog/SEM-25.md) (Trung bàn giao):** [SYNC_CORE_API.md](../../../docs/SYNC_CORE_API.md) và [CHECKS SEM-25](../SEM-25/CHECKS.md) — Tầng Room database, SyncRepository, SyncWorker dùng chung và bộ điều phối [SyncWorkEnqueuer.kt](../../../android/app/src/main/java/com/thanhtris/seminarie307/sync/SyncWorkEnqueuer.kt) cho 3 nguồn MANUAL, PERIODIC, PUSH.
3. **[SEM-28](../../../tasks/backlog/SEM-28.md) (Trí bàn giao):** [SETUP.md](../../../docs/SETUP.md), [ENVIRONMENT.md](../../../docs/ENVIRONMENT.md), [M1.md](../SEM-28/M1.md) và [CHECKS SEM-28](../SEM-28/CHECKS.md) — Thiết lập môi trường đầu cuối M1, xác nhận liên kết UI Gateway và server snapshot v2.

---

## 3. Tiêu chí và Kết quả Kiểm tra Chi tiết

| STT | Yêu cầu kiểm tra | Kết quả mong đợi (Expected) | Bằng chứng thực tế (Actual / Evidence) | Đánh giá |
|:---:|---|---|---|:---:|
| 1 | **Nhận data-only v1 và loại trừ notification** | Chỉ chấp nhận payload data-only; từ chối hoặc bỏ qua payload chứa khối UI notification | `PushSyncEnqueueAdapter` kiểm tra `hasNotificationPayload`: nếu có khối notification, ghi warning và trả về `Ignored("NOTIFICATION_PAYLOAD_NOT_ALLOWED")`, không tạo UI banner hay notification | **Pass** |
| 2 | **Không sync dài trong callback** | Hàm `onMessageReceived` hoàn tất ngay (< 50ms), không gọi Retrofit/OkHttp trực tiếp | Callback chuyển việc xử lý sang Coroutine IO scope, không thực hiện network GET; trả quyền kiểm soát ngay để nhả Wakelock | **Pass** |
| 3 | **Ghi nhận sự kiện `push_received` tức thì** | Ghi nhận event `push_received` vào Room DB ngay khi nhận callback hợp lệ | Lưu Room `TimelineEventEntity` với `eventType = "push_received"`, `outcome = "received"`, UTC ISO 8601, monotonic `elapsedRealtimeMillis`, `version_hint`, `requestId`, `messageId` | **Pass** |
| 4 | **Trích xuất và bảo toàn Correlation IDs** | Chuyển tiếp đầy đủ `run_id`, `request_id`, `version_hint`, `message_id` sang Worker | Trích xuất và validate `APP_ID_PATTERN` (`^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$`); truyền qua `CorrelationUi` và `SyncInput` vào `SyncWorkEnqueuer` | **Pass** |
| 5 | **Xử lý payload thiếu/sai** | `run_id` rỗng hoặc sai cú pháp bị từ chối; không tạo event có run giả mạo | Trả về `Rejected("INVALID_PAYLOAD", runId = null)`, không ghi nhận bản ghi rác vào bảng timeline theo chuẩn EVENT_SCHEMA 2.0.0 | **Pass** |
| 6 | **Kiểm soát chế độ hoạt động (Mode Guard)** | Nếu thiết bị đang ở chế độ không cho phép push (ví dụ `PERIODIC`), ghi nhận `trigger_rejected` và không enqueue | Kiểm tra `metadataDao.getValue("mode")`: nếu là `PERIODIC`, ghi `push_received` (quan sát được), tiếp theo ghi `trigger_rejected` với reason `MODE_DISABLED`, không xếp lịch worker | **Pass** |
| 7 | **Bàn giao sang `SyncWorkEnqueuer` dùng chung** | Enqueue `OneTimeWorkRequestBuilder<SyncWorker>` qua WorkEnqueuer thống nhất | Gọi `SyncWorkEnqueuer.enqueue(syncInput)`: áp dụng ràng buộc mạng `NetworkType.CONNECTED`, ghi `work_enqueued` kèm UUID `workId` thật | **Pass** |
| 8 | **Không dùng High Priority / EAP để che độ trễ** | Giữ Normal Priority tự nhiên, không lách Doze Mode | Tuân thủ cấu hình Normal Priority từ `fcm-sender.js` (SEM-35), không dùng Foreground Service hay Exact Alarm | **Pass** |
| 9 | **Quản lý Token Refresh** | `onNewToken` lưu FCM token mới vào Room metadata | `BulletinFirebaseMessagingService.onNewToken` lưu `SyncMetadataEntity("fcmToken", token)` trong Room DB | **Pass** |
| 10 | **Kiểm thử Unit Tests (JVM)** | Suite unit test bao phủ toàn bộ nhánh logic của adapter | `PushSyncEnqueueAdapterTest.kt` bao phủ 6 ca kiểm thử. Đã cập nhật theo review của nhóm trưởng: sửa nullable map `String?` và bật `unitTests.isReturnDefaultValues = true`. Toàn bộ test suite PASS 100% | **Pass** |
| 11 | **Kiểm thử thực nghiệm trên thiết bị thật / Emulator** | Đo độ trễ push thực tế trên môi trường thiết bị | SEM-32 là task triển khai callback và adapter code. Thao tác chạy pilot push E02 và đo đạc thuộc về SEM-34 (Vinh) | **Not run** (Theo phân công) |

---

## 4. Xử lý Đóng góp từ Code Review (PR #20 Review Feedback)

Theo [Pull Request Review #20](https://github.com/ThanhTris/Seminar-IE307/pull/20#pullrequestreview-5822425988) từ nhóm trưởng `ThanhTris`, hai vấn đề sau đã được rà soát và điều chỉnh triệt để:

1. **Lỗi biên dịch Kotlin (Type Mismatch trong Unit Test):**
   - *Nguyên nhân:* `SyncMetadataEntity.value` có kiểu nullable `String?`, nhưng `FakeSyncMetadataDao.map` khai báo kiểu không nullable `mutableMapOf<String, String>()`.
   - *Khắc phục:* Đổi khai báo thành `val map = mutableMapOf<String, String?>()` tại dòng 210 trong [`PushSyncEnqueueAdapterTest.kt`](../../../android/app/src/test/java/com/thanhtris/seminarie307/fcm/PushSyncEnqueueAdapterTest.kt).
2. **Lỗi chạy Unit Test trên JVM máy host (Android platform classes not mocked):**
   - *Nguyên nhân:* Khi chạy unit test JVM thuần, các lệnh gọi `android.util.Log` và `android.os.SystemClock.elapsedRealtime()` ném ngoại lệ `RuntimeException at Log.java:-1 / SystemClock.java:-1` do chưa mock phương thức nền tảng Android.
   - *Khắc phục:* Thêm `unitTests.isReturnDefaultValues = true` vào khối `testOptions` trong [`android/app/build.gradle.kts`](../../../android/app/build.gradle.kts). Nhờ đó, AGP tự động trả về giá trị mặc định cho các API Android thay vì ném ngoại lệ.

---

## 5. Bàn giao Đầu ra cho các Task Downstream

Đầu ra của SEM-32 mở khóa trực tiếp các nhiệm vụ kế thừa:

1. **[SEM-33](../../../tasks/backlog/SEM-33.md) (Trang — Token refresh và bàn giao PUSH.md):**
   - Kế thừa `onNewToken` và `fcmToken` trong `SyncMetadataEntity` để xây dựng luồng đăng ký token với server.
   - Soạn thảo tài liệu hướng dẫn kỹ thuật `docs/PUSH.md`.
2. **[SEM-34](../../../tasks/backlog/SEM-34.md) (Vinh — Chạy pilot push E02 và xác nhận cache nền):**
   - Sử dụng `BulletinFirebaseMessagingService` và `PushSyncEnqueueAdapter` để nhận tín hiệu push từ CLI SEM-35 trên máy ảo/thiết bị thật.
   - Đo đạc độ trễ và tỷ lệ thành công của silent push trong ca thử nghiệm E02.
3. **[SEM-36](../../../tasks/backlog/SEM-36.md) (Trung — Tích hợp ba mode và pilot hybrid):**
   - Tích hợp luồng enqueue của PUSH với PERIODIC và MANUAL trong mô hình HYBRID.
4. **[SEM-38](../../../tasks/backlog/SEM-38.md) (Trang — Xử lý duplicate và version hint của push):**
   - Phát triển tiếp bộ lọc version hint và deduplication trên nền tảng adapter đã dựng.

---

## 6. Kết luận Nghiệm thu

- Toàn bộ các yêu cầu của SEM-32 và các phản hồi từ review của nhóm trưởng đã được hiện thực đầy đủ, chuẩn xác theo kiến trúc Ingest & Offload.
- `PushSyncEnqueueAdapter` và `BulletinFirebaseMessagingService` liên kết hoàn chỉnh với `SyncWorkEnqueuer`.
- Bộ unit test suite `PushSyncEnqueueAdapterTest` đã được hiệu chỉnh sạch lỗi type và sẵn sàng cho quá trình merge PR #20.
