# Mở và chạy ứng dụng Android

Project Android nằm trong thư mục `android/`. Mở thư mục này bằng Android Studio; Gradle project root là `android/`, còn `app/` là application module duy nhất.

## Baseline project

| Thành phần | Giá trị |
|---|---|
| `applicationId` / `namespace` | `com.thanhtris.seminarie307` |
| `compileSdk` / `targetSdk` / `minSdk` | 37 / 37 / 24 |
| Build Tools | 36.0.0 |
| Android Gradle Plugin / Gradle Wrapper | 9.4.1 / 9.6.0 |
| Kotlin built-in runtime / Compose Compiler plugin | 2.4.10 / 2.4.10 |
| Compose BOM | 2026.09.00 |
| Activity Compose / Lifecycle Compose | 1.13.0 / 2.11.0 |
| Room / KSP / WorkManager | 2.8.5 / 2.3.12 / 2.12.0 (catalog only) |
| Firebase Android BOM / Google Services plugin | 35.1.0 / 4.5.0 (catalog only) |

## JDK và Android SDK

SEM-11 đã kiểm tra Android Studio JBR `25.0.3`, Android SDK tại `C:\Users\ADMIN\AppData\Local\Android\Sdk`, API 37 và Build Tools `36.0.0`. Trong Android Studio, chọn JDK đó làm **Gradle JDK**:

`C:\Program Files\Android\Android Studio\jbr`

Nếu `JAVA_HOME` toàn máy trỏ sai hoặc Android tools chưa ở `PATH`, không cần sửa cấu hình Windows. Có thể chạy wrapper trong PowerShell với biến chỉ tồn tại trong tiến trình hiện tại:

```powershell
$env:JAVA_HOME = 'C:\Program Files\Android\Android Studio\jbr'
$env:ANDROID_HOME = 'C:\Users\ADMIN\AppData\Local\Android\Sdk'
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
```

Android Studio có thể tạo `android/local.properties` trỏ đến SDK cục bộ. File này bị Git bỏ qua; không commit đường dẫn máy cá nhân.

## Build và kiểm tra

Chạy lệnh từ thư mục `android/`:

```powershell
.\gradlew.bat :app:assembleDebug
.\gradlew.bat :app:testDebugUnitTest
.\gradlew.bat :app:lintDebug
.\gradlew.bat :app:connectedDebugAndroidTest
```

APK debug ở `android/app/build/outputs/apk/debug/app-debug.apk`. Lệnh connected test cần một emulator/device đang sẵn sàng; emulator API 37 có tên `Medium_Phone_API_37.0` trên máy đã kiểm tra.

## UI và adapter sync

Khi mới cài, app hiển thị trạng thái rỗng. `AppContainer.bulletinUiGateway` hiện được nối với `EmptyBulletinUiGateway`: UI chỉ collect `Flow` trạng thái, không tự enqueue hay gọi GET khi mở màn hình. Nút manual bị khóa cho tới khi gateway phát mode, `activeRunId` và quyền enqueue hợp lệ.

SEM-25/28 thay binding trong `app/src/main/java/com/thanhtris/seminarie307/config/AppContainer.kt` bằng adapter đọc cache/timeline và enqueue qua sync core. Adapter cung cấp `BulletinUiState` cùng `ManualSyncContext`; context manual luôn lấy từ run/mode đang hoạt động, không lấy từ bộ lọc timeline. `Accepted` chỉ có nghĩa request đã được xếp lịch; trạng thái applied phải đến từ state quan sát được.

Compose Preview fixture nằm trong `app/src/debug/` và các test fixture trong source set test. App khởi chạy không dùng dữ liệu mẫu. Model UI là presentation model, chưa định nghĩa JSON hoặc schema server của SEM-26.

Firebase, Room, WorkManager và KSP đã được pin trong version catalog để bàn giao tiếp theo; scaffold chưa áp dụng plugin Google Services, chưa khởi tạo Firebase và không cần `google-services.json`.
