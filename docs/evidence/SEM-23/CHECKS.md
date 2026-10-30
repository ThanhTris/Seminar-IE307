# SEM-23 — Kiểm tra và bàn giao

## Nhận dạng lần kiểm

- **Thời điểm:** 31/10/2026 03:32 UTC+7.
- **Commit nền:** `ff8f11148d5d2cfe0f2602bb6b58db00ca194f64` (`main`, sau khi merge SEM-14).
- **Commit artifact Android/UI:** `f07478b5b03f34e8d246f3aee323cb75eefd1821` — `feat(android): scaffold bulletin and timeline UI`.
- **Nhánh:** `codex/SEM-23-android-scaffold`.
- **Owner:** Trí (`ThanhTris`).
- **Môi trường:** Windows 11; Android Studio JBR `25.0.3`; Android SDK `C:\Users\ADMIN\AppData\Local\Android\Sdk`; API 37.0 / extension 22; Build Tools `36.0.0`; ADB `37.0.1-15733141`.
- **Gradle:** Wrapper `9.6.0`, distribution SHA-256 `bbaeb2fef8710818cf0e261201dab964c572f92b942812df0c3620d62a529a01`. Lần chạy wrapper thành công đã xác minh checksum distribution.
- **Không thay đổi môi trường toàn máy:** `JAVA_HOME` cấp user hiện vẫn trỏ tới `D:\Download\jdk-17.0.12` không tồn tại và Android SDK tools chưa ở `PATH`. Lệnh dùng JBR/SDK path trực tiếp qua `JAVA_HOME`, `ANDROID_HOME`, `ANDROID_SDK_ROOT` ở tiến trình PowerShell; `JAVA_TOOL_OPTIONS=-XX:ActiveProcessorCount=4`, `--max-workers=4`, `--no-daemon` giới hạn worker của lần build này. `sdkmanager` chưa cài, nhưng không cần tải thêm package cho scaffold này.

## Lệnh và kết quả

Các lệnh Gradle chạy từ `android/`:

```powershell
.\gradlew.bat :app:assembleDebug :app:testDebugUnitTest :app:lintDebug :app:connectedDebugAndroidTest --max-workers=4 --no-daemon
.\gradlew.bat --version
.\gradlew.bat buildEnvironment --no-daemon --max-workers=4
```

| Kiểm tra | Expected | Actual | Trạng thái |
|---|---|---|---|
| JBR và Gradle | JBR 25.0.3, Wrapper 9.6.0 khởi chạy được | `java -version`: 25.0.3; `gradlew --version`: Gradle 9.6.0, JVM 25.0.3 | Pass |
| Kotlin Gradle Plugin | Dùng Kotlin 2.4.10 theo SEM-11 | `buildEnvironment` xác nhận `org.jetbrains.kotlin:kotlin-gradle-plugin:2.4.10`; dependency 2.2.10 đi kèm AGP được nâng lên 2.4.10 | Pass |
| SDK / Build Tools / ADB | API 37, Build Tools 36 và ADB hoạt động | Platform `android-37.0` API 37.0 extension 22; Build Tools 36.0.0; ADB 37.0.1-15733141 | Pass |
| `:app:assembleDebug` | Tạo APK debug với package/version/SDK đã khóa | Thành công; `com.thanhtris.seminarie307`, versionCode 1, versionName 0.1.0, min 24, target/compile 37; SHA-256 `C934DD0BBC0866480C5EEE1F351244808CEEA1A7CFEB7AC5107EDC84799AB588` | Pass |
| `:app:testDebugUnitTest` | Filter run chính xác, không phân biệt hoa/thường sai; thứ tự mới nhất trước | 2 tests, 0 failures | Pass |
| `:app:lintDebug` | Không có lỗi lint chặn build | Lint thành công. Còn 3 cảnh báo gợi ý nâng Gradle lên 9.8.2, AGP lên 9.5.0 và Compose Compiler lên 2.4.21; giữ các bản SEM-11 đã khóa, không tự nâng baseline | Pass (cảnh báo thông tin) |
| `:app:connectedDebugAndroidTest` | UI chạy trên AVD API 37, trạng thái rỗng/manual/filter/recreation/theme đều đúng | `Medium_Phone_API_37.0`, 4 tests, 0 failures: trạng thái rỗng; gateway giả nhận đúng context và accepted không báo applied; filter/restore không đổi active run; dark theme/font 1.6 vẫn cuộn được | Pass |
| Chạy app rỗng | Không tự enqueue/GET; manual khóa khi chưa có core/run | Cài và mở app trên AVD; UI hiển thị `—`, `Chưa cấu hình`, `Chưa đồng bộ`, nội dung rỗng và nút manual bị khóa. Binding khởi chạy là `EmptyBulletinUiGateway` | Pass (scaffold) |
| Snapshot Room / HTTP / worker | Dữ liệu thật được đọc từ core khi có bàn giao | Chưa có SEM-25/26; UI adapter thật chưa được nối | Not run — SEM-25/26, phần manual end-to-end ở SEM-28 |
| Periodic / FCM / server / mạng | Trigger và API thật được xác nhận | Ngoài ranh giới SEM-23; không gửi FCM và không gọi server | Not run — SEM-26/27/30/32 |
| Thiết bị OPPO / đo pin / run thực nghiệm | Hồ sơ thiết bị và benchmark thực tế | Không dùng thiết bị vật lý hoặc chạy thử nghiệm; SEM-12 sở hữu hồ sơ thiết bị | Not run — SEM-12 và các task thực nghiệm |
| Secret/cấu hình local | Không có khóa, service account, `google-services.json`, `local.properties` hoặc keystore trong commit | Quét file/dấu hiệu token không có kết quả; các cấu hình cá nhân bị Git bỏ qua | Pass |

Lint còn cảnh báo mới-version vì SEM-23 phải dùng baseline từ [SEM-11](../../environment/ANDROID_BUILD.md). Tương thích của API 37 / AGP 9.4 / Gradle 9.6 được đối chiếu [release notes AGP 9.4](https://developer.android.com/build/releases/agp-9-4-0-release-notes). Built-in Kotlin và việc không áp plugin `org.jetbrains.kotlin.android` theo [hướng dẫn Android](https://developer.android.com/build/migrate-to-built-in-kotlin); Compose test dùng API hiện hành theo [Compose testing](https://developer.android.com/develop/ui/compose/testing).

## Đối chiếu acceptance SEM-23

| Yêu cầu | Bằng chứng |
|---|---|
| Hai tab Bản tin/Timeline, empty state và trạng thái chung | `BulletinScreenTest.emptyScaffoldShowsBothTabsAndKeepsManualDisabled`; mở `MainActivity` thực tế trên AVD cũng cho UI rỗng |
| Mở màn hình không enqueue hoặc tự fetch | Activity chỉ collect state từ `BulletinUiGateway`; `EmptyBulletinUiGateway` phát state rỗng, không có client HTTP hoặc lệnh enqueue khi mở |
| Manual dùng active `run_id`/mode, filter không tác động run | `manualUsesActiveRunContextAndAcceptedMessageDoesNotClaimApplied` và `runFilterRestoresAfterRecreationAndDoesNotChangeManualRun` |
| Accepted tách biệt với applied | Test gateway giả trả Accepted; thông báo là “Đã xếp lịch; chưa xác nhận đã đồng bộ.” và cache vẫn giữ version 41 |
| Fixture không xuất hiện khi app chạy | Preview fixture nằm trong `src/debug`; Activity mặc định nối `EmptyBulletinUiGateway` |
| Theme, chữ lớn, cuộn | `darkThemeAndLargeFontKeepSnapshotScrollable`; `SeminarTheme` theo system theme |
| Build/test có thể lặp lại | [Hướng dẫn mở project/build](../../setup/ANDROID.md); Gradle Wrapper checksum ghi ở trên |

## Bàn giao và giới hạn

- **SEM-25:** thay `EmptyBulletinUiGateway` qua [AppContainer](../../../android/app/src/main/java/com/thanhtris/seminarie307/config/AppContainer.kt); ánh xạ cache/Room và timeline sang `BulletinUiState`, triển khai `enqueueManual(ManualSyncContext)` qua core. Ý nghĩa source/mode/run tham chiếu [SEM-14 shared sync](../../mechanisms/SHARED_SYNC.md).
- **SEM-28:** nối manual đầu-cuối với API đã được SEM-25/26 bàn giao; xác nhận server/event thực. Test ở SEM-23 chỉ dùng gateway giả.
- **SEM-26/27/30/32:** lần lượt hoàn thiện contract/server/periodic/FCM; version catalog đã khai báo thư viện nhưng chưa áp plugin hay khởi tạo Firebase.
- **SEM-23 không triển khai:** Room, sync engine, HTTP, lịch periodic, FCM, đổi mode, credentials hoặc ký release.
- Artifact bàn giao tại commit `f07478b5b03f34e8d246f3aee323cb75eefd1821`; APK debug là build cục bộ, không commit APK.

## Tài liệu liên quan

- [Yêu cầu SEM-23](../../../tasks/backlog/SEM-23.md)
- [Hướng dẫn Android](../../setup/ANDROID.md)
- [Baseline Android SEM-11](../../environment/ANDROID_BUILD.md)
- [Hợp đồng sync SEM-14](../../mechanisms/SHARED_SYNC.md)
