# Hồ sơ OPPO và emulator — SEM-12

Kiểm tra **03/11/2026, 01:16–01:20 (UTC+7)** bởi Vinh (`Vinh5905`), hỗ trợ thao tác bằng Codex. Code được kiểm: `8f8d39e31b50fae946da050094eb3d3432fe540a`; nhánh tài liệu `codex/SEM-12-device-profile`.

**Trạng thái bàn giao:** emulator đã được khởi động và kiểm ADB, cấu hình, package Google, kết nối server, Internet và logcat. Ngày 03/11/2026, Vinh xác nhận **hiện không có OPPO để kiểm**; phần máy thật được bàn giao dưới dạng blocker, không phải lỗi thiết bị. Hồ sơ đủ để đề nghị kiểm nhận SEM-12 theo tiêu chí cho phép ghi blocker; chưa thay Status trên Project. [CHECKS](../evidence/SEM-12/CHECKS.md), [kết quả máy đọc được](../evidence/SEM-12/EMULATOR_CHECKS.json) và [cách tái lập](../evidence/SEM-12/REPRODUCE.md).

## Máy host và công cụ

| Thành phần | Giá trị quan sát |
|---|---|
| Host | macOS 26.1, Darwin 25.1.0, ARM64 |
| SDK local | `~/Library/Android/sdk` |
| ADB | Android Debug Bridge 1.0.41; platform-tools `37.0.1-15733141` |
| Emulator | `37.1.11.0`, build `15917651` |
| AVD có sẵn | `Pixel_7a` |
| Thiết bị vật lý tại lúc kiểm | 0 thiết bị được liệt kê bởi ADB |

Đây là máy Vinh. Cấu hình Windows trong [ANDROID_BUILD.md](ANDROID_BUILD.md) và máy Tâm trong [SERVER_FIREBASE.md](SERVER_FIREBASE.md) là những môi trường riêng.

## Emulator đã kiểm: `emulator-main`

| Thuộc tính | Giá trị thực tế / nguồn |
|---|---|
| Alias công khai | `emulator-main`; serial ADB chỉ sử dụng local |
| AVD / trạng thái boot | `Pixel_7a`; ADB ở trạng thái `device`; `sys.boot_completed=1` |
| Model guest / hãng | `sdk_gphone16k_arm64` / Google |
| Android / API runtime | Android `17` / SDK `37`, đọc bằng `getprop` |
| Security patch | `2026-07-05` |
| Build incremental | `16064790` |
| Build fingerprint | `google/sdk_gphone16k_arm64/emu64a16k:17/CP31.260623.012/16064790:user/dev-keys` — định danh bản build, không phải serial |
| ABI / page size | `arm64-v8a` / `16384` byte |
| System image | `system-images/android-37.1/google_apis_playstore_ps16k/arm64-v8a/`, revision `9`, extension `23` từ metadata SDK |
| Google Play services | Có, `26.33.32 (260400-974685114)`, versionCode `263332035`; installed, không hidden/suspended |
| Google Play Store | Có, `53.7.23-34 [0] [PR] 1001145691`, versionCode `85372340`; installed, enabled |
| App seminar | Package `com.thanhtris.seminarie307` chưa cài trong emulator này |
| Cấu hình app trong source | `compileSdk=37`, `targetSdk=37`, `minSdk=24`, versionName `0.1.0`, versionCode `1` từ `android/app/build.gradle.kts`; chưa phải thông số APK đã cài |
| Pin / nguồn tại lúc kiểm | 100%; AC/USB/Wireless powered đều false; Battery Saver `0` |
| Deep idle tại lúc kiểm | `ACTIVE`; chưa thực hiện ca Doze |
| Log | Ghi marker tag `SEM12` và đọc lại bằng logcat thành công |

Metadata system image ghi `37.1`, trong khi runtime `ro.build.version.sdk` trả `37`: giữ riêng hai giá trị, không suy API runtime từ tên AVD hoặc thư mục image.

Khi khởi động, emulator báo thiếu bộ nhớ khả dụng so với mức khuyến nghị và dùng software rendering. Log launcher cho biết tăng RAM guest lên 4096 MB dù config AVD ghi 2048 MB. Đây là điều kiện của lần kiểm môi trường; trước các run đo cần ghi lại tài nguyên/rendering thực tế, tránh chạy tác vụ host nặng đồng thời. SEM-12 chưa kiểm khả năng chạy APK trên image 16 KB và chưa tạo dữ liệu pilot/main.

## OPPO: `oppo-find-x9` — chưa có thiết bị để kiểm

| Thuộc tính | Trạng thái |
|---|---|
| Thiết bị theo phạm vi nhóm | OPPO Find X9; chưa đối chiếu model bằng ADB/Settings |
| Android / API / ColorOS / build / ABI | **Not run**; không suy từ tên model |
| ADB / quyền USB debugging | **Not run**; inventory lần kiểm có 0 máy thật; sau đó Vinh xác nhận hiện không có OPPO để kiểm |
| Pin, Battery Saver, tối ưu pin theo app, mạng | **Not run** |
| Google Play services, Internet, FCM | **Not run** |
| Người đang giữ máy | Chưa xác định; không suy Vinh hoặc thành viên khác đang giữ máy |
| Khung giờ mượn / máy host / cách kết nối | Chưa thể xác lập khi chưa có thiết bị; chưa có lịch đã thống nhất |

Nguồn xác nhận tình trạng chưa có máy: trao đổi với Vinh ngày 03/11/2026 ("không có OPPO"). Không đặt ngày mượn dự kiến thành lịch đã chốt. Việc chưa có máy được ghi thành blocker B1; thông tin người giữ/lịch B2 phụ thuộc việc tìm được máy. Phạm vi đối chiếu OPPO trong kế hoạch nhóm vẫn được giữ; hồ sơ này không tự hủy SEM-42 hoặc thay OPPO bằng emulator.

Khi nhận OPPO: kiểm model/OS/API/ColorOS thực tế, quyền ADB, nguồn điện/pin/mạng, Google Play services và lấy log; ghi cấu hình tối ưu pin baseline từ Settings. Chốt người giữ máy và lịch dành cho pilot, main, quay video theo [protocol](../EXPERIMENT_PROTOCOL.md). Nếu đổi cấu hình pin ở task sau, lưu thành cấu hình thử riêng và ghi cách hoàn tác.

## Kết nối server và Internet

Server được chạy từ source repo, bind **`127.0.0.1`**, cổng tự cấp **`58207`** trong lần kiểm; chỉ gọi GET `/health` và `/api/bulletin`. Sau kiểm đã dừng server tạm. Không đổi snapshot hoặc cấu hình URL của app.

| Đường kiểm | Kết quả thực tế | Phạm vi xác nhận |
|---|---|---|
| Host → `127.0.0.1:58207/health` | HTTP `200`, `status=ok` | Server hiện tại chạy được trên host |
| Emulator → `10.0.2.2:58207/health` | HTTP `200`, `status=ok` | Guest truy cập server trên host |
| Emulator → `10.0.2.2:58207/api/bulletin` | HTTP `200`, ETag `"v1"`, snapshot version `1` | Đọc được snapshot qua mạng guest |
| Emulator → ADB reverse → `127.0.0.1:58207/health` | HTTP `200` với probe giữ stdin mở 2 giây | Mapping reverse hoạt động; đã gỡ mapping thử |
| Emulator → `connectivitycheck.gstatic.com:80/generate_204` | HTTP `204` | DNS và HTTP Internet hoạt động |
| Emulator → `fcm.googleapis.com:443` | `nc -z` exit `0` | TCP tới FCM host hoạt động; chưa kiểm TLS/OAuth/quyền gửi/token hoặc nhận push |
| OPPO → server bằng reverse/LAN | **Not run** | Chờ thiết bị; không coi kết quả emulator là bằng chứng cho OPPO |

`58207` chỉ là cổng của probe, không phải cấu hình mặc định mới. Khi server chạy cổng `3000`, emulator dùng `http://10.0.2.2:3000`. OPPO có thể dùng `http://127.0.0.1:3000` **sau khi** tạo ADB reverse trên đúng host chạy server; hoặc dùng IP LAN của host khi server bind LAN và kiểm firewall. Chưa sửa app để chạy trên OPPO; code hiện mặc định `http://10.0.2.2:3000`.

ADB reverse không cấp Internet cho FCM. Google Play services đã cài và TCP thông chưa chứng minh app lấy được token hay nhận push. Cấu hình Firebase thật và test nhận push vẫn cần kiểm riêng ở SEM-33/34/35.

## Cách kiểm lại và lấy log

Serial được chọn từ inventory local; tài liệu/evidence công khai chỉ ghi alias. Không dán raw `adb devices -l` hoặc toàn bộ logcat vào repo.

```sh
SEM12_SDK="$HOME/Library/Android/sdk"
"$SEM12_SDK/emulator/emulator" -list-avds
"$SEM12_SDK/platform-tools/adb" version
"$SEM12_SDK/platform-tools/adb" devices -l

# Chọn serial local của đúng alias; không commit giá trị thật.
SEM12_DEVICE='<SERIAL_LOCAL>'
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getprop sys.boot_completed
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getprop ro.build.version.release
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getprop ro.build.version.sdk
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell pm path com.google.android.gms
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell getconf PAGE_SIZE

# Kiểm đường lấy log bằng marker riêng, không xóa buffer log hiện có.
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" shell log -p i -t SEM12 SEM12_LOG_PROBE
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" logcat -d -v brief -s SEM12:I '*:S'

# Chỉ dùng khi host đang chạy server tại cổng 3000 và chưa có mapping xung đột.
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" reverse --list
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" reverse tcp:3000 tcp:3000
# Kiểm xong: gỡ đúng mapping vừa tạo, giữ nguyên mapping của tác vụ khác.
"$SEM12_SDK/platform-tools/adb" -s "$SEM12_DEVICE" reverse --remove tcp:3000
```

Để thu log app ở task sau, giữ bản gốc trong `.local/` hoặc `experiments/private/` rồi lọc dữ liệu nhạy cảm trước công bố. Code app hiện có log token FCM, nên không công bố raw logcat ngay cả khi đã lọc theo PID. Export event theo schema/run_id thuộc SEM-24; marker SEM-12 chỉ kiểm đường lấy log hệ thống.

## Bàn giao và phần còn thiếu

- **SEM-24:** hồ sơ emulator và blocker OPPO đã đủ làm đầu vào kiểm nhận của task audit SEM-12. Có thể triển khai exporter/manifest trên emulator sau khi kiểm nhận bàn giao; hỗ trợ OPPO giữ trạng thái chưa kiểm, không cần giả định cấu hình OPPO để viết công cụ.
- **SEM-19/20/21:** nhận cấu hình emulator đã quan sát và giới hạn chưa kiểm OPPO/FCM; không gọi đây là kết quả thử nghiệm.
- **SEM-42:** còn chờ model/OS/ColorOS, mạng/pin và lịch OPPO thực tế trước khi chạy đối chiếu.

SEM-12 cho phép nghiệm thu hồ sơ có blocker cụ thể (xem [tiêu chí task](../../tasks/backlog/SEM-12.md)); thiếu OPPO không tự chặn việc đưa hồ sơ này vào Review. Trước khi chạy ca trên OPPO, vẫn phải có thiết bị, lịch sử dụng và kiểm thật B1/B2. Status/đầu vào trên Project chỉ thay đổi khi workflow nguồn được cập nhật, không suy đã Done từ tài liệu này.

Các thông tin phục vụ run nhưng chưa thu trong SEM-12: transport Wi-Fi/mobile cụ thể, trạng thái sạc trong run, clock offset host/guest, cấu hình pin theo app và APK checksum. Những trường này cần thu tại setup/run theo SEM-16/24 và protocol; kết quả HTTP/TCP ở trên không thay thế manifest run.
