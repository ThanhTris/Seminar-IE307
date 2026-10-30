# Baseline môi trường build Android

Cập nhật 30/10/2026 cho SEM-11. Phiên bản trong bảng là baseline được chọn để SEM-23 tạo scaffold; trạng thái cài đặt bên dưới phản ánh máy Windows hiện tại. Việc chọn phiên bản không có nghĩa toàn bộ dependency đã được resolve qua một project Android.

## Cấu hình build được chốt

| Thành phần | Phiên bản/cấu hình | Ghi chú |
|---|---|---|
| Application ID / namespace | `com.thanhtris.seminarie307` | Dùng cùng giá trị cho app đầu tiên; Firebase registration thuộc SEM-13. |
| `compileSdk` / `targetSdk` | `37` / `37` | SDK Platform 37.0 đã có trên máy build. |
| `minSdk` | `24` | Phù hợp baseline AndroidX/WorkManager đã chọn. |
| Android Gradle Plugin | `9.4.1` | Stable; API 37 được hỗ trợ bởi AGP 9.4. |
| Gradle Wrapper | `9.6.0` | Sẽ được tạo cùng scaffold tại SEM-23; distribution local đã kiểm checksum. |
| Android Build Tools | `36.0.0` | Có sẵn trong SDK cục bộ. |
| JDK chạy Gradle | Android Studio JBR `25.0.3` | Gradle 9.6 chạy thành công. Dùng đường dẫn JBR rõ ràng/project-local; user-level `JAVA_HOME` hiện trỏ sai. |
| Java/Kotlin bytecode target | `17` | Runtime build JDK và target bytecode là hai cấu hình riêng. |
| Kotlin / Compose Compiler plugin | `2.4.10` | Compose Compiler plugin cùng phiên bản Kotlin. |
| Compose BOM | `2026.09.00` | Stable BOM; Compose libraries lấy phiên bản qua BOM. |
| Activity Compose | `1.13.0` | Tích hợp Activity với Compose. |
| Lifecycle ViewModel Compose | `2.11.0` | Tích hợp ViewModel với Compose. |
| Room | `2.8.5` | Persistence cho cache cục bộ. |
| KSP | `2.3.12` | Annotation processing của Room; không dùng KAPT. |
| WorkManager | `2.12.0` | Periodic và one-time work dùng cùng sync core. |
| Firebase Android BoM | `35.1.0` | Version catalog cho Firebase Messaging; không thêm Firebase config thật tại SEM-11. |
| Google Services Gradle plugin | `4.5.0` | Để SEM-23/13 tích hợp khi có Firebase app registration và file local. |

Version matrix dựa trên tài liệu phát hành chính thức: [AGP 9.4/API 37](https://developer.android.com/build/releases/agp-9-4-0-release-notes), [Compose BOM và compiler](https://developer.android.com/develop/ui/compose/setup-compose-dependencies-and-compiler), [WorkManager](https://developer.android.com/jetpack/androidx/releases/work), [AndroidX/Room](https://developer.android.com/jetpack/androidx/versions) và [Firebase Android SDK releases](https://firebase.google.com/support/release-notes/android). JBR 25.0.3 được kiểm tra thực tế cùng Gradle 9.6.0; ma trận Java/Gradle chính thức cho biết Java 25 được hỗ trợ từ Gradle 9.1.0 trở lên ([Gradle compatibility](https://docs.gradle.org/current/userguide/compatibility.html)).

## Máy build được kiểm tra

| Hạng mục | Kết quả thực tế | Trạng thái |
|---|---|---|
| Hệ điều hành | Windows 11, build `10.0.26300`, x64 | Pass |
| Android Studio | `AI-262.9437.185.2621.16467767` | Pass |
| JBR đi kèm Android Studio | OpenJDK/Javac `25.0.3`; `C:\Program Files\Android\Android Studio\jbr` | Pass |
| `JAVA_HOME` user environment | `D:\Download\jdk-17.0.12`, đường dẫn không tồn tại; Machine-level `JAVA_HOME` chưa đặt | Fail (user setting sai) |
| Android SDK | `C:\Users\ADMIN\AppData\Local\Android\Sdk` | Pass |
| SDK Platforms | `android-36`, `android-37.0` | Pass |
| SDK Build Tools | `35.0.0`, `36.0.0` | Pass |
| ADB | `1.0.41`, platform-tools `37.0.1-15733141` | Pass |
| ADB trên `PATH` | Không tìm thấy; gọi bằng đường dẫn SDK trực tiếp hoạt động | Ghi chú cấu hình |
| Android Emulator | `37.2.12.0` | Pass |
| AVD inventory | `Medium_Phone_API_37.0`, Google Play image, `PlayStore.enabled=true` theo config tĩnh | Pass (chưa boot; SEM-12 xác nhận thiết bị) |
| Thiết bị ADB đang ở trạng thái `device` | `0`; serial không được ghi | Not available (không phải tiêu chí build SEM-11) |
| Android SDK Command-line Tools / `sdkmanager` | Chưa cài | Not installed; không chặn build hiện tại vì SDK Platform và Build Tools cần dùng đã có |
| Gradle global | Không cài trên `PATH` | Dùng Gradle 9.6.0 trong `.local/tools/` để kiểm tra; project wrapper tạo tại SEM-23 |
| Android project / `gradlew.bat` | Chưa có trong repo | Not run; tạo ở SEM-23 |

## Cách chạy build sau khi SEM-23 tạo scaffold

Các đường dẫn dưới đây dành cho PowerShell trên máy đã kiểm tra. Dùng project wrapper; không phụ thuộc PATH toàn hệ thống.

```powershell
$env:JAVA_HOME = 'C:\Program Files\Android\Android Studio\jbr'
$env:ANDROID_HOME = 'C:\Users\ADMIN\AppData\Local\Android\Sdk'
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
$env:PATH = "$env:JAVA_HOME\bin;$env:ANDROID_HOME\platform-tools;$env:PATH"
.\gradlew.bat --version
.\gradlew.bat :app:assembleDebug
```

Wrapper nên trỏ tới Gradle `9.6.0`; target bytecode app đặt Java/Kotlin 17. Dùng API Platform 37 và Build Tools 36.0.0 đã kiểm tra. SEM-23 xác nhận build debug thật trước khi giao M1.

## Cấu hình Firebase và thiết bị

- SEM-11 chỉ khóa package ID và các phiên bản build Android. Firebase project, quyền gửi test, Google Services app registration và cấp cấu hình local thuộc SEM-13.
- Không commit `google-services.json`, `.env`, service-account JSON, token, `local.properties` hoặc keystore. `.gitignore` hiện đã loại các file/đường dẫn nhạy cảm liên quan.
- Chi tiết Android/API/ColorOS, emulator boot, kết nối OPPO, mạng tới server và Internet/FCM thuộc SEM-12/SEM-13; các nội dung đó không được suy ra từ inventory của máy này.
