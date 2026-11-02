# Event schema và correlation — SEM-26

**Schema `2.0.0` — bản bàn giao chờ review, 02/11/2026.** Đây là contract log cho SEM-24/25/27/35/45, không phải bằng chứng có run thật. Bản nháp `1.0.0` đã có trên main; delta không tương thích ở cuối tài liệu. API snapshot ở [API.md](API.md); bất biến của core ở [SHARED_SYNC](mechanisms/SHARED_SYNC.md); giải thích FCM ở [SERVER_FCM](mechanisms/SERVER_FCM.md). Các run theo [protocol](EXPERIMENT_PROTOCOL.md).

## Định dạng và quy tắc chung

- Một event là một JSON object trên **một dòng UTF-8 JSONL**, không có dòng trống; các file `events.jsonl` được export cùng manifest của run. Mỗi dòng phải có **tất cả các key** trong bảng dưới, kể cả key có giá trị `null` hoặc `[]`; không dùng `-1`, `"null"` hay ID giả làm giá trị chưa biết. JSON object không được có duplicate key.
- Event log là bằng chứng quan sát: chỉ ghi event khi sự kiện thực sự xảy ra; `event_id` duy nhất cho từng event, không tạo lại event khi replay update. Thứ tự các dòng giữa các nguồn không phải thứ tự nhân quả; khi merge giữ nguyên timestamp từng nguồn và deduplicate theo `event_id`.
- `schema_version` theo semver. Consumer hỗ trợ major `2` có thể bỏ qua trường mới từ minor version lớn hơn, nhưng phải giữ bản gốc an toàn và gắn cờ event type/outcome không nhận diện; không tự gán ý nghĩa hoặc gộp vào thống kê. Major không hỗ trợ: từ chối phân tích và báo version. Mọi thay đổi sau bàn giao ghi delta tại đây và [API.md](API.md).
- Runtime export không chứa registration token, credential, service-account key, serial, địa chỉ IP cá nhân, nội dung HTTP/FCM thô hoặc exception/stack trace. `reason`/`provider_code` chỉ là mã an toàn. Log gốc nhạy cảm giữ local theo protocol; che định danh không đổi timestamp/version/outcome đo được.
- Experiment event chỉ được ghi khi xác định được run/mode/device alias hợp lệ. Input lỗi hoặc callback không xác định được run/config: từ chối trigger và ghi **diagnostic local ngoài tập experiment**, không gán vào run đang active, không tạo event có run giả. Không coi diagnostic này là run hợp lệ khi phân tích.

Các ID ứng dụng (`run_id`, `device_alias`, `request_id`, `update_id`, `signal_ids` và `send_attempt_id`) theo regex trong [API.md](API.md). `event_id`, `work_id`, `network_call_id` là UUID string; `event_id` tạo UUID v4 mới cho mỗi event, `work_id` dùng nguyên UUID WorkManager, `network_call_id` tạo UUID v4 mỗi lần GET thực tế. `message_id` do FCM cung cấp là chuỗi opaque 1–512 ký tự hoặc null, không tự tạo hay giả định hai phía có cùng biểu diễn. Các giá trị số là JSON integer, không vượt `2^53-1`.

## Các trường bắt buộc trong mỗi event

| Key | Kiểu / miền giá trị | Ý nghĩa và nullability |
|---|---|---|
| `schema_version` | string, `"2.0.0"` | Phiên bản schema của dòng này. |
| `event_id` | UUID string | ID của event, duy nhất xuyên nguồn trong run. |
| `event_type` | string enum | Tên trong bảng event bên dưới, chữ thường `snake_case`. |
| `origin` | `SERVER` / `ANDROID` | Nơi thực sự ghi event; khác với source kích hoạt sync. |
| `run_id` | ID string | Run hợp lệ được capture, không thay bằng run active khác. |
| `mode` | `PERIODIC` / `PUSH` / `HYBRID` | Mode chụp tại run; không đổi tên event cũ khi đổi mode. |
| `source` | `MANUAL` / `PERIODIC` / `PUSH` / null | Trigger sync; null cho `server_updated`, `PUSH` cho event gửi/nhận push. MANUAL được phép ở cả ba mode và loại khỏi thống kê sync nền. |
| `device_alias` | ID string | Alias thiết bị test; server dùng alias của run/mục tiêu, không dùng token/serial. |
| `timestamp_utc` | RFC 3339 UTC string kết thúc `Z` | Đồng hồ tường lúc xảy ra event; có thể có phần giây. |
| `elapsed_realtime_ms` | integer >= 0 / null | Android: `SystemClock.elapsedRealtime()` tại event, bao gồm deep sleep; server: null. |
| `boot_session_id` | ID string / null | Alias ngẫu nhiên phân biệt lần boot trên **một thiết bị**; server null. Nếu không xác định chắc cùng boot, Android ghi null và không tính duration monotonic qua các event đó. |
| `data_version` | integer >= 0 / null | Version đối tượng mà event thực sự xác nhận; không biết thì null. Ý nghĩa từng event ở bảng dưới. Không thay bằng hint. |
| `cached_version` | integer >= 0 / null | Version cache thực tế tại thời điểm event khi biết; sau commit dùng version mới. Server hoặc cache chưa tồn tại: null. |
| `version_hint` | integer >= 0 / null | Hint của push; không tự xác nhận dữ liệu đã lấy/applied. |
| `request_id` | ID string / null | ID một logical sync của Android; tạo lúc enqueue hoặc mỗi chu kỳ periodic, giữ qua retry. Trước khi tạo và ở server: null nếu chưa biết. |
| `work_id` | UUID string / null | ID WorkManager thật; null trước khi được cấp/biết. Work periodic có thể giữ cùng work ID qua nhiều chu kỳ. |
| `work_attempt` | integer >= 0 / null | `runAttemptCount` WorkManager, bắt đầu từ 0; null khi không ở một lượt worker. |
| `network_call_id` | UUID string / null | UUID riêng cho mỗi HTTP GET snapshot, nối `snapshot_fetch_started` và `snapshot_fetch_completed`; null ngoài cặp này. Retry GET tạo ID mới, giữ `request_id`. |
| `update_id` | ID string / null | Idempotency key update snapshot theo API; không phải `request_id` của worker. |
| `signal_ids` | array ID string, có thể `[]` | ID do server tạo cho tín hiệu push; phải khác FCM message ID. Giữ tất cả signal IDs khi coalesce, không ghi đè tín hiệu đến sau. |
| `send_attempt_id` | ID string / null | Mỗi lần server gọi FCM tạo một ID riêng; retry cùng signal tạo ID attempt mới. Android để null nếu không thật sự biết. |
| `message_id` | opaque string / null | Giá trị thật từ FCM response hoặc Android callback; null khi chưa được cấp/không có. Không tự rút gọn ID để ép hai phía khớp. |
| `ttl_ms` | integer 0–2419200000 / null | TTL FCM được cấu hình thực tế theo milliseconds khi gửi, lưu ở event gửi; event không biết để null. Chưa chốt giá trị cố định ở SEM-26. |
| `http_status` | integer 100–599 / null | HTTP status thật của lần GET/FCM khi nhận response; không có response để null, không dùng 0. |
| `provider_code` | string / null | Mã FCM/API an toàn đã nhận, ví dụ `UNREGISTERED` hoặc `messaging/registration-token-not-registered`; chỉ nhận `^[A-Z][A-Z0-9_]{0,63}$` hoặc `^messaging/[a-z][a-z0-9-]{0,63}$`, ngoài hai dạng ghi null. Không ghi error body. |
| `outcome` | string enum | Một trong các giá trị được phép cho `event_type` ở bảng dưới; không suy outcome từ việc thiếu event. |
| `reason` | uppercase code / null | Mã an toàn `^[A-Z][A-Z0-9_]{0,63}$`; failure/rejected/unknown/retry/skipped/stale bắt buộc có reason, còn lại có thể null. Registry tối thiểu ở dưới. |

`boot_session_id` là alias không định danh, ví dụ nonce ngẫu nhiên được lưu cùng marker boot và đổi sau reboot; không export boot ID/serial thật. Nếu không thể biết chắc đã reboot, dùng null thay vì ghép nhầm. Chỉ trừ `elapsed_realtime_ms` của cùng device alias **và cùng boot session ID khác null**. UTC được ghi hai đầu; trước khi tính latency liên máy phải kiểm soát/ghi clock offset theo protocol, nếu không thì báo không đủ cơ sở. Nguồn clock: [Android SystemClock](https://developer.android.com/reference/android/os/SystemClock).

## Event types, outcome và trường tối thiểu theo sự kiện

Mọi quy tắc ở bảng trường chung vẫn áp dụng. `data_version`/`cached_version` không biết thì null trừ nơi bảng ghi bắt buộc. Các giá trị outcome dưới đây có phân biệt chữ hoa/thường.

| `event_type` | Origin / source | `outcome` | Điều kiện ghi và correlation |
|---|---|---|---|
| `server_updated` | SERVER / null | `updated` | Commit snapshot mới; `update_id` và `data_version` version đã commit bắt buộc; cùng transaction với state/ledger. Replay không tạo event mới. |
| `push_send_accepted` | SERVER / PUSH | `accepted` | FCM response thành công của send thật; đúng một `signal_ids`, có `send_attempt_id`, `ttl_ms`, `message_id` thật; `data_version` là version server gửi hint. Dry-run không ghi event này. |
| `push_send_rejected` | SERVER / PUSH | `rejected` | FCM trả lỗi xác định; một signal, attempt, TTL, reason; `provider_code`/`http_status` ghi khi có; message ID null nếu chưa cấp. |
| `push_send_failed_local` | SERVER / PUSH | `failure` | Payload/config lỗi trước khi gọi FCM; một signal nếu đã tạo, `send_attempt_id`, `message_id`, `provider_code`, `http_status` đều null; TTL null nếu chưa xác định, reason bắt buộc. Không ghi thành provider rejection. |
| `push_send_unknown` | SERVER / PUSH | `unknown` | Đã thử gửi nhưng response không quan sát được; một signal, attempt, TTL, reason; không khẳng định rejected hay delivered. |
| `push_send_skipped` | SERVER / PUSH | `skipped` | Cố ý bỏ gửi trong fault injection; reason `FAULT_INJECTION_SKIP`, không có FCM message ID/attempt; `data_version` là snapshot version đã commit. Không gọi đây là FCM làm mất tin. |
| `push_received` | ANDROID / PUSH | `received` | Callback thật; một signal từ data; hint để ở `version_hint`, `data_version` null nếu chưa GET; FCM message ID có thể null. Callback có thể đến sau khi mode không còn cho phép: vẫn ghi observed receipt rồi từ chối trigger. |
| `trigger_rejected` | ANDROID / bất kỳ source | `rejected` | Run xác định được nhưng mode/trigger hoặc input không hợp lệ; reason bắt buộc, không ghi enqueue như đã thành công. |
| `periodic_registered` | ANDROID / PERIODIC | `registered` | Đăng ký periodic được hệ thống chấp nhận; có `work_id` lịch thật, `request_id` null vì chu kỳ chưa bắt đầu. Đăng ký không xác nhận worker chạy. |
| `work_enqueued` | ANDROID / MANUAL hoặc PUSH | `enqueued` | Hệ thống đã chấp nhận enqueue one-time; có `request_id` và `work_id` thật. Receipt không xác nhận worker đã chạy. |
| `work_started` | ANDROID / bất kỳ source | `started` | Worker thật bắt đầu; có `request_id`, `work_id`, `work_attempt`; `data_version` null, `cached_version` là cache lúc bắt đầu nếu có. |
| `snapshot_fetch_started` | ANDROID / bất kỳ source | `started` | Ngay trước mỗi lần gọi GET; có `request_id`, `work_id`, `work_attempt`, `network_call_id`; `data_version` null. Số ID khác nhau là số lần client bắt đầu gọi, chưa chứng minh server nhận đủ request nếu process chết/mạng lỗi. |
| `snapshot_fetch_completed` | ANDROID / bất kỳ source | `success` / `not_modified` / `failure` | Cùng `network_call_id` với fetch_started; HTTP 200 hợp schema → `success` và `data_version` từ response; 304 → `not_modified`, `data_version` null; lỗi → `failure`/reason, status null nếu không có response. |
| `snapshot_applied` | ANDROID / bất kỳ source | `applied` | Room đã commit items + metadata version + event trong cùng transaction; có request/work/attempt, `data_version` và `cached_version` bằng version mới. Không ghi trước commit. |
| `snapshot_unchanged` | ANDROID / bất kỳ source | `unchanged` | 200 version bằng cache hoặc 304 có cache xác thực hợp lệ; có request/work/attempt và `cached_version`. Với 200, `data_version` là response; với 304, null vì không có body. Không ghi lại items. |
| `snapshot_stale` | ANDROID / bất kỳ source | `stale` | 200 version thấp hơn cache trong transaction; có request/work/attempt, `data_version` là version response và `cached_version` là cache mới hơn, reason `VERSION_STALE`. Không ghi đè cache. |
| `sync_retrying` | ANDROID / bất kỳ source | `retry` | Lỗi tạm thời và còn lượt retry; có request/work/attempt, reason. Không phát applied. |
| `sync_failed` | ANDROID / bất kỳ source | `failure` | Lỗi vĩnh viễn hoặc đã hết retry; có request/work/attempt, reason. Không phát applied. |

Với đăng ký periodic và work/snapshot event, `source=PERIODIC` chỉ được chạy trong mode PERIODIC/HYBRID; `source=PUSH` chỉ trong PUSH/HYBRID. `push_received`/`trigger_rejected` là ngoại lệ để quan sát và từ chối tín hiệu khi mode không cho phép. Không đồng nhất `server_updated` với `push_send_accepted`, accepted với received, enqueue với started, started với applied. Callback có thể được ghi trước khi server lưu response; không dựa vào thứ tự timestamp giữa hai máy để áp đặt trình tự này.

`reason` tối thiểu: `MODE_DISABLED`, `INVALID_TRIGGER`, `VERSION_STALE`, `INVALID_RESPONSE`, `HTTP_ERROR`, `NETWORK_ERROR`, `TIMEOUT`, `STORE_UNAVAILABLE`, `INVALID_FCM_CONFIG`, `INVALID_PAYLOAD`, `FCM_REJECTED`, `FCM_RESPONSE_UNKNOWN`, `FAULT_INJECTION_SKIP`, `RETRY_EXHAUSTED`, `UNEXPECTED_ERROR`. Các mã là phân loại an toàn, không chép error text. Mã mới phải được ghi trong delta schema; `provider_code` không thay thế `reason`.

## Nối run, attempt, FCM và worker

1. Mỗi update có `run_id`, `mode`, `device_alias`, `update_id`; `server_updated.data_version` bằng version sau commit. POST không tự gửi FCM.
2. Với PUSH, server tạo `signal_id` cho tín hiệu logic, giữ qua retry gửi; tạo `send_attempt_id` mới cho mỗi lần gọi FCM. Trong data-only payload gửi **các giá trị string**: `run_id`, `mode`, `source="PUSH"`, `version_hint` dạng số nguyên thập phân không âm và `signal_id`. Không có `notification` hoặc credential trong data. `device_alias` lấy từ cấu hình run trên từng thiết bị, không lấy từ token.
3. Android đối chiếu run/mode với cấu hình run hợp lệ; không thay `run_id` thiếu/sai bằng giá trị mặc định. Ghi `push_received`, sau đó tạo `request_id` cho logical enqueue, giữ `signal_id` và FCM ID khi có. Với một update + nhiều thiết bị/run, mỗi run/device dùng signal ID riêng và correlation riêng.
4. Mỗi periodic cycle tạo `request_id` mới, dù `work_id` giữ nguyên. Worker retry giữ `request_id`/`work_id`, tăng `work_attempt`; mỗi GET thật tạo `network_call_id` mới. `work_enqueued` không bắt buộc có `work_attempt`.
5. Một worker có thể đại diện nhiều tín hiệu; ghi đầy đủ `signal_ids` trong các event liên quan và bảo đảm tín hiệu mới đến gần lúc worker kết thúc được giữ cho lượt sync sau. Mảng này không buộc mỗi signal phải có một DB write. Chiến lược coalesce/race thuộc SEM-38/39, không giả định `KEEP` đủ an toàn.
6. `message_id` sender và callback giữ nguyên theo nguồn, không join bắt buộc bằng cách so chuỗi hoặc cắt prefix: dùng `run_id` + `device_alias` + `signal_id` để nối; `request_id` nối enqueue → work → fetch/apply. Không join chỉ bằng version/timestamp. `send_attempt_id` nối attempt trên server; khi không biết attempt nào đã delivered, không tự gán một attempt cho callback.

Nếu `version_hint` cũ hoặc bị lặp, worker vẫn GET snapshot hiện hành và dùng version guard. Nếu coalesce khiến quan hệ message ID/attempt không biết rõ, để các trường tương ứng null, giữ danh sách signal IDs; không hy sinh provenance để có một dòng dễ join.

## Ví dụ JSONL fixture — không phải kết quả đo

Ví dụ dưới mô tả bốn event khác nhau; các UUID, thời gian, alias, ID và `"<fixture-fcm-response-id>"` đều **chỉ là placeholder do tác giả đặt**, không phải FCM ID đã cấp. Khi chạy thật, `push_send_accepted.message_id` phải thay bằng chuỗi thật từ response; nếu chưa có response thì không được ghi accepted. Ví dụ không chứa token.

```jsonl
{"schema_version":"2.0.0","event_id":"00000000-0000-4000-8000-000000000001","event_type":"push_send_accepted","origin":"SERVER","run_id":"run-demo-001","mode":"PUSH","source":"PUSH","device_alias":"emulator-01","timestamp_utc":"2026-11-02T03:00:00Z","elapsed_realtime_ms":null,"boot_session_id":null,"data_version":1,"cached_version":null,"version_hint":1,"request_id":null,"work_id":null,"work_attempt":null,"network_call_id":null,"update_id":"update-demo-001","signal_ids":["signal-demo-001"],"send_attempt_id":"send-attempt-001","message_id":"<fixture-fcm-response-id>","ttl_ms":600000,"http_status":200,"provider_code":null,"outcome":"accepted","reason":null}
{"schema_version":"2.0.0","event_id":"00000000-0000-4000-8000-000000000002","event_type":"push_received","origin":"ANDROID","run_id":"run-demo-001","mode":"PUSH","source":"PUSH","device_alias":"emulator-01","timestamp_utc":"2026-11-02T03:00:01Z","elapsed_realtime_ms":31000,"boot_session_id":"boot-fixture-01","data_version":null,"cached_version":0,"version_hint":1,"request_id":null,"work_id":null,"work_attempt":null,"network_call_id":null,"update_id":null,"signal_ids":["signal-demo-001"],"send_attempt_id":null,"message_id":null,"ttl_ms":null,"http_status":null,"provider_code":null,"outcome":"received","reason":null}
{"schema_version":"2.0.0","event_id":"00000000-0000-4000-8000-000000000003","event_type":"work_started","origin":"ANDROID","run_id":"run-demo-001","mode":"PUSH","source":"PUSH","device_alias":"emulator-01","timestamp_utc":"2026-11-02T03:00:02Z","elapsed_realtime_ms":32000,"boot_session_id":"boot-fixture-01","data_version":null,"cached_version":0,"version_hint":1,"request_id":"request-demo-001","work_id":"00000000-0000-4000-8000-000000000011","work_attempt":0,"network_call_id":null,"update_id":null,"signal_ids":["signal-demo-001"],"send_attempt_id":null,"message_id":null,"ttl_ms":null,"http_status":null,"provider_code":null,"outcome":"started","reason":null}
{"schema_version":"2.0.0","event_id":"00000000-0000-4000-8000-000000000004","event_type":"snapshot_applied","origin":"ANDROID","run_id":"run-demo-001","mode":"PUSH","source":"PUSH","device_alias":"emulator-01","timestamp_utc":"2026-11-02T03:00:03Z","elapsed_realtime_ms":33000,"boot_session_id":"boot-fixture-01","data_version":1,"cached_version":1,"version_hint":1,"request_id":"request-demo-001","work_id":"00000000-0000-4000-8000-000000000011","work_attempt":0,"network_call_id":null,"update_id":null,"signal_ids":["signal-demo-001"],"send_attempt_id":null,"message_id":null,"ttl_ms":null,"http_status":null,"provider_code":null,"outcome":"applied","reason":null}
```

Fixture chỉ minh họa bốn mốc chính; không biểu diễn toàn bộ `work_enqueued` và fetch events mà runtime có instrument phải ghi. Parser không suy event thiếu thành timeout/success. Run manifest quyết định cửa sổ quan sát; run hết cửa sổ mà không có applied giữ outcome timeout/không quan sát được, không gán latency 0.

## Bàn giao và thay đổi phiên bản

SEM-24 export/manifest, SEM-25 Android core/serializer, SEM-27 server/log, SEM-35 FCM sender và SEM-45 parser thực hiện cùng schema này sau khi đầu ra được chấp thuận.

**Delta 1.0.0 → 2.0.0, 02/11/2026:** bản nháp 1.0.0 trong commit `5e7eb82` dùng camelCase và khối `correlation` lồng, chưa có phân biệt đầy đủ sự kiện server/FCM; bản 2.0.0 dùng JSONL snake_case phẳng, có version, origin, mode/device, các correlation nullable, signal IDs, attempt, UTC/monotonic và event/outcome được liệt kê ở trên. Đây là thay đổi **không tương thích**: SEM-25 cần adapter/serializer và bổ sung thông tin trong Room, SEM-27/35 phát log mới, SEM-24/45 xử lý schema mới. Không tự gán giá trị thật cho các trường bản cũ không có; dữ liệu thiếu được báo không đủ điều kiện phân tích, không ghép run v1/v2. Nhóm trưởng cần review trước khi coi 2.0.0 là bàn giao cuối.

Sửa sau bàn giao cần ghi ngày, version cũ/mới, delta, khả năng tương thích, consumer và các run phải đo lại. Build/run của phiên bản khác nhau không gộp vào cùng thống kê nếu không có nhóm/giải thích riêng.

[CHECKS SEM-26](evidence/SEM-26/CHECKS.md) ghi các kiểm tra contract và những phần chưa chạy; schema này không xác nhận runtime hiện tại đã tuân thủ.
