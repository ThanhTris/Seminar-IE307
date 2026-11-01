# Hướng dẫn Thiết lập và Chạy Toàn bộ Dự án — SEM-28 / M1

Tài liệu này tổng hợp toàn bộ các bước thiết lập môi trường máy chủ và ứng dụng Android phục vụ thử nghiệm các cơ chế đồng bộ dữ liệu (Manual, Periodic, Push, Hybrid).

---

## 1. Yêu cầu Tiền đề (Prerequisites)

| Thành phần | Phiên bản yêu cầu | Ghi chú |
|---|---|---|
| Hệ điều hành | Windows 11 / macOS | Đã kiểm chứng trên cả 2 môi trường |
| Node.js | v22.0.0+ hoặc v24.0.0+ | Dùng cho Snapshot Server & CLI |
| Android SDK | Compile/Target SDK 37, Build Tools 36.0.0 | Cài đặt qua Android Studio |
| JDK cho Gradle | Android Studio JBR `25.0.3` | Chọn làm Gradle JDK trong Android Studio |
| Android Emulator / Device | AVD API 37 (`Medium_Phone_API_37.0`) hoặc thiết bị thật | Min SDK 24, Target SDK 37 |

---

## 2. Khởi chạy Snapshot Server

Máy chủ cung cấp REST API cho bản tin và công cụ CLI để cập nhật dữ liệu.

```bash
# Di chuyển vào thư mục server
cd server

# Chạy server (lắng nghe cổng 3000)
npm start
```

*Địa chỉ truy cập:*
- Trình duyệt / Máy host: `http://127.0.0.1:3000/health`
- Từ Android Emulator: `http://10.0.2.2:3000/api/bulletin`

---

## 3. Build và Cài đặt Ứng dụng Android

Chạy các lệnh từ thư mục gốc của dự án bằng PowerShell:

```powershell
# Thiết lập biến môi trường trỏ SDK & JBR
$env:JAVA_HOME = 'C:\Program Files\Android\Android Studio\jbr'
$env:ANDROID_HOME = 'C:\Users\ADMIN\AppData\Local\Android\Sdk'
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
$env:PATH = "$env:JAVA_HOME\bin;$env:ANDROID_HOME\platform-tools;$env:PATH"

# Build debug APK
cd android
.\gradlew.bat :app:assembleDebug

# Cài đặt APK vào emulator hoặc thiết bị đang kết nối
adb install -r app\build\outputs\apk\debug\app-debug.apk
```

---

## 4. Kịch bản Kiểm thử Đồng bộ Thủ công (Cột mốc M1)

1. **Khởi chạy ban đầu:**
   - Đảm bảo server đang chạy (`npm start` trong `server/`).
   - Mở ứng dụng "Seminar IE307" trên thiết bị/emulator.
   - Trạng thái ban đầu: Bản tin hiển thị dữ liệu ban đầu hoặc rỗng, Version cache hiển thị `—` hoặc `v1`.
2. **Tạo dữ liệu mới từ Server:**
   - Mở một terminal mới tại thư mục `server/`:
     ```bash
     npm run update -- --title "Bản tin đột xuất" --body "Nội dung kiểm thử M1"
     ```
   - Terminal server sẽ thông báo snapshot đã tăng lên `v2`.
3. **Kích hoạt đồng bộ thủ công trên Android:**
   - Trên màn hình ứng dụng, bấm nút **"Đồng bộ thủ công"**.
   - Nút hiển thị trạng thái `Đang xếp lịch…` trong khi `SyncWorker` chạy nền.
   - Sau khi hoàn thành:
     - Version cache chuyển thành `v2`.
     - Tab **Bản tin** hiển thị bản tin "Bản tin đột xuất" vừa tạo.
     - Tab **Timeline** hiển thị chuỗi sự kiện: `work_enqueued` -> `work_started` -> `snapshot_applied` (outcome: `applied`, version: `v2`).
4. **Kiểm tra ngoại tuyến (Offline Persistence):**
   - Đóng ứng dụng hoàn toàn (Kill process).
   - Bật chế độ máy bay (Airplane mode) hoặc tắt kết nối mạng.
   - Mở lại ứng dụng: Toàn bộ bản tin và dòng thời gian vẫn hiển thị đầy đủ từ Room Database, không phát sinh lỗi và không tự động gọi API khi mở app.
