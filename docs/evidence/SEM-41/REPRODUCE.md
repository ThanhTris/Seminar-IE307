# SEM-41 — Chuẩn bị và chạy tập emulator

Đọc [task](../../../tasks/backlog/SEM-41.md), [protocol E01–E06](../../../experiments/PROTOCOL.md), [run schedule](../../../experiments/RUN_SCHEDULE.md) và [CHECKS](CHECKS.md). Phần này dành cho `emulator-main`; điện thoại do SEM-42 xử lý. Các slot nằm trong [EMULATOR_PLAN](../../../experiments/plans/SEM-41/EMULATOR_PLAN.json).

## Kiểm trước phiên

Nhận `release/CANDIDATE_MANIFEST.json`, `docs/evidence/SEM-37/CANDIDATE_GATE.md`, CHECKS và APK từ Trung. Đối chiếu full source commit, APK SHA-256, config và trạng thái gate. Tại lần kiểm 15/11, các file này chỉ có trên PR #28 ở trạng thái NOT_READY. Khi chỉ kiểm source chưa freeze, ghi development/pilot.

Ví dụ tái lập build đúng revision đã kiểm trên máy Vinh, từ root repo. Thư mục worktree phải chưa tồn tại.

```sh
git worktree add --detach /private/tmp/sem41-candidate-reproduce \
  9e7e55b76c646ff113a152022cc23317a202e533
cd /private/tmp/sem41-candidate-reproduce/android
ANDROID_HOME="$HOME/Library/Android/sdk" sh gradlew --no-daemon --max-workers=2 \
  :app:assembleDebug :app:assembleDebugAndroidTest :app:testDebugUnitTest
```

Revision trên còn 1/32 unit test fail. Với candidate mới, dùng commit được bàn giao và kiểm lại test/config, lấy APK hash của chính lần build đó. Build tạo APK chưa đồng nghĩa candidate gate đã qua.

Từ root source được nhận, kiểm hash và cài app/test APK. Serial lấy từ mapping private. Trước upgrade, lưu DB/capture cũ vào storage private, xác nhận work đã drain và slot thiết bị/server được khóa.

```sh
shasum -a 256 android/app/build/outputs/apk/debug/app-debug.apk
adb -s "$pilot_serial" install -r android/app/build/outputs/apk/debug/app-debug.apk
adb -s "$pilot_serial" install -r android/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
adb -s "$pilot_serial" shell am start -W -n com.thanhtris.seminarie307/.MainActivity
```

Cấu hình Run ID, Device alias và mode qua UI. Trên Android 17 cấp quyền mạng cục bộ qua dialog khi app yêu cầu. Chọn lại mode sau upgrade để periodic request có device alias theo version mới. Kiểm WorkInfo thực tế, network/idle/pin và package stopped. Probe HTTP server riêng, xác nhận token Firebase theo PUSH.md cho các ca push.

## Kiểm export development trước main

Lượt đã thực hiện ngày 15/11 dùng chế độ PUSH nhưng trigger MANUAL để kiểm shared core. Target store riêng được đưa lên 4, cache trước 3, manual apply lên 4. Giữ lượt này ở development. Khi tiếp tục, chọn target cao hơn cache, run ID mới và source đúng ca.

Sau khi core đã hoàn tất, xuất bằng action `export-v2` của test APK candidate. Chạy instrumentation ngoài cửa sổ đo.

```sh
adb -s "$pilot_serial" shell am instrument -w -r \
  -e class 'com.thanhtris.seminarie307.experiments.PeriodicPilotControl#control' \
  -e sem29_action export-v2 -e sem29_run_id "$run_id" \
  com.thanhtris.seminarie307.test/androidx.test.runner.AndroidJUnitRunner
adb -s "$pilot_serial" exec-out run-as com.thanhtris.seminarie307 \
  cat "files/sem29/$run_id/events-v2-export-report.json"
```

Capture `events-v2.jsonl` và `export-v2-events-legacy.jsonl` vào private. Report PARTIAL phải được đọc từng event omitted. Row cũ thiếu captured fields giữ trong raw legacy. `periodic_cancelled` hiện được report là unsupported. Chỉ đưa canonical event đã kiểm vào exporter SEM-24, giữ raw/report kèm evidence sau kiểm nhạy cảm.

## Ma trận tuần tự

| Nhóm | Số slot | Window mỗi slot | Tổng phút | Đầu vào riêng |
|---|---:|---:|---:|---|
| E01 PERIODIC | 1 | 90 phút | 90 | ≥3 cycle tự nhiên, cùng một phiên |
| E02 PUSH | 5 | 120 giây | 10 | Firebase/token, periodic đã tắt |
| E03 PERIODIC | 2 | 35 phút | 70 | 5 baseline + 20 confirmed Doze + 10 sau thoát |
| E03 PUSH | 2 | 35 phút | 70 | Doze và Firebase |
| E04 PERIODIC | 3 | 32 phút | 96 | 2 phút offline + 30 sau reconnect |
| E04 PUSH | 3 | 7 phút | 21 | 2 phút offline + 5 sau reconnect, TTL 24 giờ |
| E05 duplicate | 3 | 15 phút | 45 | Giữ signal ID khi gửi lặp |
| E05 stale hint | 3 | 15 phút | 45 | Hint cũ, target server mới hơn cache |
| E05 signal mới khi work chạy | 3 | 15 phút | 45 | Barrier/overlap, INJECTED |
| E06 HYBRID skip | 2 | 45 phút | 90 | SEM-40 skip thật, apply source PERIODIC |
| **Tổng emulator** | **27** | | **582** | Setup/cleanup/pilot/buffer bổ sung |

Khóa một emulator/app và một snapshot store cho từng run, gồm setup/window/export/cleanup. Sau mỗi lượt giữ đủ window dù applied sớm, ghi elapsed/end/UTC, giữ timeout/failure và event muộn. E01/E06 giữ lịch tự nhiên ổn định. E03 xác nhận idle bằng OS dump trước khi tính pha idle; E04 giữ đúng transport baseline khi khôi phục. E05 race bắt đầu khi đã có bằng chứng overlap theo protocol.

Khi candidate/pilot đã qua, điền manifest mới từ template với `run_phase=main`, `data_kind=OBSERVED`, commit/checksum/candidate gate thật. Copy slot kế hoạch thành run ID riêng của lần đo. `planned-slot` chỉ theo dõi lịch, mọi mốc và kết quả actual được ghi từ lần chạy.

## Đóng run và export

Lưu raw client/server và snapshot state trước reset. Đóng nhận trigger, cancel/drain đúng work, kiểm idle/network/pin/stopped và trả baseline. Khi drain chưa đạt, giữ thiết bị được khóa. Ghi cleanup theo evidence OS/WorkInfo. Các mapping reverse/rule chỉ được gỡ nếu do phiên tạo.

Khi có đủ canonical JSONL, chạy exporter từ root repo. Các đường dẫn `manifest_input`, `android_raw`, `server_raw`, `deny_file` phải được đặt từ run đã đo. Deny file chứa token/serial thật và nằm trong private.

```sh
python3 experiments/scripts/export_logs.py \
  --manifest "$manifest_input" --run-id "$run_id" --device-alias emulator-main \
  --android-log "$android_raw" --server-log "$server_raw" --deny-values "$deny_file"
```

Exporter ghi `experiments/runs/<run_id>/`, từ chối ghi đè. Consumer phân tích tập chính chọn phase main và chia theo build/config/device/case; raw development trong CHECKS này giữ đường dẫn development. Trước bàn giao SEM-43/44/45, rà link/hash, count, window và provenance của từng run, kèm mọi omission/timeout/Not run còn lại.
