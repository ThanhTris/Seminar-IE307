# SEM-11 — CHECKS và bàn giao

- Thực hiện: Trí (`ThanhTris`).
- Ngày kiểm tra: 30/10/2026 (UTC+7).
- Repo baseline: `63a3ab0804ca18e96d1180a449fa2ed64465f221` (`main`).
- Nhánh thực hiện: `codex/SEM-11-android-build`.
- Bàn giao: xem commit của nhánh này chứa ba artifact SEM-11; chưa ghi commit hash ở đây để tránh giá trị tự tham chiếu trước khi commit được tạo.

## Kiểm tra và kết quả

| Check | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| Android Studio/JBR | IDE và JDK thực tế có thể được xác định | Android Studio `AI-262.9437.185.2621.16467767`; JBR Java/Javac `25.0.3` tại `C:\Program Files\Android\Android Studio\jbr` | Pass |
| `JAVA_HOME` mặc định | Trỏ tới JDK khả dụng | User-level setting là `D:\Download\jdk-17.0.12`; thư mục không tồn tại và `java`/`javac` không resolve qua PATH. Machine-level `JAVA_HOME` chưa đặt; Gradle đã chạy bằng JBR trực tiếp | Pass (có cảnh báo cấu hình user) |
| Gradle/JDK tương thích | Chạy Gradle 9.6.0 và nhận diện Java 25 | Tải distribution vào `.local/tools/`; SHA-256 từ endpoint `.sha256` khớp `bbaeb2fef8710818cf0e261201dab964c572f92b942812df0c3620d62a529a01`. Với `$env:JAVA_HOME='C:\Program Files\Android\Android Studio\jbr'`, `gradle --version` báo Gradle `9.6.0`, Launcher/Daemon JVM `25.0.3` | Pass |
| Android SDK inventory | API 37 và Build Tools 36.0.0 có sẵn | SDK `C:\Users\ADMIN\AppData\Local\Android\Sdk`; platforms `android-36`, `android-37.0`; Build Tools `35.0.0`, `36.0.0` | Pass |
| ADB | Có thể gọi và xác nhận thiết bị hiện diện mà không lưu serial | ADB `1.0.41`, platform-tools `37.0.1-15733141`; `adb devices` cho 0 thiết bị ở trạng thái `device`, serial không lưu vào tài liệu | Pass (công cụ); thiết bị vật lý chưa xác nhận ở SEM-12 |
| Android SDK CLI | Có sdkmanager nếu cần cài package mới | `cmdline-tools`/`sdkmanager` chưa cài. Các platform/build tools cần cho baseline đang hiện diện | Not installed (không chặn baseline hiện tại) |
| Emulator | Inventory khả dụng; không cần boot cho SEM-11 | Emulator `37.2.12.0`; AVD `Medium_Phone_API_37.0`. Đọc config tĩnh xác nhận system image Google Play API 37.0 và `PlayStore.enabled=true`; không boot emulator | Pass (inventory); run thực tế thuộc SEM-12 |
| Android project/build | Có thể chạy `assembleDebug` | Repo chưa có Android project hoặc Gradle Wrapper; `assembleDebug` chưa chạy và được bàn giao cho SEM-23 | Not run |
| Package ID / namespace | Một giá trị ổn định để SEM-23 scaffold | Chốt `com.thanhtris.seminarie307`; được ghi trong `docs/SCOPE.md` và `docs/environment/ANDROID_BUILD.md` | Pass (quyết định cấu hình) |
| Firebase cấu hình thật | Project/quyền/app registration xác định được | Không kiểm trong SEM-11; Firebase project và credential do SEM-13 | Not run (SEM-13) |
| OPPO/ColorOS và mạng | Có thông tin thiết bị/kết nối thực | Không kiểm trong SEM-11; Vinh/Tâm bàn giao qua SEM-12/13 | Not run (SEM-12/13) |

## Lệnh kiểm tra đã dùng

Các lệnh sau rút gọn từ PowerShell. Serial thiết bị không được lưu; emulator không được khởi động.

```powershell
$studio = 'C:\Program Files\Android\Android Studio'
$sdk = 'C:\Users\ADMIN\AppData\Local\Android\Sdk'
$jbr = Join-Path $studio 'jbr'
$env:JAVA_HOME = $jbr
$env:ANDROID_HOME = $sdk
$env:ANDROID_SDK_ROOT = $sdk
& "$jbr\bin\java.exe" -version
& "$jbr\bin\javac.exe" -version
& "$sdk\platform-tools\adb.exe" version
& "$sdk\platform-tools\adb.exe" devices
& "$sdk\emulator\emulator.exe" -version
& "$sdk\emulator\emulator.exe" -list-avds
& '.local\tools\gradle-9.6.0\bin\gradle.bat' --version
```

Gradle 9.6.0 zip được tải từ `services.gradle.org/distributions/gradle-9.6.0-bin.zip`; checksum SHA-256 đối chiếu endpoint cùng tên `.sha256`. Distribution và cache nằm dưới `.local/`, được ignore bởi Git.

## Blocker và cách xử lý

- `JAVA_HOME` user-level trỏ tới đường dẫn JDK không tồn tại. Build của SEM-23 dùng `C:\Program Files\Android\Android Studio\jbr` qua cấu hình project/session; không cần thay biến môi trường toàn máy.
- Android SDK tools chưa ở `PATH`. SEM-23 dùng `ANDROID_HOME`/`ANDROID_SDK_ROOT` theo project/session hoặc gọi tool qua đường dẫn SDK; không cần cài lại SDK đã có.
- `sdkmanager` chưa cài. Chưa chặn baseline vì API 37 và Build Tools 36.0.0 đã có; nếu SEM-23 cần thêm package thì cài Command-line Tools trong SDK manager và ghi lại phiên bản.
- Chưa có `gradlew.bat` hoặc Android project nên build APK chưa thể chạy trong SEM-11. SEM-23 sở hữu scaffold và xác nhận `:app:assembleDebug`.

## Bàn giao

- [SEM-14](../../../tasks/backlog/SEM-14.md): package ID, API/target/min SDK và baseline Android để vẽ luồng sync.
- [SEM-19](../../../tasks/backlog/SEM-19.md), [SEM-20](../../../tasks/backlog/SEM-20.md), [SEM-21](../../../tasks/backlog/SEM-21.md): scope, baseline Android và giới hạn FCM để hoàn tất tổng hợp/nghiên cứu.
- [SEM-23](../../../tasks/backlog/SEM-23.md): application ID/namespace, version matrix, JBR/SDK paths và lệnh wrapper để tạo scaffold và chạy debug build.
- [SEM-26](../../../tasks/backlog/SEM-26.md): package ID đã khóa để Tâm chốt API/event contract; Firebase registration và server config chờ SEM-13.

## Bảo mật và kiểm tra tài liệu

- Không ghi token, service-account key, Google Services JSON, local properties, keystore hoặc serial thiết bị.
- `.gitignore` hiện bỏ qua `.env*`, `google-services.json`, `local.properties`, service-account JSON và keystore.
- `git diff --cached --check`: Pass sau khi thêm ba artifact.
- Kiểm tra liên kết tương đối trong cả ba file: Pass; mọi đích nội bộ đều tồn tại.
- Quét mẫu credential-shaped (API key, access token, private key): Pass; không thấy giá trị bí mật.
