# Hướng dẫn Thiết lập và Chạy Toàn bộ Dự án — SEM-28 / Cột mốc M1

Tài liệu này là chỉ mục tổng hợp hướng dẫn thiết lập môi trường, biên dịch, khởi chạy và kiểm thử toàn bộ hệ thống từ máy chủ (Server v2) đến ứng dụng Android (Client), xác thực cột mốc đồng bộ đầu cuối **M1** (End-to-End Manual Sync) và công cụ trích xuất log thực nghiệm.

---

## 1. Yêu cầu Tiền đề (Prerequisites)

| Thành phần | Phiên bản yêu cầu | Đường dẫn / Ghi chú |
|---|---|---|
| **Hệ điều hành** | Windows 11 x64 / macOS ARM64 | Đã kiểm chứng tương thích đa nền tảng |
| **Node.js** | v22.0.0+ hoặc v24.15.0+ | Dùng cho Snapshot Server v2 & Update CLI |
| **npm** | 10.x+ hoặc 11.x+ | Kèm `package-lock.json` chuẩn hóa (SEM-27) |
| **JDK cho Android** | Android Studio JBR `25.0.3` (Java 17/21 bytecode) | Mặc định: `C:\Program Files\Android\Android Studio\jbr` |
| **Android SDK** | Compile/Target SDK 37, Build Tools 36.0.0 | Mặc định: `C:\Users\ADMIN\AppData\Local\Android\Sdk` |
| **Gradle** | Wrapper `9.6.0`, AGP `9.4.1` | Khóa tại SEM-11 & SEM-23 |
| **Android Emulator** | API 37 (`Medium_Phone_API_37.0` hoặc `Pixel_7a`) | Google APIs Play Store image, Min SDK 24 |
| **Python** | 3.10+ | Dùng chạy exporter log và audit script |

---

## 2. Khởi chạy Snapshot Server v2 (SEM-27)

Máy chủ cung cấp REST API cho bản tin theo hợp đồng API 2.0.0 ([`docs/API.md`](API.md)) và công cụ dòng lệnh cập nhật dữ liệu.

```bash
# 1. Di chuyển vào thư mục server
cd server

# 2. Cài đặt các gói phụ thuộc (nếu cài lần đầu hoặc sau pull mới)
npm ci

# 3. Biên dịch TypeScript sang JavaScript
npm run build

# 4. Chạy kiểm thử tự động (9/9 tests)
npm test

# 5. Khởi chạy server (lắng nghe cổng 3000 mặc định)
npm start
```

*Kiểm tra sức khỏe dịch vụ:*
- Trên trình duyệt máy host: `http://127.0.0.1:3000/health` (trả về `{ "status": "ok", "version": ... }`).
- Lấy danh sách bản tin: `http://127.0.0.1:3000/api/bulletin`.
- Phân giải mạng từ Android Emulator: `http://10.0.2.2:3000/api/bulletin`.

---

## 3. Biên dịch và Cài đặt Ứng dụng Android (SEM-23, SEM-25, SEM-28)

Thực hiện trong PowerShell tại thư mục gốc của dự án:

```powershell
# 1. Thiết lập biến môi trường trỏ JDK JBR và Android SDK
$env:JAVA_HOME = 'C:\Program Files\Android\Android Studio\jbr'
$env:ANDROID_HOME = 'C:\Users\ADMIN\AppData\Local\Android\Sdk'
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
$env:PATH = "$env:JAVA_HOME\bin;$env:ANDROID_HOME\platform-tools;$env:PATH"

# 2. Di chuyển vào thư mục android
cd android

# 3. Biên dịch APK debug và chạy unit test
.\gradlew.bat :app:assembleDebug :app:testDebugUnitTest

# 4. Kiểm tra thiết bị / emulator đã kết nối
adb devices

# 5. Cài đặt APK vào emulator hoặc thiết bị
adb install -r app\build\outputs\apk\debug\app-debug.apk
```

*Nếu dùng thiết bị thật qua cáp USB:*
```powershell
# Chuyển tiếp cổng kết nối từ thiết bị về máy host
adb reverse tcp:3000 tcp:3000
```

---

## 4. Kịch bản Kiểm chứng Cột mốc M1 (End-to-End Manual Sync)

Quy trình xác nhận hệ thống hoạt động thực tế đầu cuối qua 4 bước:

1. **Khởi động ban đầu:**
   - Server đang chạy (`npm start` trong thư mục `server/`).
   - Mở ứng dụng "Seminar IE307" trên Android Emulator.
   - Trạng thái ban đầu: Thẻ trạng thái hiển thị Version `—` hoặc `v1`, tab Bản tin hiển thị rỗng hoặc dữ liệu khởi tạo, nút "Đồng bộ thủ công" sẵn sàng.

2. **Phát hành bản tin mới từ Server:**
   - Mở terminal tại thư mục `server/`, chạy lệnh:
     ```bash
     npm run update -- --title "Bản tin Cột mốc M1" --body "Nội dung xác thực đồng bộ thủ công đầu cuối"
     ```
   - Terminal Server thông báo snapshot đã được lưu bền vững và tăng version lên `v2` (hoặc phiên bản kế tiếp).

3. **Thực hiện đồng bộ thủ công trên Android:**
   - Trên màn hình app, nhấn nút **"Đồng bộ thủ công"**.
   - Giao diện nút hiển thị `Đang xếp lịch…`.
   - `RealBulletinUiGateway` chuyển tiếp tới `SyncWorkEnqueuer`, xếp lịch `OneTimeWorkRequest` và ghi nhận `work_enqueued`.
   - `SyncWorker` chạy ngầm gửi GET kèm ETag tới Server, nhận HTTP 200, Room lưu snapshot trong transaction nguyên tử.
   - Sau vài giây:
     - Version cache chuyển sang phiên bản mới.
     - Tab **Bản tin** hiển thị bản tin "Bản tin Cột mốc M1".
     - Tab **Timeline** ghi nhận chuỗi sự kiện hoàn chỉnh: `work_enqueued` ➔ `work_started` ➔ `snapshot_applied` (outcome: `applied`, version: mới).

4. **Kiểm tra ngoại tuyến (Offline Persistence):**
   - Đóng hoàn toàn ứng dụng (Vuốt tắt khỏi Recents hoặc chạy `adb shell am force-stop com.thanhtris.seminarie307`).
   - Tắt kết nối mạng trên emulator (`adb shell svc wifi disable`, `adb shell svc data disable`).
   - Mở lại ứng dụng: Toàn bộ bản tin và dòng thời gian hiển thị tức thì từ Room SQLite database (`seminar_bulletin.db`), không phát sinh lỗi và không gọi network request khi khởi động.

---

## 5. Xuất Log Thực nghiệm và Đối chiếu Manifest (SEM-24)

Dự án cung cấp công cụ tự động hóa xuất log và đối chiếu manifest ([`experiments/README.md`](../experiments/README.md)):

```bash
# Kiểm tra bộ test xuất log
python experiments/scripts/tests/test_export_logs.py

# Xuất log từ SQLite Android và Server logcat về tệp JSONL
python experiments/scripts/export_logs.py --run-id run-manual-live --manifest experiments/RUN_MANIFEST_TEMPLATE.json --output-dir experiments/exports/run-manual-live
```

---

## 6. Khắc phục Sự cố Thường gặp (Troubleshooting)

- **Cổng 3000 bị chiếm dụng (EADDRINUSE):** Chạy `Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process` trên PowerShell hoặc đổi cổng qua biến môi trường `$env:PORT = '3001'`.
- **Khóa `state.json.lock` cũ sau khi server bị tắt đột ngột (SIGKILL):** Kiểm tra tiến trình cũ đã dừng hoàn toàn, sau đó xóa tệp `server/data/state.json.lock`.
- **Android không kết nối được Server host (`Connection refused`):** Đảm bảo dùng URL `http://10.0.2.2:3000/api/bulletin` đối với Emulator, hoặc chạy `adb reverse tcp:3000 tcp:3000` đối với thiết bị thật.
- **Lỗi Windows fsync thư mục:** Snapshot server đã được cấu hình tối ưu để bỏ qua `fsync` directory trên Windows (commit `af60deb`), bảo đảm an toàn trên mọi hệ điều hành.
