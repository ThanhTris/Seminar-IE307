# Tái lập pilot periodic SEM-29

Người thực hiện Vinh (`Vinh5905`). Đọc [task SEM-29](../../../tasks/backlog/SEM-29.md), [protocol E01](../../../experiments/PROTOCOL.md), [PERIODIC](../../PERIODIC.md) và [CHECKS](CHECKS.md) trước khi nhận thiết bị và kho snapshot riêng.

## Build và bộ điều khiển pilot

`PeriodicPilotControl` thuộc `androidTest`, gọi trực tiếp `PeriodicSyncScheduler` và WorkManager thật. APK ứng dụng dùng source trên main. Test APK chỉ thực hiện thao tác setup, snapshot và cleanup khi được truyền action rõ ràng. Lưu SHA-256 của cả hai APK cùng commit source.

```sh
cd android
ANDROID_HOME="$HOME/Library/Android/sdk" sh gradlew \
  :app:assembleDebug :app:assembleDebugAndroidTest :app:testDebugUnitTest
cd ..
```

Cài APK ứng dụng và test APK trên emulator đã bàn giao. Dùng serial trong mapping private, chọn run ID mới cho mỗi lần thử. Các biến dưới đây phải được đặt từ mapping và lượt chạy thực tế.

```sh
adb -s "$pilot_serial" install -r android/app/build/outputs/apk/debug/app-debug.apk
adb -s "$pilot_serial" install -r android/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
adb -s "$pilot_serial" shell am start -W -n com.thanhtris.seminarie307/.MainActivity
```

Trên Android 17/API 37, cấp quyền mạng cục bộ qua hộp thoại Nearby devices của ứng dụng. Khai báo `ACCESS_LOCAL_NETWORK` và yêu cầu quyền nằm trong entrypoint MainActivity. Khi từ chối, ứng dụng hiển thị hướng dẫn cấp quyền trong Settings. Kiểm lại quyền trước khi chạy worker vì kết nối TCP đến server LAN có thể timeout khi quyền bị chặn. [Nguồn Android](https://developer.android.com/privacy-and-security/local-network-permission)

Sau khi server v2 đã sẵn sàng, chạy probe bằng chính HTTP client của app. Probe phải đạt trước khi mở cửa sổ pilot.

```sh
adb -s "$pilot_serial" shell am instrument -w -r \
  -e class 'com.thanhtris.seminarie307.experiments.PeriodicPilotControl#control' \
  -e sem29_action probe -e sem29_run_id "$probe_run" \
  com.thanhtris.seminarie307.test/androidx.test.runner.AndroidJUnitRunner

adb -s "$pilot_serial" shell am instrument -w -r \
  -e class 'com.thanhtris.seminarie307.experiments.PeriodicPilotControl#control' \
  -e sem29_action diagnose -e sem29_run_id "$diagnostic_run" \
  com.thanhtris.seminarie307.test/androidx.test.runner.AndroidJUnitRunner
```

Action `diagnose` yêu cầu chưa có periodic work active, đăng ký hai lần và kiểm một WorkManager ID active, sau đó hủy và kiểm không còn lịch active. Giữ dữ liệu lượt chẩn đoán bằng run ID riêng. Kiểm mạng/idle/pin, package stopped và công việc còn lại trước khi chuyển sang pilot.

## Phiên E01

Khởi chạy server v2 trên cổng 3000 với `STORE_DIR` riêng, nhận version baseline và kiểm đường emulator đến server. Ghi commit/config/build, OS/thiết bị và clock trước phiên.

```sh
cd server
npm ci --ignore-scripts
npm test
PORT=3000 HOST=127.0.0.1 STORE_DIR=../.local/sem29-server-reproduce node dist/server.js
```

Giữ terminal server và dùng terminal khác từ root để chạy CLI cập nhật baseline. Chọn ID mới, giữ update ID khi retry cùng thao tác.

```sh
node server/bin/update-cli.js --update-id "$baseline_update" \
  --run "$diagnostic_run" --mode PERIODIC --device emulator-main \
  --title 'SEM-29 baseline' --body 'Baseline before periodic pilot'
```

```sh
adb -s "$pilot_serial" shell am instrument -w -r \
  -e class 'com.thanhtris.seminarie307.experiments.PeriodicPilotControl#control' \
  -e sem29_action register -e sem29_run_id "$pilot_run" \
  com.thanhtris.seminarie307.test/androidx.test.runner.AndroidJUnitRunner
adb -s "$pilot_serial" shell am start -W -n com.thanhtris.seminarie307/.MainActivity
adb -s "$pilot_serial" shell input keyevent KEYCODE_HOME
adb -s "$pilot_serial" shell dumpsys activity activities
adb -s "$pilot_serial" shell dumpsys package com.thanhtris.seminarie307
adb -s "$pilot_serial" shell cat /proc/uptime
```

Xác nhận Home resumed và `stopped=false`, lưu mốc UTC/elapsed bắt đầu. Ngay sau đó cập nhật target bằng CLI với `--update-id`, `--run`, `--mode PERIODIC`, `--device`, `--title`, `--body` đúng API. Lưu response và event `server_updated` từ kho riêng.

```sh
node server/bin/update-cli.js --update-id "$target_update" \
  --run "$pilot_run" --mode PERIODIC --device emulator-main \
  --title 'SEM-29 periodic pilot target' --body 'Target for background periodic observation'
```

Giữ phiên đủ **5400 giây** theo E01. Mục tiêu SEM-29 là ít nhất hai lần `work_started` tự nhiên trong cửa sổ background. Chu kỳ trước mốc Home thuộc setup. Giữ lịch đăng ký ổn định, nguồn mạng/pin và ghi các dump đọc trạng thái ở đầu, giữa, cuối phiên. Lưu mọi timeout, failure và event muộn cùng run gốc. Clock chưa được kiểm soát phải ghi `controlled=false` và giữ giới hạn phép tính latency.

## Snapshot và cleanup

Đóng cửa sổ, lưu end UTC/elapsed rồi mới chạy instrumentation snapshot và cancel. Instrumentation có thể khởi động/kết thúc process của ứng dụng nên chỉ dùng ngoài cửa sổ đo.

```sh
adb -s "$pilot_serial" shell am instrument -w -r \
  -e class 'com.thanhtris.seminarie307.experiments.PeriodicPilotControl#control' \
  -e sem29_action snapshot -e sem29_run_id "$pilot_run" \
  com.thanhtris.seminarie307.test/androidx.test.runner.AndroidJUnitRunner
adb -s "$pilot_serial" exec-out run-as com.thanhtris.seminarie307 \
  cat "files/sem29/$pilot_run/snapshot-events-legacy.jsonl"
adb -s "$pilot_serial" exec-out run-as com.thanhtris.seminarie307 \
  cat "files/sem29/$pilot_run/snapshot-state.json"

adb -s "$pilot_serial" shell am instrument -w -r \
  -e class 'com.thanhtris.seminarie307.experiments.PeriodicPilotControl#control' \
  -e sem29_action cancel -e sem29_run_id "$pilot_run" \
  com.thanhtris.seminarie307.test/androidx.test.runner.AndroidJUnitRunner
```

Lưu output private trước, kiểm token/serial và các giá trị nhạy cảm trước khi bàn giao. Snapshot giữ đúng tên cột, giá trị và null của Room, lọc theo run ID. State chỉ lấy cache version, mode và WorkInfo, tách khỏi metadata FCM token. Giữ event sau cửa sổ và event cancel riêng để đánh giá cleanup.

Mở ứng dụng rồi Home sau cleanup, kiểm package stopped đã được xóa, WorkInfo không active và trạng thái mạng/idle/pin đã trở về baseline. Dừng server do phiên tạo sau khi lưu outbox. Giữ thiết bị bị khóa khi cleanup chưa đạt.

## Định dạng bàn giao

Android hiện có format `legacy-room-v1`. Exporter SEM-24 yêu cầu canonical `2.0.0` với các trường đo bổ sung. File legacy cần manifest khai báo đúng format và CHECKS ghi phần producer còn thiếu. Server v2 xuất JSONL riêng. Bàn giao producer cho SEM-25/36 để hoàn thiện logging trước tập chính và parser v2.

Script kiểm pilot đọc dữ liệu đã bàn giao và tái tính riêng setup, retry phục hồi và chu kỳ periodic mới từ request ID cùng elapsed time.

```sh
python3 docs/evidence/SEM-29/validate_pilot.py \
  experiments/runs/run-sem29-periodic-emulator-20261107-r2
```
