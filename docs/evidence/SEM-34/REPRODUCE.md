# Tiếp tục pilot push SEM-34

Theo [task SEM-34](../../../tasks/backlog/SEM-34.md), [protocol E02](../../../experiments/PROTOCOL.md), [PUSH](../../PUSH.md) và [FCM sender](../../setup/FCM_SENDER.md). Lần kiểm ngày 12/11/2026 đang chờ Firebase, kết quả đã thực hiện nằm trong [CHECKS](CHECKS.md).

## 1. Nhận cấu hình và build

Nhận `android/app/google-services.json` đúng package `com.thanhtris.seminarie307`, project ID và credential local có quyền gửi FCM. File config được gitignore. Đặt biến môi trường theo đường dẫn private trên máy gửi. Lấy token theo PUSH.md sau khi cài và mở app, đối chiếu fingerprint với token file hiện hành.

```sh
cd android
ANDROID_HOME="$HOME/Library/Android/sdk" sh gradlew \
  :app:assembleDebug :app:assembleDebugAndroidTest :app:testDebugUnitTest
cd ..
adb -s "$pilot_serial" install -r android/app/build/outputs/apk/debug/app-debug.apk
adb -s "$pilot_serial" install -r android/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
adb -s "$pilot_serial" shell am start -W -n com.thanhtris.seminarie307/.MainActivity
```

Cấp quyền mạng cục bộ trên Android 17 qua hộp thoại app. Kiểm app đã lấy token. Copy token bằng redirect byte vào private file, dùng serial từ mapping private.

```sh
mkdir -p .local/secrets
adb -s "$pilot_serial" exec-out run-as com.thanhtris.seminarie307 \
  cat files/fcm/device-token.txt > .local/secrets/device-token.txt
chmod 600 .local/secrets/device-token.txt
```

Nếu token chưa READY hoặc file thiếu, dừng tại preflight và ghi blocker. APK có `google-services.json` sẽ có SHA-256 mới. Ghi commit/checksum/build mới cho các run thực hiện tiếp.

## 2. Preflight và cửa sổ E02

Chọn run ID mới cho từng lượt, khác các slot NOT_RUN đã lưu, định nghĩa `pilot_run`, `pilot_serial`, `update_id`, `signal_id`, `target_version` và đường dẫn private từ môi trường thực tế. Các biến cấu hình gửi phải trỏ tới project/credential/token đã được bàn giao.

```sh
adb -s "$pilot_serial" shell am instrument -w -r \
  -e class 'com.thanhtris.seminarie307.experiments.PushPilotControl#control' \
  -e sem34_action preflight -e sem34_run_id "$pilot_run" \
  com.thanhtris.seminarie307.test/androidx.test.runner.AndroidJUnitRunner
adb -s "$pilot_serial" exec-out run-as com.thanhtris.seminarie307 \
  cat "files/sem34/$pilot_run/preflight-state.json"
```

Preflight read-only ghi mode/cache, token status, boolean token file, số periodic/sync work và số notification hiện có của app. Harness nằm trong test APK. Các thao tác instrumentation được thực hiện ngoài cửa sổ E02 vì runner có thể thay trạng thái process.

Chạy server v2 trên kho riêng được khóa cho phiên, từ `server/` trong terminal riêng. Các đường dẫn cần được đặt tuyệt đối để terminal sender dùng đúng store.

```sh
cd server
npm ci --ignore-scripts
npm test
HOST=127.0.0.1 PORT=3000 STORE_DIR="$pilot_store" node dist/server.js
```

Đảm bảo cache trước lượt thấp hơn target server. Nếu dùng store mới có version thấp hơn cache cũ, tiếp tục tăng version qua update CLI hoặc nhận baseline được quản lý cho phiên. Ghi chính xác cache/server version. Sau khi các work cũ đã drain, chuẩn bị PUSH.

```sh
adb -s "$pilot_serial" shell am instrument -w -r \
  -e class 'com.thanhtris.seminarie307.experiments.PushPilotControl#control' \
  -e sem34_action prepare -e sem34_run_id "$pilot_run" \
  com.thanhtris.seminarie307.test/androidx.test.runner.AndroidJUnitRunner
adb -s "$pilot_serial" exec-out run-as com.thanhtris.seminarie307 \
  cat "files/sem34/$pilot_run/prepare-state.json"
adb -s "$pilot_serial" shell am start -W -n com.thanhtris.seminarie307/.MainActivity
adb -s "$pilot_serial" shell input keyevent KEYCODE_HOME
adb -s "$pilot_serial" shell dumpsys activity activities
adb -s "$pilot_serial" shell dumpsys package com.thanhtris.seminarie307
```

Prepare kiểm token READY và file token, chặn one-time work còn active, hủy periodic qua scheduler bàn giao và xác nhận 0 active work trước khi ghi mode PUSH. Nó lưu mode trước đó ở `files/sem34/<run>/setup.json`. Capture state phải ghi PUSH, periodic/sync work count bằng 0 trước send. Xác nhận Home resumed, stopped=false, mạng/pin/idle đúng baseline và ghi notification baseline. Dump thô giữ private.

Từ root, update target khi app ở Home, giữ response và event server. Cửa sổ **120 giây** bắt đầu ở `server_updated` target theo protocol. Sender kiểm đúng update/version/store trước khi gửi.

```sh
node server/bin/update-cli.js --update-id "$update_id" --run "$pilot_run" \
  --mode PUSH --device emulator-main --title 'SEM-34 E02 target' --body 'Background cache pilot'
node server/bin/fcm-sender.js --send --run "$pilot_run" --mode PUSH --device emulator-main \
  --update-id "$update_id" --signal-id "$signal_id" --version "$target_version" \
  --server-events "$pilot_store/events.jsonl" --events "$sender_events"
```

`target_version` lấy từ response thật. Sender sử dụng `FIREBASE_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`, `FCM_TOKEN_FILE` đã cấu hình. TTL mặc định 86400000 ms, data-only normal priority, baseline không collapse key. Khi accepted, giữ message ID thật. Rejected/unknown/local failure được lưu theo loại thực tế. Unknown cần kiểm bằng chứng trước khi quyết định retry.

Giữ app ở Home hết 120 giây, lấy mốc UTC/elapsed và evidence background. Snapshot/cache/timeline được kiểm qua capture private trước khi mở UI, dùng Room snapshot có WAL hoặc giao diện producer đã bàn giao. Đối chiếu `snapshot_applied` target với mốc end/user reopen và source PUSH. Giữ timeout, failure và event muộn. Kiểm notification trong cửa sổ bằng capture OS private cùng trạng thái app. Clock chưa hiệu chỉnh thì ghi `controlled=false` và giới hạn phép tính latency.

## 3. Kết thúc, xuất log và cleanup

Đóng cửa sổ trước, ghi end UTC/elapsed. Sau đó lấy snapshot bằng harness, lưu file vào private để lọc định danh trước bàn giao.

```sh
adb -s "$pilot_serial" shell am instrument -w -r \
  -e class 'com.thanhtris.seminarie307.experiments.PushPilotControl#control' \
  -e sem34_action snapshot -e sem34_run_id "$pilot_run" \
  com.thanhtris.seminarie307.test/androidx.test.runner.AndroidJUnitRunner
adb -s "$pilot_serial" exec-out run-as com.thanhtris.seminarie307 \
  cat "files/sem34/$pilot_run/snapshot-events-legacy.jsonl"
adb -s "$pilot_serial" exec-out run-as com.thanhtris.seminarie307 \
  cat "files/sem34/$pilot_run/snapshot-state.json"
```

Raw Android hiện có cột Room legacy. Ghi đúng `legacy-room-v1` nếu dùng file này, nhận chuẩn hóa producer qua SEM-36 trước consumer canonical v2. Server update và sender log dùng file riêng và có canonical v2. Log v2 đã được producer bàn giao có thể đưa vào exporter SEM-24 với deny values chứa token/serial thật.

Đợi hoặc xử lý work pending theo quy trình drain đã nhận, giữ thiết bị được khóa khi còn work có thể chạy. Cleanup chỉ restore mode khi không còn active sync work.

```sh
adb -s "$pilot_serial" shell am instrument -w -r \
  -e class 'com.thanhtris.seminarie307.experiments.PushPilotControl#control' \
  -e sem34_action cleanup -e sem34_run_id "$pilot_run" \
  com.thanhtris.seminarie307.test/androidx.test.runner.AndroidJUnitRunner
adb -s "$pilot_serial" exec-out run-as com.thanhtris.seminarie307 \
  cat "files/sem34/$pilot_run/cleanup-state.json"
adb -s "$pilot_serial" shell am start -W -n com.thanhtris.seminarie307/.MainActivity
adb -s "$pilot_serial" shell input keyevent KEYCODE_HOME
```

Kiểm lại stopped, mode, work, mạng/idle/pin và notification. Nếu trước phiên có lịch periodic được phép khôi phục, đăng ký lại theo bàn giao của scheduler sau khi đã giải phóng slot E02. Dừng server do phiên tạo sau khi lưu state/outbox và sender log. Giữ target/version đơn điệu khi tiếp tục trên cùng store.

Lặp lại với **5 run ID riêng**, mỗi lượt đủ 120 giây. Ghi manifest, events, report và CHECKS theo kết quả thật cho từng lượt. Bộ NOT_RUN ngày 12/11 giữ lịch sử cấu hình thiếu, các lượt tiếp theo có ID/build/config của lần thực hiện mới.
