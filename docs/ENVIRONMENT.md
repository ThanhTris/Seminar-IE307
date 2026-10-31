# Chỉ mục Môi trường Toàn bộ Dự án — SEM-28

Tài liệu này tổng hợp cấu hình môi trường từ các hồ sơ độc lập của Android ([`ANDROID_BUILD.md`](environment/ANDROID_BUILD.md)) và Server ([`SERVER_FIREBASE.md`](environment/SERVER_FIREBASE.md)) để phục vụ kiểm thử và vận hành các cơ chế đồng bộ.

---

## 1. Môi trường Build Android (SEM-11, SEM-23, SEM-25)

| Thành phần | Cấu hình đã khóa | Ghi chú |
|---|---|---|
| OS | Windows 11 x64 | Đã kiểm chứng |
| Android SDK Platform | API 37 (`android-37.0`), extension 22 | `C:\Users\ADMIN\AppData\Local\Android\Sdk` |
| Build Tools | `36.0.0` | Sẵn sàng trong SDK |
| Gradle Wrapper | `9.6.0` | Checksum đã kiểm tra |
| Android Gradle Plugin (AGP) | `9.4.1` | Hỗ trợ API 37 |
| JDK chạy Gradle | Android Studio JBR `25.0.3` | `C:\Program Files\Android\Android Studio\jbr` |
| Bytecode Target | Java 17 | `JVM_17` |
| Kotlin / Compose Compiler | `2.4.10` | Compose BOM `2026.09.00` |
| Room Persistence | `2.8.5` | KSP `2.3.12` |
| WorkManager | `2.12.0` | Quản lý Worker chạy ngầm |

---

## 2. Môi trường Server & Snapshot Backend (SEM-13, SEM-26, SEM-27)

| Thành phần | Cấu hình | Ghi chú |
|---|---|---|
| Runtime | Node.js v24.15.0 (Windows) / v26.0.0 (macOS) | Không yêu cầu package ngoài |
| Package Manager | npm 11.12.1 | Module chuẩn `node:http`, `node:fs` |
| Cổng dịch vụ | Port `3000` (Mặc định) | Biến môi trường `PORT` tùy chỉnh |
| Lưu trữ Snapshot | `server/data/snapshot.json` | JSON bền vững, nguyên tử |
| Loopback Emulator | `http://10.0.2.2:3000` | Tự động phân giải về host |
| Reverse ADB | `adb reverse tcp:3000 tcp:3000` | Dành cho thiết bị thật |

---

## 3. Bản đồ Cổng và Kết nối (Network Connectivity)

```
[Android Emulator / Device]
       │
       ▼ (GET /api/bulletin, If-None-Match)
[Host Machine :3000] ───► [server/src/server.js] ───► [server/data/snapshot.json]
       ▲
       │ (POST /api/bulletin/update)
[CLI / Admin: update-cli]
```
