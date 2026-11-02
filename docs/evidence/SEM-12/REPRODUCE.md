# SEM-12 — Cách kiểm lại hồ sơ emulator

Đây là hướng dẫn tái lập các kiểm môi trường đã ghi trong [CHECKS](CHECKS.md). Kết quả của lần kiểm cũ nằm trong [EMULATOR_CHECKS.json](EMULATOR_CHECKS.json); không chép expected trong hướng dẫn thành kết quả mới. Script probe lần đầu giữ local tại `.local/sem12/`, không cần file đó để làm theo tài liệu này.

## 1. Chọn đúng emulator

Trên máy Vinh, SDK nằm tại `~/Library/Android/sdk`; sửa đường dẫn nếu chạy máy khác. Chỉ khởi động AVD khi chưa chạy; không wipe data hoặc đổi image để kiểm lại hồ sơ.

```sh
SEM12_SDK="$HOME/Library/Android/sdk"
"$SEM12_SDK/platform-tools/adb" version
"$SEM12_SDK/emulator/emulator" -version
"$SEM12_SDK/emulator/emulator" -list-avds
"$SEM12_SDK/platform-tools/adb" devices -l

# Khi Pixel_7a chưa chạy; giữ cửa sổ này mở.
"$SEM12_SDK/emulator/emulator" -avd Pixel_7a -no-snapshot-save
```

Ở terminal khác, đặt lại `SEM12_SDK` như trên, xem inventory local và chọn serial của AVD `Pixel_7a`. Ánh xạ serial đó với alias công khai `emulator-main`; không commit serial. Nếu có nhiều AVD, đối chiếu thêm `ro.boot.qemu.avd_name` trước khi kiểm.

```sh
SEM12_SDK="$HOME/Library/Android/sdk"
SEM12_DEVICE='<SERIAL_LOCAL>'
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getprop ro.boot.qemu.avd_name
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getprop sys.boot_completed
```

Chỉ bắt đầu kiểm package/network khi trạng thái ADB là `device` và boot trả `1`. Nếu còn trống/offline/unauthorized, ghi đúng trạng thái và kiểm lại sau; chưa tính Pass. Trong lần kiểm cũ, chạy emulator ngoài sandbox mới đọc version/khởi động được; lỗi `neon` trong sandbox không được ghi thành lỗi CPU host.

## 2. Thu cấu hình và trạng thái

```sh
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getprop ro.product.model
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getprop ro.product.manufacturer
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getprop ro.build.version.release
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getprop ro.build.version.sdk
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getprop ro.build.version.security_patch
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getprop ro.build.version.incremental
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getprop ro.build.fingerprint
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getprop ro.product.cpu.abi
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getconf PAGE_SIZE
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell pm path com.google.android.gms
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell pm path com.android.vending
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell pm path com.thanhtris.seminarie307
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell dumpsys package com.google.android.gms
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell dumpsys package com.android.vending
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell dumpsys battery
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell settings get global low_power
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell dumpsys deviceidle get deep
```

Package dump có thể chứa cả bản đang dùng và bản hệ thống ẩn: lấy `versionName`/`versionCode` trong section package đang dùng, trước `Hidden system packages:`, cùng trạng thái user tương ứng. Public evidence chỉ giữ version và các cờ installed/hidden/suspended/stopped/enabled, không công bố nguyên dump. Pin chỉ giữ nguồn điện/status/level/scale/temperature.

System image trong lần kiểm cũ lấy từ `image.sysdir.1` của `~/.android/avd/Pixel_7a.avd/config.ini`, sau đó đọc `source.properties` của image đó trong SDK. Đối chiếu `AvdId`, ABI, PlayStore, RAM và image path; tránh công bố toàn bộ config chứa định danh local. Giữ riêng SDK metadata `37.1` và API runtime `37`.

## 3. Chạy server tạm, chỉ đọc dữ liệu

Terminal A, từ thư mục `server/` của checkout được kiểm:

```sh
node --input-type=module -e 'import {createServer} from "./src/server.js"; const server=createServer(); server.listen(0,"127.0.0.1",()=>console.log(JSON.stringify({sem12_probe_port:server.address().port})));'
```

Node in ra cổng tự cấp; ghi lại cổng của lần kiểm mới. Terminal B dưới đây dùng `58207` làm **ví dụ của lần kiểm cũ**, phải thay bằng cổng vừa in. Server này bind loopback, không cần mở LAN và không gọi API cập nhật snapshot.

```sh
SEM12_PORT=58207
curl --silent --show-error --max-time 10 "http://127.0.0.1:$SEM12_PORT/health"

"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell "(printf 'GET /health HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n'; sleep 2) | nc -w 8 10.0.2.2 $SEM12_PORT"
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell "(printf 'GET /api/bulletin HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n'; sleep 2) | nc -w 8 10.0.2.2 $SEM12_PORT"
```

Pass khi nhận HTTP 200 và nội dung phù hợp: health `status=ok`, snapshot có version/ETag. Version có thể đổi giữa các lần kiểm; ghi giá trị mới, không bắt buộc phải bằng `1` của lần cũ. HTTP qua shell guest kiểm đường mạng; chưa chứng minh app đã fetch/cập nhật Room.

## 4. Thử reverse và dọn mapping

Xem `reverse --list` trước. Chỉ tạo mapping nếu cổng guest được chọn chưa dùng; nếu trùng, chọn cổng guest khác và giữ nguyên mapping có sẵn. Các lệnh sau giả định cổng guest bằng cổng host và không xung đột:

```sh
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" reverse --list
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" reverse "tcp:$SEM12_PORT" "tcp:$SEM12_PORT"
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell "(printf 'GET /health HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n'; sleep 2) | nc -w 8 127.0.0.1 $SEM12_PORT"

# Gỡ đúng mapping vừa tạo kể cả khi probe thất bại.
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" reverse --remove "tcp:$SEM12_PORT"
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" reverse --list
```

Exit 0 mà response trống chưa đạt. Trong lần cũ, probe giữ stdin mở thêm 2 giây nhận HTTP 200; các lần đóng stdin ngay không nhận response được giữ riêng trong JSON. Sau thử, xác nhận mapping vừa tạo không còn; không dùng `--remove-all`.

## 5. Internet, TCP FCM và đường lấy log

```sh
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell "(printf 'GET /generate_204 HTTP/1.1\r\nHost: connectivitycheck.gstatic.com\r\nConnection: close\r\n\r\n'; sleep 2) | nc -w 8 connectivitycheck.gstatic.com 80"
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell nc -z -w 8 fcm.googleapis.com 443
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell log -p i -t SEM12 SEM12_LOG_PROBE
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" logcat -d -v brief -s SEM12:I '*:S'
```

Ghi riêng HTTP Internet (lần cũ 204), TCP FCM (lần cũ exit 0) và marker đọc được. Đây không phải test TLS/OAuth, token, FCM delivery hoặc sync nền. Không cần tài khoản Google, credential Firebase hoặc cài app để kiểm marker SEM-12. Không xóa buffer log; public evidence chỉ giữ dòng marker. Không dùng raw log app vì source hiện có lệnh log token FCM.

Kiểm xong, dừng server ở terminal A bằng Ctrl+C. Không tắt emulator đang được dùng cho công việc khác. Nếu lần kiểm mới khác build/config, ghi ngày, commit, alias, expected/actual và kết quả mới trong hồ sơ riêng; không ghi đè lịch sử JSON ngày 03/11 để làm như kết quả cũ đã thay đổi.

## 6. Phần OPPO và bàn giao

Vinh xác nhận hiện không có OPPO để kiểm. Giữ OS/ColorOS/ADB/mạng/log là Not run, người giữ/lịch là chưa xác lập, B1/B2 là blocker. Đây là đầu ra audit được chấp nhận theo nhánh "hoặc ghi blocker cụ thể" của SEM-12; không phải kết quả thí nghiệm thất bại và không tự hủy phạm vi OPPO của nhóm.

Khi có máy: kiểm identity/OS/ColorOS thật qua ADB và Settings, pin baseline, Google Play services, server qua reverse/LAN, Internet và log; chốt người giữ/lịch. Với OPPO, chưa dùng `10.0.2.2` như emulator và chỉ dùng guest localhost sau khi reverse hoạt động. Nếu cần sửa base URL của app, bàn giao đúng task tích hợp, không sửa core app trong task hồ sơ.
