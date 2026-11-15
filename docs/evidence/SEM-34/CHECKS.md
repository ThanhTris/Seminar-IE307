# SEM-34 — Kiểm đầu vào và pilot push E02

## Nhận dạng lần kiểm

- Vinh (`Vinh5905`) thực hiện ngày **12/11/2026, UTC+7**. Hạn gốc 03/11/2026 22 giờ được giữ trong task.
- Đã pull `main` đến `decdef675e9eb11104bfb77cef57565d72df05d8`, tạo nhánh `codex/SEM-34-push-pilot`.
- Nhận [SEM-16](../SEM-16/CHECKS.md), [SEM-24](../SEM-24/CHECKS.md), [SEM-32](../SEM-32/CHECKS.md), [SEM-35](../SEM-35/CHECKS.md), [SEM-33](../SEM-33/CHECKS.md) và [PUSH](../../PUSH.md). Các task nguồn Done trên Project lúc bắt đầu. Code SEM-32/33/35 đã merge qua PR #20/#22/#16.
- App và server dùng commit `decdef6`. APK app SHA-256 `39255f700a271d73d8bc4cd16f3741e11f1446980542125d5eb0efdf35dc2f39`, đã đọc APK cài trên emulator và kiểm hash khớp.
- Harness androidTest ở commit `9f7f0e5`. Test APK SHA-256 `256586356d143e0667320197130dab5de00533e47ef3892b5f4a51f23395e5b8`. Source harness được ghi hash riêng trong [PREFLIGHT.json](PREFLIGHT.json).
- macOS ARM64, JDK 21.0.11, Gradle 9.6.0, Android API/target 37, WorkManager 2.12.0. Emulator `emulator-main` là Google `sdk_gphone16k_arm64`, Android 17, ARM64, page size 16384, security patch 2026-07-05, Google Play services 26.43.30.

## Expected và actual

| Hạng mục | Expected | Actual | Kết quả |
|---|---|---|---|
| Build app/test APK | Build từ source đã nhận | `assembleDebug`, `assembleDebugAndroidTest` đạt trong 2 phút 44 giây | Pass |
| Unit tests Android | Token, callback adapter, dedup và UI filter hoạt động | 31 tests đạt gồm token 8, adapter 6, input policy 15, filter 2 | Pass — JVM |
| Server/sender | Build và bộ test hiện có đạt | `npm ci --ignore-scripts`, `npm test` đạt 22/22 | Pass — local/fixture |
| APK trên emulator | APK thực khớp build | SHA-256 khớp file đã build | Pass |
| App HTTP client | Emulator gọi được snapshot v2 bằng client thật | Probe qua `PeriodicPilotControl` đạt trên kho server riêng | Pass — HTTP local |
| Firebase trên app | Trạng thái phản ánh cấu hình hiện có | `FIREBASE_NOT_CONFIGURED`, file token debug chưa có | Blocker B1 |
| Bật PUSH khi thiếu token | Dừng trước khi đổi mode hoặc mở cửa sổ E02 | `PushPilotControl.prepare` thất bại đúng guard, chưa tạo setup. Snapshot sau đó vẫn mode PERIODIC | Pass — nhánh thiếu cấu hình |
| Payload sender | Data-only, normal, TTL 86400000 ms | CLI `--validate-only` đạt, payload đã loại token được lưu trong PREFLIGHT | Pass — kiểm input |
| Sender chưa cấu hình | Ghi local failure sau kiểm snapshot | Store commit version 1 thật. CLI trả `local_failure`, event `push_send_failed_local`, reason `INVALID_FCM_CONFIG`, attempt/message ID null | Pass — tái hiện blocker |
| Gửi FCM và callback thật | Có response/provider ID, receipt và cache evidence | Người dùng xác nhận chưa có Firebase. Credential/project/token chưa được cung cấp | Not run |
| E02, 5 lượt × 120 giây | Nhận và apply target trong background | 5 slot `PLANNED/NOT_RUN` trong E02_PLAN, run ID và build cho lần chạy thực để null | Not run |
| Notification | Đối chiếu trước/trong/sau E02 | Checkpoint preflight ghi 0 notification của app. Chưa có cửa sổ push để đánh giá | Not run — E02 |
| Cleanup preflight | Work/OS và kho server được trả về trạng thái an toàn | 0 active sync/periodic work, Home resumed, stopped=false, network connected, idle ACTIVE. Mode giữ PERIODIC, cache giữ 3 từ lượt cũ. Server riêng đã dừng, lock được giải phóng | Pass — preflight |
| Prepare/cleanup có token | Bật PUSH, chặn trigger khác, restore mode sau pilot | Nhánh có Firebase/token thật chưa thực hiện | Not run |

Các unit test chạy trên JVM với cấu hình `unitTests.isReturnDefaultValues` từ SEM-32. Kết quả này kiểm logic và khả năng build. Các phép đo thời gian callback và delivery thực tế cần pilot trên thiết bị.

## Artifact đã bàn giao

- [PREFLIGHT.json](PREFLIGHT.json) lưu build/checksum, trạng thái token đã lọc, số work và notification, kết quả test, payload validation, sender failure và hash capture private.
- [PushPilotControl.kt](../../../android/app/src/androidTest/java/com/thanhtris/seminarie307/experiments/PushPilotControl.kt) cung cấp `preflight`, `prepare`, `snapshot`, `cleanup` qua instrumentation. Bước prepare yêu cầu token READY, file token hiện diện, drain one-time work và tắt periodic trước khi ghi mode PUSH. Snapshot xuất đúng các cột Room legacy, status/token-file boolean và số work/notification. Raw token được giữ trong storage riêng của app.
- [REPRODUCE.md](REPRODUCE.md) ghi quy trình tiếp tục khi có cấu hình, 5 lượt 120 giây, cách đọc sender/callback/cache và cleanup.
- [Control cấu hình](../../../experiments/development/run-sem34-fcm-config-20261112/manifest.json) mang `case_id=CONTROL`, `run_phase=development`, `COMPLETED/FAILURE/INVALID`. Hai event server thực là `server_updated` và `push_send_failed_local`. Snapshot target của control là version 1 trên store riêng. Cache emulator trước/sau vẫn 3.

| Lượt E02 | Slot kế hoạch | Trạng thái |
|---|---|---|
| 1 | `planned-slot-sem34-e02-01` | NOT_RUN |
| 2 | `planned-slot-sem34-e02-02` | NOT_RUN |
| 3 | `planned-slot-sem34-e02-03` | NOT_RUN |
| 4 | `planned-slot-sem34-e02-04` | NOT_RUN |
| 5 | `planned-slot-sem34-e02-05` | NOT_RUN |

Danh sách nằm trong [E02_PLAN.json](../../../experiments/plans/SEM-34/E02_PLAN.json), ghi cửa sổ dự kiến 120 giây, normal/data-only/TTL theo protocol. Format kế hoạch có `data_kind=PLANNED`, `plan_version=1.0.0`, các slot có `run_id=null`, commit/APK cho lần chạy thực để null. Các ID cũ được giữ ở `previous_placeholder_id` để tra lịch sử. PREFLIGHT ngày 12/11 giữ bản ghi tên slot đã chọn lúc kiểm ban đầu.

## Blocker cần nhận tiếp

**B1 — Firebase thực tế.** Người dùng xác nhận chưa có cấu hình Firebase. Trên máy kiểm chưa thấy `android/app/google-services.json`, credential/token ở đường dẫn mẫu hoặc ADC mặc định, các biến `FIREBASE_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`, `FCM_TOKEN_FILE` chưa đặt. Phạm vi kiểm là các vị trí cấu hình chuẩn và môi trường tiến trình. Cần người quản lý project bàn giao config đúng package, credential gửi FCM và quyền project qua kênh riêng. Sau đó build lại với Google Services, lấy token của emulator và kiểm fingerprint theo PUSH.md.

**B2 — Producer log Android.** Timeline còn `legacy-room-v1`, thiếu các trường và fetch events của canonical schema 2.0.0. SEM-36 tiếp nhận phần chuẩn hóa producer. Lượt có callback thật cần lưu raw legacy đúng nhãn và kiểm nhận đường bàn giao trước khi đưa vào consumer v2.

**B3 — Thực nghiệm chưa chạy.** Chưa có bằng chứng accepted/received/applied, cache nền do push, delivery window hoặc notification trong E02. SEM-34 còn mở cho đến khi có lượt pilot thật và evidence tương ứng. Đây là đầu vào SEM-36 cần nhận tiếp.

## Kiểm artifact

Lần kiểm ngày 12/11 đã tái xuất control và 5 placeholder để đối chiếu byte. Sau review, 5 placeholder được thay bằng kế hoạch PLANNED ngoài thư mục runs. Control được chuyển sang development, giữ nguyên byte của manifest, events và report. Event control đúng source SERVER, không có FCM message/send attempt. Capture thô, database và mapping giữ trong `.local/sem34/` được gitignore. Trạng thái Project tiếp tục Todo trong lúc chờ B1 và pilot.

## Cập nhật theo review ngày 15/11/2026

Review của Trí ngày 12/11 xác nhận preflight và guard phù hợp, các lưu ý về kế hoạch không chặn merge. Nhánh đã nhận main tại `c77772e426c00ae464240f00942f8368c638aaa8`. [Review PR #26](https://github.com/ThanhTris/Seminar-IE307/pull/26#pullrequestreview-5867500531)

1. Thay 5 manifest OBSERVED chưa chạy bằng E02_PLAN với `data_kind=PLANNED`, slot ID thể hiện kế hoạch và `run_id=null`. Exporter SEM-24 hiện nhận OBSERVED/FIXTURE cho run manifest, nên format kế hoạch được đặt ở `experiments/plans/SEM-34/`.
2. Chuyển control đã quan sát sang `experiments/development/`, giữ nguyên log và hash. Auditor quét `experiments/runs/` giờ không thu control hoặc slot kế hoạch SEM-34.
3. Báo cáo audit mặc định vẫn ghi hai `MANIFEST_CONTRACT_INVALID` của SEM-29 legacy có từ trước. Kết quả được ghi trong review, thuộc đầu vào SEM-29 và consumer SEM-44/45.
4. Android pilot thật tiếp tục lưu raw legacy đúng nhãn cho đến khi có producer v2. Cấu hình Firebase và 5 lượt E02 thực tế còn chờ bàn giao.

Kiểm sau sửa có 36/36 tests exporter đạt, 5 slot PLANNED đúng trạng thái và 38 link nội bộ cùng 9 block shell hợp lệ. Byte control/PREFLIGHT khớp bản trước review. Auditor trả exit 2 với hai loại vấn đề hiện có `MANIFEST_CONTRACT_INVALID` từ hai run SEM-29 và `RESULTS_CSV_MISSING`. Sáu mục SEM-34 đã ra khỏi kết quả quét runs, mã `NON_MAIN_RUN_IN_RUNS_DIRECTORY` không còn xuất hiện trong lần kiểm này.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s experiments/scripts/tests -v
python3 experiments/scripts/audit_main_runs.py --output .local/sem34-review/AUDIT_RESULTS.md
git diff --check
```
