# SEM-35 — CLI FCM data-only

CLI phát tín hiệu từ snapshot đã commit, dùng Firebase Admin Node **14.5.0**, AndroidConfig v1 `normal`, không có notification. `send()` thành công chỉ là FCM đã nhận để chuyển tiếp, không chứng minh Android nhận hoặc đồng bộ. [Tài liệu Admin SDK](https://firebase.google.com/docs/reference/admin/node/firebase-admin.messaging.messaging) và [AndroidConfig](https://firebase.google.com/docs/reference/admin/node/firebase-admin.messaging.androidconfig) xác nhận TTL của Admin SDK tính bằng milliseconds.

## Điều kiện

- Node.js 22+, `cd server && npm ci && npm run build`; `npm test` còn cần Python 3.10+ để đối chiếu validator SEM-24. Server SEM-27 chạy và đã commit update cùng `run_id`, `mode`, `device_alias`, `update_id`, `version` muốn báo; đường `--server-events` phải trỏ đúng file JSONL export của chính store server đó.

- Firebase project và app Android phải được người quản lý xác nhận; máy gửi có quyền FCM HTTP v1, credential ADC/service-account local hợp lệ, thiết bị lấy được registration token thật. Theo [SEM-13](../environment/SERVER_FIREBASE.md) các điều kiện này chưa xác nhận; không tạo project, credential hay token giả làm kết quả thật.
- Để ngoài Git: `GOOGLE_APPLICATION_CREDENTIALS` là đường dẫn credential local; `FIREBASE_PROJECT_ID` là project thật; `FCM_TOKEN_FILE` là đường dẫn file chỉ chứa token test. Không đưa token vào argument, log, manifest hoặc chat. Ví dụ đường dẫn phía dưới là placeholder, không phải cấu hình đang có.

Test ưu tiên executable trong biến `PYTHON`; khi không đặt, dùng `python` trên Windows và `python3` trên macOS/Linux. Nếu máy chỉ có Python Launcher, đặt `PYTHON=py`; nếu cần chọn bản cụ thể, đặt đường dẫn executable Python 3.10+ (không kèm tham số). Ví dụ PowerShell: `$env:PYTHON = 'C:\Python312\python.exe'`, sau đó chạy `npm test`.

```sh
export STORE_DIR="$PWD/../.local/sem35-store"
export SERVER_URL="http://127.0.0.1:3000"
export FIREBASE_PROJECT_ID="<project-id-that>"
export GOOGLE_APPLICATION_CREDENTIALS="$PWD/../.local/secrets/fcm-service-account.json"
export FCM_TOKEN_FILE="$PWD/../.local/secrets/device-token.txt"
```

Dùng cùng `STORE_DIR` khi khởi động `npm start` ở terminal server. Cấu hình ví dụ không tự nạp `.env` và không chứa credential. `FCM_TOKEN_FILE` có thể thay bằng `--token-file <đường-dẫn-local>`; không truyền nội dung token qua `--token`.

## Tạo snapshot, kiểm payload và gửi

Từ `server/` khi server đang chạy, tạo update (chọn các ID riêng cho run thật):

```sh
npm run update -- --update-id update-e02-01 --run run-e02-01 --mode PUSH --device emulator-01 --title 'Thông báo thử' --body 'Bản tin thử nghiệm'
```

Đọc `version` thực từ response update. Ví dụ dưới giả định response trả `version=1`; thay `1` bằng giá trị thực, không tự suy. Tạo và giữ `signal-id` ổn định cho cùng tín hiệu nếu retry; mỗi lần gọi SDK có một `send_attempt_id` mới.

```sh
npm run send-push -- --validate-only --run run-e02-01 --mode PUSH --device emulator-01 --update-id update-e02-01 --signal-id signal-e02-01 --version 1
npm run send-push -- --send --run run-e02-01 --mode PUSH --device emulator-01 --update-id update-e02-01 --signal-id signal-e02-01 --version 1 --server-events "$STORE_DIR/events.jsonl" --events ../.local/sem35-sender/events.jsonl
```

`--validate-only` chỉ kiểm input và in cấu trúc không chứa token; không gọi SDK, không ghi event, không chứng minh quyền Firebase. `--send` kiểm snapshot server và event `server_updated` khớp run/mode/device/update/version trước khi lấy credential và gọi SDK. Nếu store hoặc event chưa sẵn sàng, xử lý nguyên nhân và chạy lại; không phát push cho update chưa xác nhận. Hai nguồn kiểm phải trỏ về cùng server/store: CLI không xác thực mật mã mối liên hệ này.

TTL mặc định là **86400000 ms (24 giờ)** theo [protocol](../../experiments/PROTOCOL.md); chỉ thay bằng `--ttl-ms` khi protocol run cho phép và ghi TTL thực vào manifest. Giá trị hợp lệ 0–2419200000 ms. Signal data gồm `run_id`, `mode`, `source=PUSH`, `version_hint` và `signal_id`; không có notification, `AndroidConfigV2` hay token trong data.

## Kết quả và log

- SDK trả ID thật: event `push_send_accepted` lưu nguyên `message_id`; chưa xác nhận thiết bị đã nhận.
- Thiếu cấu hình hoặc không chứng minh được commit: `push_send_failed_local`, không có attempt/message ID. Hai lỗi SDK token hết đăng ký hoặc sai sender được phân loại `push_send_rejected`; lỗi SDK/network khác được ghi `push_send_unknown` vì không đủ cơ sở khẳng định FCM đã từ chối. Không ghi exception thô, HTTP body hay credential. `http_status` để null khi SDK không cung cấp bằng chứng tin cậy.
- Với unknown, không tự retry: xem event và bằng chứng callback, sau đó nếu cần thử lại giữ `signal_id`, dùng attempt mới, tôn trọng rate limit và [hướng dẫn backoff FCM](https://firebase.google.com/docs/cloud-messaging/error-codes). Một lần gọi SDK được ghi một attempt; SDK có thể tự retry bên trong nên attempt không tương đương từng HTTP request.
- Sender append JSONL riêng, mặc định `server/.local/fcm-sender/events.jsonl`; không dùng chung đường dẫn `STORE_DIR/events.jsonl` vì SEM-27 có thể tái xuất file đó. Để export một run, tập hợp **bản sao ổn định** của hai nguồn vào `experiments/private/<run_id>/server.jsonl`, sau đó dùng [SEM-24 exporter](../../experiments/README.md); không sửa hay ghi đè state server. File sender nên có một process ghi tại một thời điểm.
- Nếu lỗi ghi log sau khi gọi SDK, CLI trả lỗi và không tự gửi lại; kiểm tra bằng chứng trước khi retry. Process chết sau phản hồi FCM nhưng trước khi ghi event có thể làm mất event, không được kết luận không gửi; sender chưa có journal khôi phục trạng thái đó.

SEM-35 chưa xác minh FCM thật hoặc callback trên Android. Khi đã có quyền và thiết bị, chạy send thật trên máy được cấp quyền, lưu event riêng và đối chiếu callback theo `run_id`, `device_alias`, `signal_id`; không gửi credential hay token vào repo/chat. Cập nhật CHECKS bằng kết quả thật hoặc blocker còn lại.
