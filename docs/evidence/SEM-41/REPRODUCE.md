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

## Pilot tự động khi chưa có Firebase

[Runner](../../../experiments/scripts/run_sem41_periodic_pilots.py) thực hiện tuần tự E01×1, E03 PERIODIC×2, E04 PERIODIC×3 và E06×2. Tổng cửa sổ là 346 phút; cộng thêm setup/cleanup và thời gian của các lần thử bị dừng/lượt thay thế nếu có. Runner chỉ tạo phase pilot, đối chiếu hash APK đã cài với PREFLIGHT, cấu hình run/alias/mode qua UI và ghi checkpoint OS mỗi 5 phút. Không force-run job. Cửa sổ vẫn được giữ dù target đã applied sớm.

Chuẩn bị `device-map.json` và `deny-values.json` private có alias/serial và các giá trị nhạy cảm thật. Port 3000 phải trống; app/test APK phải đúng revision đã kiểm, baseline mạng hoạt động, airplane off và deep idle ACTIVE. Dành riêng emulator trong suốt batch, giữ máy mở, không thao tác app. Output phải là thư mục mới. Ví dụ trên macOS, từ root repo:

```sh
caffeinate -i python3 experiments/scripts/run_sem41_periodic_pilots.py \
  --adb "$HOME/Library/Android/sdk/platform-tools/adb" \
  --device-map .local/sem41/device-map.json \
  --private-output .local/sem41/pilots-new-batch
```

Theo dõi `status.json`, `heartbeat.json` và `observation.json` trong private output. Nếu không chứng minh được guest offline, runner giữ lượt E04 aborted, khôi phục mạng, ghi blocker và bỏ qua những lượt E04 còn lại. Lỗi khác dừng batch sau cleanup. Giữ cả lần setup sai hoặc bị gián đoạn và dùng run ID mới khi thử lại. Trên Android 17 dùng `cmd wifi set-wifi-enabled`, `cmd phone data`, `cmd connectivity airplane-mode`; không dựa vào lệnh `svc` không có trên image này.

Runner hiện tự ghi `runner-identity.json` ở batch root với full observer commit và SHA-256 source tại lúc khởi động, phase pilot và candidate gate false. Source runner phải được commit. Runner kiểm hash cả app/test APK, đối chiếu source server với commit ghim rồi build server trước setup. Trong batch giữ nguyên code/app/server, dùng private output mới. E04 tự lưu `offline-proof.json`; restore-idle chờ ACTIVE tối đa 10 giây và giữ các mẫu trong `*-transition.json`.

Sau khi một batch lỗi đã cleanup đạt, có thể chọn những lượt còn lại bằng `--runs E03:2 E04:1 E04:2 E04:3 E06:1 E06:2` trên lệnh khởi động mới. Mỗi lượt vẫn có run ID mới và đủ toàn bộ window. Giữ run lỗi dưới INVALID và ghi quan hệ thay thế; không nối phần thời gian còn thiếu vào run cũ.

Sau mỗi lượt FINISHED, [review/export helper](../../../experiments/scripts/export_sem41_pilots.py) đối chiếu raw/canonical/omitted IDs, window, source, work/fetch provenance, checkpoint và cleanup; tái xuất hai lần để so từng byte của ba file canonical. Helper chỉ hỗ trợ build/config trong control SEM-41 đã kiểm và từ chối run còn chạy. Ví dụ:

```sh
python3 experiments/scripts/export_sem41_pilots.py \
  --run-folder .local/sem41/pilots-new-batch/run-id-da-hoan-tat \
  --deny-values .local/sem41/deny-values.json
```

Artifacts pilot nằm trong `experiments/pilots/<run_id>/`, riêng với tập main. Đọc `audit.json` và mọi reason code trước dùng kết quả. Manifest có boot alias của collector, dẫn xuất từ hash kernel boot ID trong baseline private; observer kiểm cùng boot tại từng checkpoint. Nhờ đó duration giữa hai mốc `/proc/uptime` của collector có cùng boot đã xác minh. Helper không bổ sung boot session ID vào event: các event vẫn giữ null, không tính event latency từ các trường đó. Clock controlled=false giữ nguyên, không tính latency liên máy. E03 force-idle và E06 deliberate skip mang nhãn INJECTED. Thời gian idle là điều kiện điều khiển, không đại diện Doze tự nhiên.

## Đóng run và export

Lưu raw client/server và snapshot state trước reset. Đóng nhận trigger, cancel/drain đúng work, kiểm idle/network/pin/stopped và trả baseline. Khi drain chưa đạt, giữ thiết bị được khóa. Ghi cleanup theo evidence OS/WorkInfo. Các mapping reverse/rule chỉ được gỡ nếu do phiên tạo.

Khi có đủ canonical JSONL, chạy exporter từ root repo. Các đường dẫn `manifest_input`, `android_raw`, `server_raw`, `deny_file` phải được đặt từ run đã đo. Deny file chứa token/serial thật và nằm trong private.

```sh
python3 experiments/scripts/export_logs.py \
  --manifest "$manifest_input" --run-id "$run_id" --device-alias emulator-main \
  --android-log "$android_raw" --server-log "$server_raw" --deny-values "$deny_file"
```

Exporter ghi `experiments/runs/<run_id>/`, từ chối ghi đè. Consumer phân tích tập chính chọn phase main và chia theo build/config/device/case; raw development trong CHECKS này giữ đường dẫn development. Trước bàn giao SEM-43/44/45, rà link/hash, count, window và provenance của từng run, kèm mọi omission/timeout/Not run còn lại.
