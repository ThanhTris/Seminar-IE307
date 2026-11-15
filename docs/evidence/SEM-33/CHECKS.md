# SEM-33 — CHECKS Token refresh và bàn giao PUSH.md

## 1. Nhận dạng lần kiểm

- **Người thực hiện:** Trang (`rosy179`).
- **Nhiệm vụ:** [SEM-33](../../../tasks/backlog/SEM-33.md) — Xử lý token refresh và bàn giao PUSH.md.
- **Ngày lập:** 09/11/2026 (UTC+7).
- **Base commit:** `54d48c2` (`origin/main`, đã gồm SEM-32 và SEM-35).
- **Nhánh làm việc:** `codex/SEM-33-token-lifecycle`.
- **Máy kiểm:** Windows, JDK 23 có sẵn nhưng `java` trên PATH là 1.8; **không có Android SDK** (`ANDROID_HOME` chưa đặt, không thấy `%LOCALAPPDATA%\Android\Sdk`), không có `adb`/`kotlinc`. Vì vậy không build Gradle, không chạy unit test Android và không chạy trên emulator/thiết bị.
- **Đầu ra bàn giao:**
  - `android/app/src/main/java/com/thanhtris/seminarie307/fcm/FcmTokenManager.kt` (mới)
  - `android/app/src/main/java/com/thanhtris/seminarie307/fcm/BulletinFirebaseMessagingService.kt` (`onNewToken`)
  - `android/app/src/main/java/com/thanhtris/seminarie307/SeminarApp.kt` (token khi khởi động)
  - `android/app/build.gradle.kts`, `android/build.gradle.kts` (Google Services có điều kiện)
  - `android/app/src/test/java/com/thanhtris/seminarie307/fcm/FcmTokenManagerTest.kt` (mới)
  - [`docs/PUSH.md`](../../PUSH.md), cập nhật [`docs/setup/ANDROID.md`](../../setup/ANDROID.md)

## 2. Đầu vào đã nhận

| Đầu vào | Đã dùng |
|---|---|
| [SEM-13](../SEM-13/CHECKS.md) — [SERVER_FIREBASE.md](../../environment/SERVER_FIREBASE.md) | Quy ước `google-services.json`, `FCM_TOKEN_FILE`, blocker B1 (chưa có project/credential/token xác nhận) |
| [SEM-32](../SEM-32/CHECKS.md) — callback + adapter | `onNewToken` và khóa `fcmToken` trong Room làm nền cho vòng đời token |
| [SEM-35](../SEM-35/CHECKS.md) — [FCM_SENDER.md](../../setup/FCM_SENDER.md) | Cách sender đọc token từ file, payload, TTL, event accepted/rejected/unknown |

## 3. Thay đổi so với SEM-32

- Gỡ log token thô: `SeminarApp.fetchAndLogFcmToken` (tag `FCM_TOKEN`) và `onNewToken` (`New FCM Token received: $token`) trước đây in token ra Logcat — vấn đề đã ghi ở [SEM-26 CHECKS](../SEM-26/CHECKS.md) và [DEVICES.md](../../environment/DEVICES.md). Nay chỉ log fingerprint 16 hex.
- `FcmTokenManager` kiểm hợp lệ (cùng quy tắc `prepareFirebase`: không rỗng, không khoảng trắng, ≤ 8192), lưu Room, theo dõi xoay vòng bằng fingerprint (`fcmTokenFingerprint`, `fcmTokenPreviousFingerprint`, `fcmTokenRefreshCount`, `fcmTokenUpdatedAtUtc`, `fcmTokenSource`, `fcmTokenStatus`).
- Thiếu cấu hình Firebase → `FIREBASE_NOT_CONFIGURED`, không crash, không token hardcode. Token fetch lỗi → `FETCH_FAILED` (chỉ mã, không exception message).
- Plugin Google Services chỉ áp dụng khi tồn tại `android/app/google-services.json` (file đã gitignore) nên clone không có credential vẫn build.
- Debug build ghi token vào `files/fcm/device-token.txt` (bộ nhớ riêng của app) để copy bằng `adb run-as` vào `FCM_TOKEN_FILE` mà không qua Logcat; release không ghi và xóa file còn sót.

## 4. Expected / actual

| STT | Yêu cầu | Expected | Actual / evidence | Kết quả |
|:---:|---|---|---|:---:|
| 1 | Đăng ký/cập nhật token, gồm `onNewToken` | `onNewToken` lưu token mới vào Room qua manager, ghi nhận đổi/không đổi | Code review: service gọi `FcmTokenManager.onTokenAvailable(token, ON_NEW_TOKEN)`; logic phân nhánh có trong `FcmTokenManagerTest` (token đầu, trùng, đổi, không hợp lệ) | **Not run** (chưa có Android SDK để biên dịch/chạy test) |
| 2 | Token thay đổi | Token cũ bị thay, đếm refresh, giữ fingerprint cũ | Thiết kế + test `changedTokenReplacesStoredTokenAndTracksRotation`; chưa chạy | **Not run** |
| 3 | Cấu hình thiếu | `FIREBASE_NOT_CONFIGURED`, không crash | `refreshFromFirebase` bắt `FirebaseApp` null → `onTokenUnavailable`; test `missingFirebaseConfigRecordsStatusWithoutToken` (mức manager) chưa chạy; chưa thử trên thiết bị không có `google-services.json` | **Not run** |
| 4 | Build không có `google-services.json` | Gradle không áp dụng plugin, build vẫn chạy | Điều kiện `file("google-services.json").exists()` trong `app/build.gradle.kts`; chưa chạy Gradle. Plugin `com.google.gms:google-services:4.5.0` tồn tại trên Google Maven (HTTP 200 cho `.pom`, kiểm 09/11/2026); chưa kiểm tương thích với AGP 9.4.1 | **Not run** |
| 5 | Không lộ token | Không log/export token thô | `git grep` xác nhận không còn `Log.*token` in giá trị token trong `android/`; chỉ `fingerprint` được log; test `fingerprintIsStableShortAndDoesNotContainToken` chưa chạy | **Pass** (review tĩnh); test **Not run** |
| 6 | Credential ngoài repo | `google-services.json`, token file, service-account bị gitignore | `.gitignore` đã có `google-services.json`, `*service-account*.json`, `.local/`; commit này không thêm file nhạy cảm | **Pass** |
| 7 | PUSH.md đủ để chạy sender | Có cấu hình, lấy token, lệnh gửi, payload/TTL, giới hạn | [PUSH.md](../../PUSH.md) §3–§9; lệnh `send-push` khớp `server/package.json` và [FCM_SENDER.md](../../setup/FCM_SENDER.md); liên kết tương đối đã kiểm tồn tại | **Pass** (tài liệu); quy trình **Not run** |
| 8 | Phân biệt accepted/received/applied | Bảng sự kiện và điều chưa được suy diễn | [PUSH.md §7](../../PUSH.md) đối chiếu [SILENT_PUSH.md §7](../../mechanisms/SILENT_PUSH.md) | **Pass** |
| 9 | Bằng chứng token refresh thật | Token thật lấy từ thiết bị, xoay vòng quan sát được | Chưa có Firebase project/credential/token xác nhận (blocker B1 của SEM-13/35); chưa có Android SDK/thiết bị trên máy kiểm | **Not run — blocker** |

## 5. Blocker còn lại

- **B1 (kế thừa SEM-13/SEM-35):** cần người quản lý xác nhận Firebase project, cấp `google-services.json` cho `com.thanhtris.seminarie307` và credential gửi FCM; chưa có thì không có token thật.
- **B2:** máy kiểm thiếu Android SDK và JDK 17+ trên PATH. Cần chạy `cd android && ./gradlew :app:testDebugUnitTest` trên máy có SDK để xác nhận biên dịch và 8 test `FcmTokenManagerTest`.
- **Quy trình thử xoay vòng cần chạy khi có B1/B2:** cài debug build → mở app → copy token bằng PUSH.md §4 → ghi fingerprint → `adb shell pm clear com.thanhtris.seminarie307` (hoặc gỡ/cài lại) → mở app → ghi fingerprint mới, `fcmTokenRefreshCount`; gửi push bằng token cũ phải ra `push_send_rejected` (nếu FCM từ chối) và token mới phải nhận `push_received`. Không ghi token vào evidence, chỉ ghi fingerprint.

## 6. Đầu ra đã bàn giao cho task sau

- [SEM-34](../../../tasks/backlog/SEM-34.md): [PUSH.md](../../PUSH.md) để chạy sender với thiết bị thật; cần B1 trước khi pilot.
- [SEM-37](../../../tasks/backlog/SEM-37.md), [SEM-38](../../../tasks/backlog/SEM-38.md): token status/fingerprint làm đầu vào xác định thiết bị còn nhận được push; SEM-38 xử lý duplicate/version hint trên adapter SEM-32.
- [SEM-47](../../../tasks/backlog/SEM-47.md): bảng accepted/received/applied và giới hạn nền ở [PUSH.md §7–§8](../../PUSH.md).

Trạng thái đề xuất: **Review với Not run/blocker B1, B2 ghi rõ**; không chuyển Done từ kế hoạch.
