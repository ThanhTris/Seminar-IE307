# SEM-38 — CHECKS Xử lý duplicate và version hint của push

## 1. Nhận dạng lần kiểm

- **Người thực hiện:** Trang (`rosy179`).
- **Nhiệm vụ:** [SEM-38](../../../tasks/backlog/SEM-38.md) — Xử lý duplicate và version hint của push.
- **Ngày lập và kiểm tra:** **09/11/2026 (UTC+7)**.
- **Base commit:** `abcfc89` (`origin/main`, đã merge SEM-32 PR #20 và SEM-33 PR #22; SEM-38 ở trạng thái **Sẵn sàng**).
- **Nhánh làm việc:** `codex/SEM-38-push-input-policy`.
- **Môi trường máy kiểm:**
  - OS: Windows 11 x64, JDK 23 (`C:\Program Files\Java\jdk-23`, bytecode target JVM 17).
  - Compiler & test runner local: Kotlin `2.1.20` (`K2JVMCompiler`) + `kotlinx-coroutines-core-jvm:1.9.0` + `junit:4.13.2` chạy trực tiếp bộ test messaging (`PushInputPolicyTest`, `PushSyncEnqueueAdapterTest`, `FcmTokenManagerTest` — tổng **29/29 test PASS**, 373 ms).
  - **Giới hạn host:** Máy không cài Android SDK (`ANDROID_HOME` chưa đặt) và chưa có cấu hình Firebase thật (blocker B1 từ SEM-13/SEM-33/SEM-35), nên lệnh Gradle AGP đầy đủ (`./gradlew :app:testDebugUnitTest`, `:app:assembleDebug`) và chạy thực nghiệm E05 trên emulator/thiết bị được ghi **Not run**.
- **Đầu ra bàn giao:**
  - `android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushInputPolicy.kt` (mới — chính sách input thuần Kotlin)
  - `android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushSyncEnqueueAdapter.kt` (cập nhật tích hợp `PushInputPolicy` và `Mutex` chống race callback)
  - `android/app/src/test/java/com/thanhtris/seminarie307/fcm/PushInputPolicyTest.kt` (mới — 15 unit test cho 3 nhóm ca A/B/C và ledger)
  - `docs/EVENT_SCHEMA.md` (bổ sung mã reason delta `DUPLICATE_SIGNAL` vào registry)
  - [`docs/evidence/SEM-38/PUSH_INPUT_CASES.md`](PUSH_INPUT_CASES.md) (ma trận ca kiểm duplicate / stale hint / new-during-sync và giới hạn chuyển giao)
  - `docs/evidence/SEM-38/CHECKS.md` (tài liệu này)

---

## 2. Đầu vào đã nhận và đối chiếu

| Task nguồn | Đầu ra đã nhận | Trạng thái trên Project | Cách kế thừa trong SEM-38 |
|---|---|---|---|
| [SEM-32](../../../tasks/backlog/SEM-32.md) | [`BulletinFirebaseMessagingService.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/BulletinFirebaseMessagingService.kt), [`PushSyncEnqueueAdapter.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushSyncEnqueueAdapter.kt), [CHECKS SEM-32](../SEM-32/CHECKS.md) | Done | Mở rộng `PushSyncEnqueueAdapter.processPushPayload` với chính sách lọc redelivery, giữ nguyên cổng `SyncWorkEnqueuer` dùng chung |
| [SEM-33](../../../tasks/backlog/SEM-33.md) | [`FcmTokenManager.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/FcmTokenManager.kt), [`docs/PUSH.md`](../../PUSH.md), [CHECKS SEM-33](../SEM-33/CHECKS.md) | Done | Đối chiếu luồng nhận silent push, cấu trúc payload sender (`signal_id`, `version_hint`, `run_id`, `mode`) và ranh giới sự kiện |
| [SEM-39](../../../tasks/backlog/SEM-39.md) (tham chiếu ranh giới core) | [`CORE_CASES.md`](../SEM-39/CORE_CASES.md), [CHECKS SEM-39](../SEM-39/CHECKS.md) | Done | Giữ nguyên `SyncRepository`, Room transaction và version guard của core; không viết lại logic so sánh version ở tầng messaging |

---

## 3. Tóm tắt Diff Messaging bàn giao

1. **Thêm [`PushInputPolicy.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushInputPolicy.kt):**
   - Tạo khóa nhận diện redelivery theo phạm vi `run_id`: `"$runId|sig|$signalId"` (khi `signal_id` hợp lệ theo `APP_ID_PATTERN`) và `"$runId|msg|$messageId"` (khi FCM `message_id` dài 1..512 ký tự, không chứa khoảng trắng).
   - Lưu sổ cái (ledger) tối đa `MAX_LEDGER_ENTRIES = 64` khóa mới nhất trong Room `sync_metadata` dưới khóa `pushSeenSignalKeys` để sống sót qua process death.
   - Chỉ ghi nhận vào ledger **sau khi `enqueueWork(syncInput)` trả về `workId != null`**, đảm bảo nếu WorkManager lỗi thì lần retry cùng `signal_id` vẫn được xử lý.
2. **Cập nhật [`PushSyncEnqueueAdapter.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushSyncEnqueueAdapter.kt):**
   - Bọc bước `đọc ledger → kiểm tra duplicate → gọi enqueueWork → cập nhật ledger` trong `ledgerLock: Mutex` dùng chung để chống race khi nhiều callback trùng tới đồng thời.
   - Khi phát hiện redelivery (`PushInputPolicy.isDuplicate`), vẫn giữ bản ghi `push_received` (vì callback thực sự đã xảy ra), sau đó ghi `trigger_rejected` với `outcome = "rejected"`, `reason = "DUPLICATE_SIGNAL"`, và trả về `PushProcessingResult.Rejected("DUPLICATE_SIGNAL", runId)` mà không gọi `enqueueWork` lần hai.
   - **Không lọc bỏ theo `version_hint`:** Payload có `version_hint` nhỏ hơn hoặc bằng `cachedVersion` vẫn được chuyển qua `enqueueWork` với đầy đủ `versionHint`, `requestId`, `messageId` để `SyncWorker` thực hiện HTTP GET snapshot hiện hành và để version guard của `SyncRepository` (SEM-39) quyết định `applied` / `unchanged` / `stale`.
   - **Không chặn tín hiệu mới khi worker đang chạy:** Tín hiệu mang `signal_id` / `message_id` mới luôn được enqueue qua `SyncWorkEnqueuer` dùng chung.
3. **Cập nhật [`docs/EVENT_SCHEMA.md`](../../EVENT_SCHEMA.md):**
   - Ghi nhận delta `DUPLICATE_SIGNAL` vào danh mục `reason` tối thiểu cho sự kiện `trigger_rejected` khi phát hiện push redelivery.

---

## 4. Kết quả Kiểm tra Chi tiết (Expected / Actual)

| STT | Hạng mục kiểm tra | Expected | Actual / Evidence | Kết quả |
|:---:|---|---|---|:---:|
| 1 | **Tín hiệu trùng (Case A — Duplicate signal / message redelivery)** | Cùng `run_id` + (`signal_id` hoặc `message_id`) đã enqueue: ghi `push_received` + `trigger_rejected` (`DUPLICATE_SIGNAL`), chỉ enqueue 1 lần; không tạo notification hay sync engine riêng | 10 unit test nhóm A trong [`PushInputPolicyTest.kt`](../../../android/app/src/test/java/com/thanhtris/seminarie307/fcm/PushInputPolicyTest.kt) (A1–A9, gồm cả 4 callback đồng thời và khôi phục ledger sau khi tạo adapter mới) đều **PASS** | **Pass** (unit test JVM) |
| 2 | **Hint cũ hoặc lặp (Case B — Stale / equal / repeated `version_hint`)** | Không loại bỏ tín hiệu ở tầng messaging khi `version_hint <= cachedVersion`; giữ nguyên `versionHint` trong `SyncInput` và bàn giao cho worker GET snapshot hiện hành | `hintOlderOrEqualToCacheIsStillEnqueuedBecauseWorkerFetchesCurrentSnapshot` và `repeatedHintWithNewSignalIdIsEnqueued` **PASS**; không sinh `trigger_rejected` | **Pass** (unit test JVM) |
| 3 | **Tín hiệu mới khi worker đang chạy/chờ (Case C — New signal during sync)** | Tín hiệu có `signal_id`/`message_id` mới luôn được enqueue qua `SyncWorkEnqueuer` dùng chung, sinh `workId` mới và không bị bỏ qua | `newerSignalWhileEarlierWorkIsPendingIsEnqueuedNotSkipped` **PASS** (2 lượt enqueue với `versionHint` 6 và 7, `workId` khác nhau) | **Pass** (unit test JVM) |
| 4 | **Không viết lại transaction / version guard của core** | Không chạm vào `SyncRepository.kt`, `SyncWorker.kt`, `SyncWorkEnqueuer.kt`; lỗi thuộc core chuyển về SEM-39 | `git diff` xác nhận chỉ sửa `fcm/PushSyncEnqueueAdapter.kt` và thêm `fcm/PushInputPolicy.kt`; ranh giới với [SEM-39](../SEM-39/CORE_CASES.md) được ghi rõ trong [`PUSH_INPUT_CASES.md`](PUSH_INPUT_CASES.md) | **Pass** |
| 5 | **Hồi quy các suite FCM hiện có (SEM-32 & SEM-33)** | Không làm hỏng test callback/adapter SEM-32 và token lifecycle SEM-33 | Chạy JUnit 4.13.2 trên JDK 23: `PushInputPolicyTest` (15), `PushSyncEnqueueAdapterTest` (6), `FcmTokenManagerTest` (8) → **29/29 test PASS (0 failure)** | **Pass** (unit test JVM) |
| 6 | **Tương thích EVENT_SCHEMA 2.0.0 & exporter SEM-24** | Mã reason `DUPLICATE_SIGNAL` khớp regex `^[A-Z][A-Z0-9_]{0,63}$` và không làm lỗi validator SEM-24 | Đã kiểm tra [`export_logs.py`](../../../experiments/scripts/export_logs.py) và bổ sung delta vào [`docs/EVENT_SCHEMA.md`](../../EVENT_SCHEMA.md) | **Pass** |
| 7 | **Chạy Gradle AGP đầy đủ (`:app:testDebugUnitTest`, `:app:assembleDebug`)** | Build và chạy unit test qua Gradle Wrapper của Android | Máy kiểm không có Android SDK (`ANDROID_HOME` trống); cần chạy lại `./gradlew :app:testDebugUnitTest` trên máy có Android SDK | **Not run — blocker B2** |
| 8 | **Chạy thực nghiệm E05 (A/B/C) trên Emulator / Thiết bị thật** | Đo 3 kịch bản E05-A/B/C (3 lượt × 15 phút) với server và FCM/hook theo protocol | Thuộc giai đoạn chạy thực nghiệm thiết bị sau khi chốt candidate (SEM-37/SEM-42); hiện chưa có Firebase config thật (B1) và Android SDK/emulator trên máy kiểm (B2) | **Not run — blocker B1, B2** |

---

## 5. Blocker và Giới hạn bàn giao

- **B1 (kế thừa từ SEM-13 / SEM-33 / SEM-35):** Chưa có Firebase project, `google-services.json` và token thiết bị thật được xác nhận.
- **B2 (môi trường máy kiểm):** Thiếu Android SDK local để chạy Gradle task `:app:testDebugUnitTest` và emulator API 37. Tuy nhiên toàn bộ mã nguồn Kotlin của package `fcm` và 29 unit test đã được biên dịch bằng `kotlinc 2.1.20` (target JVM 17) và chạy JUnit 4 pass 100%.
- **Lưu ý chuyển giao cho E05 / Core:**
  - Kịch bản E05-C trên thiết bị yêu cầu barrier/hook có nhãn `INJECTED` để giữ worker đang chạy giữa lúc phát tín hiệu `V+2`; phần kiểm chứng race thật ở tầng DB transaction thuộc [SEM-39](../SEM-39/CORE_CASES.md) và ca đo E05.
  - Bảng `timeline_events` (`TimelineEventEntity`) của Room hiện chưa có cột lưu `signal_id` riêng (chỉ có `requestId`, `workId`, `messageId`). Nếu khi xuất log E05 cần trường `signal_ids` trực tiếp từ Room thay vì đối chiếu qua `message_id`/server log, chủ sở hữu sync core/exporter cần bổ sung cột hoặc bước join tương ứng.

---

## 6. Đầu ra mở khóa cho các Task tiếp theo

1. **[SEM-36](../../../tasks/backlog/SEM-36.md) (Trung — Tích hợp ba mode và pilot hybrid):** Nhận adapter push đã có chống trùng `DUPLICATE_SIGNAL` và bảo toàn tín hiệu mới khi kết hợp với PERIODIC/MANUAL.
2. **[SEM-37](../../../tasks/backlog/SEM-37.md) (Trung — Chốt bản ứng viên và manifest phục vụ tập chính):** Nhận diff messaging và [`PUSH_INPUT_CASES.md`](PUSH_INPUT_CASES.md) để đóng gói APK ứng viên cho đợt đo chính.
3. **[SEM-47](../../../tasks/backlog/SEM-47.md) (Trang — Viết phần silent push và lời dẫn demo 4 phút):** Sử dụng chính sách xử lý duplicate/stale hint/new-during-sync và ma trận [`PUSH_INPUT_CASES.md`](PUSH_INPUT_CASES.md) để giải thích cơ chế hợp nhất tín hiệu và tính đúng đắn dữ liệu.

Trạng thái đề xuất: **Review** (kèm `Not run` cho Gradle AGP full build và E05 thiết bị do B1, B2; không tự chuyển Done từ kế hoạch).
