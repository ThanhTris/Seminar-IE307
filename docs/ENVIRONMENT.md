# Chỉ mục Môi trường Toàn bộ Dự án — SEM-28 / M1

Tài liệu này là chỉ mục tổng hợp toàn diện cấu hình môi trường từ **ba hồ sơ môi trường cơ sở** và **hai tài liệu hướng dẫn thành phần**, phục vụ kiểm thử và nghiệm thu cột mốc **M1** (Đồng bộ thủ công đầu cuối) cùng các cơ chế đồng bộ tiếp theo (Periodic, Push, Hybrid).

---

## 1. Danh mục Hồ sơ Môi trường và Setup Cơ sở

Hệ thống được đối chiếu và xây dựng dựa trên 5 tài liệu độc lập đã được nghiệm thu:

1. **Hồ sơ Môi trường Build Android (SEM-11):** [`docs/environment/ANDROID_BUILD.md`](environment/ANDROID_BUILD.md)  
   *Môi trường build chuẩn trên Windows 11, khóa phiên bản Android SDK 37, JBR 25.0.3, Gradle Wrapper 9.6.0, AGP 9.4.1 và Kotlin 2.4.10.*
2. **Hồ sơ Môi trường Server & Firebase (SEM-13):** [`docs/environment/SERVER_FIREBASE.md`](environment/SERVER_FIREBASE.md)  
   *Môi trường Node.js v24/v26, kiểm tra kết nối REST port 3000, xác thực Firebase service account và SDK.*
3. **Hồ sơ Môi trường Thiết bị & Emulator (SEM-12):** [`docs/environment/DEVICES.md`](environment/DEVICES.md)  
   *Cấu hình máy ảo Android Emulator AVD API 37 (`Pixel_7a` / `Medium_Phone_API_37.0`), Google Play Services 26.33.32, và ghi nhận blocker máy thật OPPO (ColorOS USB authorization blocker).*
4. **Hướng dẫn Thiết lập Client Android (SEM-23):** [`docs/setup/ANDROID.md`](setup/ANDROID.md)  
   *Quy trình build APK debug, cài đặt qua ADB, kiểm tra logcat và cấp quyền ứng dụng.*
5. **Hướng dẫn Thiết lập Snapshot Server v2 (SEM-27):** [`docs/setup/SERVER.md`](setup/SERVER.md)  
   *Cấu hình runtime TypeScript/Node, lockfile, cơ chế khóa tệp `state.json.lock`, khôi phục outbox và xử lý Windows fsync.*

---

## 2. Bảng Đối chiếu Môi trường Toàn diện

| Thành phần | Cấu hình đã khóa / Khuyến nghị | Ghi chú & Liên kết |
|---|---|---|
| **Hệ điều hành Host** | Windows 11 x64 (Build chính) / macOS ARM64 | Hỗ trợ phát triển và chạy server đa nền tảng |
| **Android SDK Platform** | API 37 (`android-37.0`), build-tools `36.0.0` | [`ANDROID_BUILD.md`](environment/ANDROID_BUILD.md) |
| **Min SDK / Target SDK** | `minSdk = 24`, `targetSdk = 37` | Hỗ trợ Android 7.0 đến Android 15 |
| **Java / Gradle JDK** | Android Studio JBR `25.0.3` (Java 17 target) | Bytecode `JVM_17`, Desugaring Java 8+ bật |
| **Gradle / AGP** | Gradle `9.6.0` / AGP `9.4.1` | Khóa checksum trong `gradle-wrapper.properties` |
| **Node.js Runtime** | Node `v24.15.0` (Win) / `v26.0.0` (macOS) | [`SERVER_FIREBASE.md`](environment/SERVER_FIREBASE.md) |
| **TypeScript / Cú pháp** | TypeScript `5.9.3` | Biên dịch sang CommonJS (`npm run build`) |
| **Android Emulator** | `Pixel_7a` hoặc `Medium_Phone_API_37.0` (API 37) | [`DEVICES.md`](environment/DEVICES.md), Play Store image, 4096MB RAM |
| **Thiết bị thật (OPPO)** | OPPO Find X9 / ColorOS | **Blocker / Not run** (SEM-12: Rào cản bảo mật ColorOS) |
| **Lưu trữ CSDL Client** | SQLite Room `2.8.5` (`seminar_bulletin.db`) | KSP `2.3.12`, persistence ngoại tuyến |
| **Lưu trữ Server** | `server/data/snapshot.json` | JSON bền vững nguyên tử kèm tệp khóa lockfile |

---

## 3. Bản đồ Mạng và Định tuyến Cổng (Network Topology)

Hệ thống giao tiếp thông qua giao thức HTTP REST API tại cổng `3000`:

```
┌────────────────────────────────────────────────────────┐
│                      MÁY HOST                          │
│                                                        │
│  [Node.js Snapshot Server v2] (Cổng 3000)              │
│       ▲                           ▲                    │
│       │ (GET/ETag)                │ (CLI Update)       │
│       │                           │                    │
│       │              [update-cli.js / npm run update]  │
└───────┼───────────────────────────┼────────────────────┘
        │                           │
        │ Loopback 10.0.2.2:3000    │ adb reverse tcp:3000 tcp:3000
        ▼                           ▼
┌──────────────────┐        ┌──────────────────┐
│ ANDROID EMULATOR │        │ THIẾT BỊ VẬT LÝ  │
│ (AVD API 37)     │        │ (Qua cáp USB)    │
│                  │        │                  │
│ App Seminar      │        │ App Seminar      │
└──────────────────┘        └──────────────────┘
```

- **Loopback Emulator:** Địa chỉ `http://10.0.2.2:3000` được định tuyến tự động bởi QEMU tới `localhost:3000` trên máy host.
- **Thiết bị thật qua USB:** Yêu cầu chạy `adb reverse tcp:3000 tcp:3000` để chuyển tiếp cổng từ thiết bị về máy host.

---

## 4. Ranh giới Tài nguyên và Giới hạn Kỹ thuật

1. **Bộ nhớ Emulator:** Khởi chạy máy ảo API 37 khuyến nghị tối thiểu 4GB RAM guest và tăng dung lượng đĩa ảo lên tối thiểu 8GB để tránh tình trạng out-of-memory trong quá trình chạy background task WorkManager.
2. **Khóa Lockfile Server:** Quá trình ghi snapshot được bảo vệ bằng tệp `state.json.lock`. Khi tắt server đột ngột bằng lệnh `SIGKILL`, cần gỡ lock thủ công trước khi khởi động lại.
3. **Độ bền mất điện trên Windows:** File tạm được bảo đảm ghi đĩa bằng `fsync` trước khi atomic rename. Lệnh `fsync` trên thư mục cha bị bỏ qua trên Windows để tránh lỗi EPERM đặc thù.
4. **Trạng thái máy thật OPPO:** Thiết bị thật chưa sẵn sàng; toàn bộ các bước kiểm thử tự động và thủ công của Cột mốc M1 được thực hiện trên Android Emulator tiêu chuẩn API 37.

---

## 5. Revision Tích hợp Cột mốc M1

- **Base Revision:** `33e3bf7` (nhánh `main`).
- **Thành phần tích hợp:** `RealBulletinUiGateway.kt` kết nối trực tiếp `SyncWorkEnqueuer.kt` (SEM-25) và gọi Server v2 (SEM-27).
