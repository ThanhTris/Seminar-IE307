# SEM-42 — Kiểm tra đối chiếu OPPO

## Pilot E01 ngày 20/11/2026

Bản debug chạy trên emulator và OPPO dùng commit app/server `76fece00110e0dba83c59b3e56bdabd2b4b7934e`. Manifest bàn giao ghi `NOT_READY`, nên các lượt đo dưới đây thuộc pha `pilot`.

| APK đã cài | SHA-256 |
| --- | --- |
| `app-debug.apk` | `814347f09ef9a61331910d7c4267fef827a4749377f3af53ae21fbb882ebaf5b` |
| `app-debug-androidTest.apk` | `b973f170fd61974029cc882c85641d65a79f416be515504e0cef56a3baa3e029` |

- **Emulator.** Dùng kết quả E01 đã ghi với cùng cặp APK. Cache chuyển v2 → v3 qua PERIODIC trong 90 phút, quan sát 2 chu kỳ tự nhiên. Thử mở một phiên kiểm tra nhanh mới dừng ở khâu khởi động và kết nối. [Kết quả emulator](https://github.com/ThanhTris/Seminar-IE307/blob/e6a1857da2a25feebd1bed3681d7e43d32d7843c/docs/evidence/SEM-53/EMULATOR_2026-11-20.md)
- **OPPO `run-sem42-oppo-e01-02` — `ABORTED`.** Find X9 dùng Android 17 (API 37), ColorOS V17.0.0 và kết nối server qua ADB reverse trong khi được cấp nguồn USB. App probe đạt, MANUAL nhận HTTP 200 và dựng cache v2. Từ 09:43:35 (UTC+7), ghi nhận 3 chu kỳ PERIODIC tự nhiên trước khi Android đưa app lên tiền cảnh lúc 10:34:34. Lần đầu áp dụng v3 lúc 09:58:36, hai lần sau trả HTTP 304. Phát hiện gián đoạn ở checkpoint 10:38:50 và đóng lượt. Export Android `PARTIAL` giữ 17 event v2, omission `periodic_cancelled` do schema. Kiểm tra riêng xác nhận lịch `CANCELLED`, reverse đã gỡ và server đã đóng store. Lượt này dùng để minh họa đồng bộ nền trước gián đoạn.
- **OPPO `run-sem42-oppo-e01-03` — `SUCCESS`.** Cửa sổ từ 10:42:37 đến 12:12:38 (UTC+7), Android elapsed realtime ghi đủ **90 phút 0,96 giây**. App probe đạt, MANUAL nhận HTTP 200 và dựng cache v4 khớp nội dung server. Server ghi v5 sau khi app về Home. Trong cửa sổ có **5 chu kỳ tự nhiên**, tính theo request ID riêng với `workAttempt=0`; mục tiêu là 3. Chu kỳ đầu nhận HTTP 200 và áp dụng v5 qua PERIODIC ở giây **930,021** tính từ đầu lượt trên đồng hồ Android. Bốn chu kỳ sau trả HTTP 304. Cache cuối v5.
- **Điều kiện lượt hoàn tất.** OPPO được cấp nguồn USB và kết nối server qua ADB reverse. Pin đầu/cuối 73%/75%, Battery Saver tắt lúc bắt đầu, app nằm ngoài danh sách miễn tối ưu pin. Các checkpoint ghi app ở nền và trạng thái idle `ACTIVE`. Số chu kỳ mô tả từng lượt pilot trong điều kiện thử của thiết bị tương ứng.
- **Evidence và cleanup.** Export trước khi hủy lịch đạt `COMPLETE`, gồm 25 event Android và 1 `server_updated` của lượt. Tệp trạng thái xác nhận lịch `CANCELLED`. Reverse cổng 3000 đã gỡ, server loopback đã dừng và nhả khóa store. Quyền mạng cục bộ cấp cho lượt thử đã được thu hồi qua Cài đặt. APK thử và cache được giữ trên OPPO. Manifest, canonical events và log gốc được lưu local.
- **E02 — `NOT_RUN`.** Bản debug ghi `FIREBASE_NOT_CONFIGURED`; chưa có lượt silent push đầu cuối.

## Kiểm tra chuẩn bị ngày 19/11/2026

- Base: `9caaf38f3932269bdcdd74aa0bfef0e9fc148271`.
- Kiểm ngày 19/11/2026 (UTC+7), trên máy Windows. Thiết bị dự kiến: OPPO Find X9, alias `oppo-find-x9`.
- Trạng thái đo: **NOT_RUN**. [Sáu slot dự kiến](../../../experiments/plans/SEM-42/OPPO_PLAN.json) là kế hoạch, chưa có run ID hoặc log OPPO.

| Kiểm tra | Expected | Actual | Kết quả |
| --- | --- | --- | --- |
| Candidate từ SEM-37 | APK, SHA-256, commit app/server và gate đã qua | Project Done. Manifest `NOT_READY`, gate false, APK và hash null. GitHub Releases và Actions không có APK bàn giao. | Blocked |
| Đường USB từ client | App GET qua `127.0.0.1:3000` và reverse trên đúng thiết bị | Đọc source thấy mặc định `10.0.2.2:3000`. Hàm đổi URL chưa có caller. Không thể xác nhận tuyến USB bằng reverse đơn lẻ. | Blocked |
| Thiết bị và baseline | Nhận đúng OPPO qua USB và đọc trạng thái trước khi đo | ADB đã nhận Find X9; xem thông số preflight bên dưới. Tối ưu pin theo app sẽ đo sau cài. | Pass kết nối, baseline đo Not run |
| Firebase E02 | Cấu hình test đúng package, quyền gửi và token hiện hành | Không có config chuẩn trong workspace hoặc biến tiến trình do run cung cấp. | Blocked |
| Server development | Server build, test và lắng nghe loopback | `npm ci`, `npm run build`, `npm test`: 22/22. `GET /health` trả API 2.0.0, status ok, trên `127.0.0.1:3000`. | Pass |
| E01 | 1 cửa sổ 90 phút, ≥3 cycle tự nhiên là mục tiêu | Chờ candidate và xác minh đường USB từ client. | Not run |
| E02 | 5 cửa sổ 120 giây, có provenance sender/callback/worker/cache | Chờ các điều kiện trên cùng Firebase. | Not run |
| Cleanup OPPO | Work thử đã dừng, reverse tạo trong phiên đã gỡ, quyền USB hoàn tác | Chưa có phiên trên OPPO. | Not run |

## Build thử trên emulator

Chạy `:app:testDebugUnitTest :app:assembleDebug :app:assembleDebugAndroidTest` với Android Studio JBR 25.0.3 và SDK local. Gradle báo `BUILD SUCCESSFUL`, 32/32 unit tests đạt. Cả hai APK qua `apksigner verify` và dùng chữ ký debug cùng certificate SHA-256 `6b88ff7e2835a23374715e1838327a6709cbc9d9573638e1c4dc3188be87e1c3`.

| Artifact development | Package / version | SHA-256 |
| --- | --- | --- |
| App | `com.thanhtris.seminarie307`, 0.1.0 (1), min 24, target 37 | `bc1732f12f2f42e114d592cfe1262ad124a3a414ab4a1e326245d7fdf66a24e1` |
| Test | `com.thanhtris.seminarie307.test` | `b973f170fd61974029cc882c85641d65a79f416be515504e0cef56a3baa3e029` |

Launcher được xác nhận là `MainActivity`. APK khai báo quyền mạng, quyền thông báo và các quyền do WorkManager/FCM thêm. Build development này dùng source base ở trên với Firebase local chưa cấu hình. APK và log build giữ local.

## Kiểm runtime development trên emulator

Hoàn tất lúc **10:59 UTC+7** trên `Medium_Phone_API_37.0`, Android API 37, alias `emulator-sem42-dev`. SHA-256 của cả hai APK đã cài khớp file build.

| Kiểm tra | Actual | Kết quả |
| --- | --- | --- |
| GET từ app | Probe đầu fail khi guest chưa có route. Sau khi guest nhận HTTP 200, chạy lại `PeriodicPilotControl` action `probe` và đạt `OK (1 test)`. | Pass sau retry |
| Setup và cache | Run `run-sem42-manual-dev`, mode PUSH, trigger MANUAL. Server commit v1, UI hiện cache v1 và log có `snapshot_applied` đúng source/alias/version. | Pass |
| Export v2 | Action `export-v2` cho 5 event Android hợp lệ ứng với enqueue, start, fetch start, fetch complete và apply. Một event `server_updated` qua validator SEM-24. Báo cáo `PARTIAL` giữ 1 omission `periodic_cancelled` do schema chưa hỗ trợ. | Pass kiểm đường export, dữ liệu partial |
| Lịch PERIODIC | Run `run-sem42-periodic`, snapshot WorkManager có đúng một work `ENQUEUED`. Action `cancel` đưa work sang `CANCELLED`, không còn lịch active. | Pass |
| Cleanup | Phiên emulator thử và listener trên cổng 3000 đã dừng. File build, log gốc và báo cáo omission giữ local. | Pass |

Các lượt trên là smoke test development. Chưa đo cycle tự nhiên 90 phút, E02 hay OPPO bằng APK development.

## Kiểm kết nối OPPO qua USB

Lúc **12:35 UTC+7 ngày 19/11/2026**, ADB xác nhận một thiết bị USB đã cấp quyền bằng `adb -d`. Các truy vấn sau đó chỉ đọc và nhắm đúng thiết bị theo serial local.

| Hạng mục | Kết quả |
| --- | --- |
| Thiết bị | OPPO Find X9, model CPH2797, alias `oppo-find-x9` |
| OS | Android 17 (API 37), ColorOS `V17.0.0` từ thuộc tính OPlus, bản vá 2026-10-01 |
| Google Play services | 26.45.31 |
| Nguồn, pin và mạng | Cấp nguồn USB, pin 38%, nhiệt độ pin đọc được 39,5 °C, Battery Saver tắt, mạng mặc định Wi-Fi |
| App và reverse | Chưa cài app Seminar, chưa có map reverse cho tcp:3000 |

Đây là thông số tại thời điểm kiểm kết nối. Đọc lại pin, mạng, idle và tối ưu pin theo app lúc bắt đầu run. Candidate trên `main` vẫn `NOT_READY`, APK và SHA-256 chưa được điền. Chưa cài, chưa tạo reverse và chưa chạy E01/E02 trên OPPO.

## Quy trình chuẩn bị cho các lượt tiếp theo

1. Nhận từ SEM-37 candidate đã chốt và cấu hình endpoint loopback cho worker. Kiểm hash, chữ ký, package và quyền trên emulator trước. Nếu OPPO đã có app Seminar, xác minh hash và chỉ tiếp tục khi dữ liệu thuộc phiên thử. Dừng nếu khác bản hoặc chưa rõ dữ liệu.
2. Người giữ máy cấp USB debugging. Chỉ chấp nhận host tin cậy. Xác nhận serial local bằng ADB và model qua Settings. Tất cả lệnh dùng `adb -s <serial-local>`. Kiểm `reverse --list`, rồi dùng `reverse --no-rebind tcp:3000 tcp:3000` nếu cổng trống. Probe từ client thật trước khi đo.
3. Theo [protocol](../../../experiments/PROTOCOL.md), mỗi slot có run ID riêng. Đặt baseline cache = server qua MANUAL ngoài cửa sổ, đợi work kết thúc rồi về Home để đo. Giữ nguồn, pin và mạng như lúc thiết lập. Không gọi JobScheduler dump hoặc instrumentation trong cửa sổ.
4. Sau cửa sổ, xuất canonical v2 cùng báo cáo omission, nối event theo alias/run/correlation và giữ timeout/failure/late event. Ghi lý do cùng timestamp nếu run bị gián đoạn. Bàn giao links thực cho SEM-43/44/45. Nếu clock chưa kiểm soát, không báo latency liên thiết bị.
5. Xác minh work của run đã kết thúc, gỡ đúng reverse đã tạo, dừng đúng server thử và kiểm trạng thái app. Người giữ máy rút cáp, hoàn tác USB debugging và quyền vừa cấp.

Nguồn: [candidate manifest](../../../release/CANDIDATE_MANIFEST.json), [hồ sơ thiết bị SEM-12](../../environment/DEVICES.md), [exporter SEM-24](../../../experiments/README.md).
