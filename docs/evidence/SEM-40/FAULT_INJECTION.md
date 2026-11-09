# SEM-40 — Cố ý bỏ gửi push cho E06

## Mục đích và hành vi

`update-cli --skip-push` cập nhật snapshot qua API SEM-27, sau response xác nhận commit mới ghi `push_send_skipped` với `reason=FAULT_INJECTION_SKIP`. Flag chỉ chấp nhận mode **HYBRID**, phục vụ E06. HTTP request vẫn đúng contract 2.0.0; flag và đường dẫn log không gửi vào JSON body.

POST của SEM-27 vốn không tự gửi FCM; cờ này đánh dấu rõ hành động bỏ gửi có chủ ý để phân tích run. Luồng skip không import hoặc gọi Firebase/sender, không cần credential/token. Nó không chặn một người hoặc process khác chủ động gọi sender cho cùng update: người chạy phải dừng các luồng gửi tự động, drain tín hiệu cũ và không gửi thủ công trong cửa sổ E06.

Đây là **fault injection do nhóm chủ động tạo**, không phải bằng chứng FCM làm mất tin, từ chối hay trì hoãn một tin đã gửi. Không tạo `message_id`, `send_attempt_id`, `signal_id` hoặc event accepted cho lần bỏ gửi.

## Lệnh bàn giao

Từ `server/`, dùng Node 22+; Python 3.10+ cần cho `npm test`/validator:

```sh
npm ci
npm run build
```

Terminal server:

```sh
STORE_DIR=../.local/sem40-store npm start
```

Terminal CLI đặt cùng store để bảo vệ đường dẫn log. Các ID dưới là ví dụ, phải chọn run thực và cấu hình app tương ứng trước khi đo:

```sh
STORE_DIR=../.local/sem40-store npm run update -- --base-url http://127.0.0.1:3000 --update-id update-e06-01 --run run-e06-01 --mode HYBRID --device emulator-01 --title 'E06 thử bỏ gửi' --body 'Nội dung thử nghiệm' --skip-push --events ../experiments/private/run-e06-01/fault-injection.jsonl
```

Trong PowerShell, đặt `$env:STORE_DIR = '../.local/sem40-store'` trước khi chạy lệnh `npm start` hoặc `npm run update ...` ở mỗi terminal; không dùng cú pháp gán biến inline của shell POSIX.

CLI trả `version` thật, `replayed`, `fault_injection=true`, `push=skipped`, `reason`, `event_id` và `commit_timestamp_utc`. Không tự điền version dự kiến. Mặc định log nằm ở `server/.local/fault-injection/events.jsonl` nếu không truyền `--events`; file riêng cho từng run giúp thu thập và kiểm lại dễ hơn.

## Thu thập bằng chứng

Giữ các nguồn riêng trong lúc producer còn chạy:

1. `STORE_DIR/events.jsonl` và state của SEM-27 xác nhận `server_updated`, update ID và version đã commit.
2. File `--events` xác nhận `push_send_skipped`, cùng `run_id`, `update_id`, `device_alias`, `mode=HYBRID`, `data_version`.
3. Log Android xác nhận nguồn worker thực sự áp dụng snapshot; không có applied thì giữ timeout/chưa quan sát được theo protocol.

Event skip dùng schema 2.0.0, `origin=SERVER`, `source=PUSH`, `outcome=skipped`, `reason=FAULT_INJECTION_SKIP`; message/attempt/TTL/hint để null, `signal_ids=[]`. `timestamp_utc` là lúc ghi nhận bỏ gửi sau response; cửa sổ E06 phải tính từ commit update (`server_updated.timestamp_utc` hoặc `commit_timestamp_utc`), không tính từ một lần retry muộn.

Sau khi thu bản sao ổn định của log, hợp nhất các nguồn SERVER cần dùng vào file private cho [SEM-24 exporter](../../../experiments/README.md); giữ nguyên event ID để deduplicate. Không dùng file skip làm `STORE_DIR/events.jsonl` hoặc `state.json`: CLI từ chối các đường này theo `STORE_DIR` đang cấu hình. Đối chiếu log sender khác nếu có để chắc cùng update không bị gửi bởi tác vụ khác.

## Retry và lỗi

- Timeout/5xx hoặc chưa ghi được skip: kết quả update có thể đã commit. Retry cùng toàn bộ payload và **cùng update_id** qua API; ledger SEM-27 trả version gốc, không tăng thêm. Không tự sửa store trực tiếp.
- Cùng update/run/device đã có skip cùng version/mode trong file log: giữ event ID/timestamp cũ, không append thêm event. Nếu file log bị mất thì retry có thể ghi event mới; cần giữ bản sao và deduplicate theo provenance khi ghép evidence, không tuyên bố một event mới là một update mới.
- Server trả 4xx/response sai: không ghi skip như thể đã xác nhận commit. CLI lỗi có exit code khác 0.
- Log không mở được, bị lock hoặc JSONL hỏng: từ chối trước khi gọi POST. Log hỏng không được âm thầm xóa; giữ bản sao và kiểm tra trước khi phục hồi/retry.
- File lock `<events>.lock` chỉ cho một CLI ghi cùng file tại một thời điểm. Sau crash, xác minh PID trong lock đã dừng rồi gỡ đúng lock cũ; giữ nguyên log/state. Nếu crash sau POST trước ghi event, retry cùng update ID để hoàn tất ghi nhận. Đây không phải giao dịch nguyên tử giữa server và file CLI, chưa kiểm mất điện vật lý.

## Quy trình E06 dành cho người chạy thực nghiệm

Theo [protocol SEM-16](../../../experiments/PROTOCOL.md#e06--hybrid-bỏ-gửi-push-có-kiểm-soát-emulator):

1. Chốt build/config/run, app ở HYBRID với periodic thật; drain push cũ. Ghi version cache và trạng thái thiết bị.
2. Dùng lệnh skip cho target version mới; giữ response và hai event server/skip. Không gọi sender cho update này.
3. Quan sát **45 phút từ commit**, không force-run hoặc đăng ký lại periodic để tạo thành công giả.
4. Chỉ quy cập nhật cho periodic nếu log liên kết được run, source, request/work và version target. Giữ failure/timeout và các can thiệp; không suy nguồn chỉ từ việc UI đổi.
5. Thực hiện **2 lượt**, ID riêng cho mỗi lượt; kết thúc và cleanup theo protocol. Ghi E06 Not run nếu chưa có log đo thật.

SEM-40 bàn giao công cụ và kiểm thử local. Chưa chạy E06/Android, không xác nhận hybrid đã phục hồi được cập nhật trên thiết bị.
