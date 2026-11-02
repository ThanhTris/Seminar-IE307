# SEM-12 — CHECKS và bàn giao hồ sơ thiết bị

- Người thực hiện: Vinh (`Vinh5905`), hỗ trợ thao tác bằng Codex.
- Ngày kiểm: **03/11/2026, 01:16–01:20 UTC+7**; các mốc HTTP tương ứng `02/11/2026 18:18–18:20 UTC`.
- Source app/server: `8f8d39e31b50fae946da050094eb3d3432fe540a`.
- Nhánh: `codex/SEM-12-device-profile`.
- Host: macOS 26.1 / Darwin 25.1.0 / ARM64.
- Build app/APK SHA-256: **Not run / null**; không build hoặc cài APK trong task này.
- Phạm vi: kiểm môi trường SEM-12; không phải run pilot/main, không có kết quả periodic/push/hybrid.
- Cập nhật hồ sơ 03/11/2026: Vinh xác nhận hiện không có OPPO để kiểm.
- Kết luận: **đủ hồ sơ đề nghị kiểm nhận SEM-12 theo nhánh acceptance cho phép ghi blocker**; emulator đã kiểm, OPPO/lịch sử dụng chưa khả dụng. Chưa đổi Status trên GitHub Project; không tuyên bố thiết bị thật hoặc tích hợp đã sẵn sàng.

## Đầu ra

- [DEVICES.md](../../environment/DEVICES.md): hồ sơ emulator, OPPO chờ kiểm, kết nối và cách kiểm lại.
- [EMULATOR_CHECKS.json](EMULATOR_CHECKS.json): kết quả thực từ ADB và HTTP probe, đã loại serial; giữ cả lần reverse chưa nhận response.
- CHECKS này: expected/actual, giới hạn, blocker và bàn giao.
- [REPRODUCE.md](REPRODUCE.md): lệnh kiểm cấu hình, khởi chạy server tạm, HTTP trực tiếp/reverse và cleanup; người clone không cần script nằm trong `.local/`.

## Kết quả kiểm

| Check | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| ADB host | Chạy được, có version | `1.0.41`, `37.0.1-15733141`; daemon cục bộ khởi động thành công | Pass |
| AVD inventory | Có emulator phù hợp | `-list-avds` trả `Pixel_7a`; metadata image Google Play ARM64, 16 KB, revision 9 | Pass |
| Emulator version | Đọc version thực | Ngoài sandbox: `37.1.11.0`, build `15917651` | Pass |
| Boot và ADB guest | `device`, `sys.boot_completed=1` | Khởi động AVD có sẵn; lần probe đầy đủ ghi boot `1` | Pass |
| Android/API/ABI | Lấy trực tiếp từ guest | Android 17 / SDK 37 / `arm64-v8a`; page size 16384 | Pass |
| Build | Ghi đúng bản runtime | Patch `2026-07-05`, incremental `16064790`; fingerprint trong hồ sơ/JSON | Pass |
| Google Play services | Có package, biết version | `26.33.32 (260400-974685114)`, installed, hidden=false, suspended=false | Pass (package) |
| Play Store | Có package, biết version | `53.7.23-34 [0] [PR] 1001145691`, installed, enabled=1 | Pass (package) |
| Baseline nguồn/pin | Ghi cấu hình đang quan sát | Pin 100%, AC/USB/Wireless=false, low_power=0, deep idle=ACTIVE | Pass (ghi nhận) |
| Server trên host | GET health trả 200 | Source repo bind 127.0.0.1, port tạm 58207, status=ok | Pass |
| Emulator → server | Nhận HTTP thật | Health 200; snapshot 200, ETag `"v1"`, version 1 qua `10.0.2.2:58207` | Pass |
| ADB reverse | Có HTTP qua guest localhost | Mapping được tạo; probe giữ stdin mở 2 giây trả 200, status=ok | Pass (sau kiểm lại) |
| Cleanup reverse | Gỡ đúng mapping thử | `reverse --remove tcp:58207` exit 0; mapping_remaining=false | Pass |
| Internet guest | Kiểm riêng với server local | `connectivitycheck.gstatic.com:80/generate_204` trả HTTP 204 | Pass (DNS/HTTP) |
| Đường mạng tới FCM | Kiểm TCP host đích | Guest `nc -z -w 8 fcm.googleapis.com 443` exit 0 | Pass (chỉ TCP) |
| Logcat | Ghi và đọc marker thực | `SEM12_LOG_PROBE_20261103` xuất hiện ở tag SEM12; không xóa buffer hiện có | Pass |
| App seminar trên AVD | Ghi đúng trạng thái | `pm path com.thanhtris.seminarie307` không tìm thấy | Chưa cài |
| Firebase token / nhận FCM thật | Có bằng chứng riêng nếu đã chạy | Không cài app, không dùng credential/token, không gửi push | Not run |
| OPPO / ColorOS / ADB / mạng | Đọc thực tế hoặc ghi blocker cụ thể | Inventory có 0 máy thật; Vinh xác nhận ngày 03/11 hiện không có OPPO để kiểm | Not run — B1 đã ghi rõ |
| Người giữ OPPO và lịch dùng | Có lịch thực hoặc ghi lý do chưa thể chốt | Chưa có OPPO để sử dụng; người giữ máy và lịch chưa xác lập, không ghi lịch giả | Chưa xác lập — B2 phụ thuộc B1 |

## Lần kiểm chưa đạt và cách kiểm lại

1. Trong sandbox, `emulator -version` báo `Incompatible processor ... neon`. Cùng executable chạy ngoài sandbox trả version đúng và khởi động AVD thành công. Không kết luận máy host thiếu ARM/NEON từ lỗi sandbox.
2. Khi ADB vừa nhận guest, `sys.boot_completed` còn trống. Probe đầy đủ sau đó ghi `1`; các kết quả mạng/package trong JSON là sau boot.
3. Probe HTTP qua reverse bằng `printf ... | nc` trả exit 0 nhưng không có HTTP response, kể cả ba lần kiểm lại. Exit code này **không được tính Pass**. Đổi probe để giữ stdin mở 2 giây trước EOF: `(printf '<HTTP_REQUEST>'; sleep 2) | nc -w 8 127.0.0.1 58207` nhận HTTP 200. Kết quả cho thấy đường reverse hoạt động khi dùng probe phù hợp; không suy các lần response trống là lỗi server. JSON giữ riêng từng lượt, không thay kết quả cũ.
4. Launcher báo dùng software rendering do bộ nhớ khả dụng dưới khuyến nghị. Không thay RAM/graphics, không wipe data, không cài system image mới hoặc thay cấu hình pin. Lần khởi động dùng `-no-snapshot-save`.

## Blocker và việc cần tiếp tục

| Blocker | Tác động | Cách gỡ / người thực hiện |
|---|---|---|
| B1 — Vinh xác nhận hiện không có OPPO để kiểm (03/11/2026) | Chưa biết model thực, Android/API/ColorOS, pin/mạng/Google Play services, ADB và đường server trên OPPO; không phải kết quả thiết bị thất bại | Khi có máy, Vinh kết nối USB, mở khóa/cấp quyền debugging và kiểm thật. Chưa có ngày gỡ blocker được xác nhận |
| B2 — Chưa có người giữ/lịch sử dụng đã xác nhận; phụ thuộc B1 | Chưa lên được lịch thiết bị thật cho pilot/main/video | Khi tìm được máy, Vinh chốt người giữ, khung giờ sử dụng và host; cập nhật sau khi thống nhất |
| Giới hạn tích hợp — app chưa cài, FCM thật chưa kiểm | Không dùng hồ sơ này để kết luận push/sync nền hoạt động | Nhận APK/config từ task tương ứng và chạy SEM-29/34 sau khi đủ đầu vào |

Tiêu chí task ghi rõ **"ADB nhận emulator và OPPO hoặc ghi blocker cụ thể"**. Vì vậy hồ sơ này đủ đề nghị Review với B1/B2 đã nêu; các kiểm tra cần máy thật vẫn phải chờ có thiết bị. Không đổi phạm vi nhóm hoặc kết luận OPPO đã sẵn sàng.

## Đối chiếu ba tiêu chí nghiệm thu SEM-12

- [x] ADB nhận emulator; OPPO không có để kiểm đã ghi thành B1/B2, thông số chưa biết để Not run, không suy phiên bản OS.
- [x] Hồ sơ phân biệt kết nối snapshot server với Internet/FCM; localhost chỉ dùng cho OPPO sau khi tạo reverse phù hợp, không lấy loopback PC làm địa chỉ trực tiếp trên OPPO.
- [x] DEVICES/CHECKS/evidence có thật, liên kết đọc được; các ca chưa chạy ghi rõ, không dùng kế hoạch làm kết quả.

Đây là kiểm nhận artifact cục bộ; chưa cập nhật trạng thái nguồn hoặc các section snapshot sinh tự động.

## Bàn giao

- **SEM-24:** đã có đầu ra bắt buộc của SEM-12 cùng alias `emulator-main`, OS/build/page size, kết nối server, đường đọc log và blocker OPPO. Có thể nhận hồ sơ để làm exporter/manifest trên emulator sau kiểm nhận SEM-12; hỗ trợ OPPO chưa được xác nhận, không đợi đủ kết quả chạy máy thật mới viết công cụ.
- **SEM-19/20/21:** có thể dùng hồ sơ emulator và các giới hạn đã ghi khi chuẩn bị nội dung; giữ rõ phần OPPO/FCM chưa kiểm.
- **SEM-42:** chưa đủ đầu vào OPPO; chờ B1/B2 và các dependency khác của task.

Mapping reverse tạm đã gỡ; snapshot repo không thay đổi. Server probe được dừng sau kiểm. Emulator được giữ mở để Vinh tiếp tục sử dụng.

## Kiểm chứng tài liệu

Các lệnh cấu hình cơ bản ở [DEVICES.md](../../environment/DEVICES.md), quy trình kiểm lại đầy đủ ở [REPRODUCE.md](REPRODUCE.md); dữ liệu đo gốc được chọn lọc trong JSON. `checked_at` trong JSON là lúc bắt đầu thu thập; các lượt reverse kiểm lại diễn ra sau đó, có mốc HTTP riêng đến 01:20 UTC+7. Rà tài liệu lần này giữ nguyên các giá trị quan sát cũ, không chạy lại môi trường hoặc ghi đè evidence.

| Kiểm artifact | Kết quả |
|---|---|
| Link tương đối trong DEVICES/CHECKS/REPRODUCE và task SEM-12 | Pass — tất cả đích nội bộ tồn tại |
| Parse EMULATOR_CHECKS.json | Pass |
| Đối chiếu boot/API/page size/package/HTTP/reverse cleanup/marker với JSON | Pass |
| Quét serial emulator và mẫu API key/private key/GitHub token | Pass — không tìm thấy trong bốn artifact và task SEM-12 |
| Whitespace/newline trên cả file mới chưa track | Pass |
| Cú pháp các code block shell (`sh -n`) | Pass; chỉ kiểm cú pháp, không chạy lại các lệnh |
| `git diff --check` | Pass; file mới được kiểm whitespace riêng vì chưa track |

Rà tài liệu bổ sung ngày 03/11/2026: đối chiếu lại acceptance gốc, cập nhật B1/B2 từ xác nhận của Vinh, thêm SDK app từ source và hướng dẫn tái lập. JSON quan sát cũ được giữ nguyên. Không đưa serial, account/token, service-account key hay raw logcat vào các artifact công khai. Các kiểm artifact này không thay thế phần kiểm OPPO còn thiếu.
