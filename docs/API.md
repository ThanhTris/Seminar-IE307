# Hợp đồng HTTP snapshot — SEM-26

**Contract `2.0.0` — bản bàn giao chờ review, 02/11/2026.** Đây là đặc tả để SEM-25 và SEM-27 triển khai độc lập, không phải xác nhận code hiện tại đã tuân thủ. Bản nháp `1.0.0` đã có trên main cùng scaffold; delta không tương thích được ghi ở cuối tài liệu. Các ví dụ là fixture, không phải dữ liệu đo. Event tương ứng được định nghĩa tại [EVENT_SCHEMA.md](EVENT_SCHEMA.md); hành vi shared sync phải giữ [hợp đồng SEM-14](mechanisms/SHARED_SYNC.md).

## Quy ước chung

- Base URL do cấu hình local; ví dụ `http://10.0.2.2:3000` chỉ dành cho emulator chạy cùng host server. Đường dẫn dưới đây tính từ root base URL. Cổng/host không cố định trong contract; xem [môi trường SEM-13](environment/SERVER_FIREBASE.md).
- JSON UTF-8 (`Content-Type: application/json; charset=utf-8`); JSON object không nhận duplicate key. Server trả `X-API-Version: 2.0.0` trên mọi response, kể cả lỗi và 304. Client gửi `Accept: application/json`, từ chối response thiếu version header hoặc có major không hỗ trợ; với JSON body, `api_version` phải khớp header. Không có auth sản phẩm trong phạm vi demo: chỉ chạy trên mạng test tin cậy, không đưa endpoint cập nhật không bảo vệ ra Internet.
- Timestamp là chuỗi RFC 3339 UTC có hậu tố `Z`, ví dụ `2026-11-02T03:00:00Z` hoặc `2026-11-02T03:00:00.123Z`. Không yêu cầu cố định số chữ số phần giây.
- Các ID do ứng dụng tạo (`run_id`, `device_alias`, `update_id`, `request_id`, item `id`) phân biệt hoa/thường, không có khoảng trắng, khớp `^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$`. Không dùng token, serial hoặc thông tin cá nhân làm ID. FCM `message_id` là chuỗi opaque do FCM cấp và không chịu regex này.
- Version là JSON integer trong khoảng **0–9007199254740991** (`2^53-1`), tương thích số nguyên an toàn JavaScript và Kotlin `Long`; không nhận số âm, số thực hoặc chuỗi số. Khi không thể tăng vì đã đạt giới hạn, trả lỗi `VERSION_EXHAUSTED`, không reset version.
- `X-Correlation-Request-Id` là header tùy chọn chứa `request_id` hợp lệ. SyncWorker **phải** gửi ID của logical sync, giữ nguyên qua retry; lệnh health/GET thủ công có thể không gửi. Server phản hồi cùng header khi hợp lệ. Header sai định dạng trả `400 INVALID_REQUEST_ID`, không phản chiếu chuỗi không hợp lệ.

## Snapshot và version

Server sở hữu một snapshot hiện hành dạng object `version`, `last_modified_utc`, `items`. Store mới khởi tạo **version 0, items rỗng**, `last_modified_utc` là thời gian UTC tạo store và được persist; không tạo fixture như bản tin thật. Mỗi update thêm một item lên đầu danh sách. Mỗi item response có `id`, `title`, `body`, `version`; `id` duy nhất, `version` là version snapshot tại thời điểm item được thêm và nằm trong `1..snapshot.version`. Các item sắp theo version giảm dần, version item không trùng; nếu `version > 0`, item mới nhất phải có version bằng snapshot version. Đây vẫn là một snapshot toàn bộ, không phải danh sách delta.

Mỗi update hợp lệ với `update_id` mới tạo version `trước + 1`, kể cả nội dung giống hệt; server không cho client tự chọn version. Update được tuần tự hóa, không có hai update mới cùng version. Snapshot/version, thời gian, bản ghi idempotency và event `server_updated` phải commit bền vững cùng nhau trước response; sau restart giữ nguyên cả bốn. Không có snapshot và event nửa chừng. Đọc GET lấy một trạng thái nhất quán, không trộn items/version của hai update.

Có thể hiện thực bằng một durable transaction hoặc transactional outbox trong cùng state: event có `event_id` ổn định được lưu cùng snapshot và ledger; exporter chuyển ra JSONL sau đó. Nếu crash sau commit nhưng trước export, phục hồi/export lại event đó; consumer deduplicate theo `event_id`. Không yêu cầu hai file được ghi độc lập cùng lúc mà không có cơ chế khôi phục.

Client nhận 200 phải kiểm payload đầy đủ, item ID/version duy nhất, thứ tự giảm dần và version item nằm trong miền snapshot trước transaction; version 0 chỉ hợp lệ khi items rỗng. Trong Room đọc **cached snapshot version** mới nhất trong transaction: lớn hơn thì thay toàn bộ cache và ghi `snapshot_applied` cùng transaction; bằng thì `snapshot_unchanged`, không ghi lại items; nhỏ hơn thì `snapshot_stale`, không giảm version. GET nằm ngoài transaction. Version cache phải lưu trong metadata độc lập với danh sách items: snapshot rỗng vẫn có version; không dùng `MAX(item.version)` làm nguồn duy nhất. Version hint của push không được dùng thay response để áp dụng dữ liệu.

## `GET /health`

Kiểm process và khả năng đọc store hiện hành. `200 OK` khi store sẵn sàng:

```json
{"api_version":"2.0.0","status":"ok"}
```

Store không thể mở/đọc: `503 STORE_UNAVAILABLE`, theo envelope lỗi phía dưới. Health không gửi push, không thay đổi snapshot và không tự khởi tạo sync Android.

## `GET /api/bulletin`

Không có `If-None-Match`: trả `200 OK`, JSON snapshot và `ETag: "v<version>"`; ETag được tạo từ đúng version trong body. Ví dụ fixture response với `ETag: "v1"`:

```json
{
  "api_version": "2.0.0",
  "version": 1,
  "last_modified_utc": "2026-11-02T03:00:00Z",
  "items": [
    {"id": "bulletin-1", "title": "Lịch seminar", "body": "Phòng học đã đổi.", "version": 1}
  ]
}
```

Server gửi `Cache-Control: no-cache`; client có cache **đầy đủ** cho version `N` có thể gửi `If-None-Match: "vN"`. Khi validator khớp snapshot hiện hành, server trả **304, không có body**, kèm ETag hiện hành và `X-API-Version`; khi không khớp trả 200 và snapshot hiện hành. Server thực hiện so sánh yếu theo [HTTP If-None-Match](https://www.rfc-editor.org/rfc/rfc9110#section-13.1.2), gồm danh sách validators và `*`; header sai cú pháp được bỏ qua, trả 200. Đây là conditional GET, không phải chỉ định server trả version lịch sử.

304 chỉ có ý nghĩa nếu client còn cache tương ứng. Nếu mất hoặc không xác minh được cache, client thực hiện lại GET **không** `If-None-Match`; không đánh dấu applied từ 304. Khi xử lý response, vẫn kiểm version hiện tại trong transaction vì một worker khác có thể đã commit phiên bản mới hơn trong lúc request đang chạy. Thời gian và số lần retry thuộc SEM-39; 304 không tự enqueue work mới.

## `POST /api/bulletin/update`

Lệnh quản trị demo thêm **một bản tin** vào snapshot hiện hành, giữ đường dẫn và ý nghĩa thêm bản tin của bản nháp hiện có. Request JSON bắt buộc đúng các trường sau; không nhận `version` hoặc `id` do client chỉ định:

```json
{
  "update_id": "update-demo-001",
  "run_id": "run-demo-001",
  "mode": "PUSH",
  "device_alias": "emulator-01",
  "title": "Lịch seminar",
  "body": "Phòng học đã đổi."
}
```

`mode` là `PERIODIC`, `PUSH` hoặc `HYBRID` được chụp cho run; `run_id`, `device_alias`, `update_id` theo quy tắc ID chung. `title` là string dài 1–256 Unicode code points, không chỉ whitespace; `body` là string dài 0–4096 code points. Không nhận `null`, trường thiếu hoặc trường thừa ở request. Server tạo ID mới `bulletin-<version>` và chèn item lên đầu; các item cũ giữ nguyên ID và version của chúng. Một snapshot có tối đa 100 item; khi đầy, trả `409 SNAPSHOT_FULL`, không tự xóa item. Giới hạn request body **1 MiB = 1048576 bytes** sau UTF-8; vượt giới hạn trả 413. Payload lỗi không được thay đổi store.

Response sau commit: `200 OK`, ETag của version đã commit và JSON sau (`replayed: false`). Response cố ý chứa snapshot đã commit để CLI kiểm tra; nó không phải tín hiệu push.

```json
{
  "api_version": "2.0.0",
  "update_id": "update-demo-001",
  "run_id": "run-demo-001",
  "replayed": false,
  "version": 1,
  "last_modified_utc": "2026-11-02T03:00:00Z",
  "items": [
    {"id": "bulletin-1", "title": "Lịch seminar", "body": "Phòng học đã đổi.", "version": 1}
  ]
}
```

### Retry và concurrent update

- `update_id` là idempotency key do caller tạo trước request và giữ qua retry, kể cả sau timeout/restart. Server lưu bền vững request đã chuẩn hóa và response gốc cùng snapshot/event trong một commit. Các request là như nhau nếu toàn bộ trường bắt buộc có cùng giá trị sau parse JSON, không xét thứ tự key object; nội dung string phải giống hệt. `run_id`, `mode`, `device_alias` là một phần nội dung so sánh.
- Cùng `update_id` + cùng request: trả lại **version/items/timestamp/ETag của commit gốc**, `replayed: true`; không tăng version, không phát `server_updated` lần hai. Response replay có thể cũ hơn snapshot hiện hành nếu update khác đã commit sau đó; GET mới cho biết snapshot hiện hành.
- Cùng `update_id` + request khác: `409 UPDATE_ID_CONFLICT`, không thay đổi store. Hai request đồng thời cùng ID cũng tuân theo các quy tắc này; hai ID khác nhau được tuần tự hóa và nhận hai version khác nhau.
- Kiểm ledger trước giới hạn version/sức chứa: replay của update đã commit vẫn phải thành công dù snapshot hiện đã đầy hoặc version đã chạm giới hạn. Chỉ update ID mới bị từ chối khi đầy hoặc không thể tăng version.
- Ledger phải tồn tại qua restart và giữ đến khi xóa/reset toàn bộ store demo có chủ ý; thao tác reset không thuộc API này. Nếu trạng thái cũ hoặc ledger hỏng/mất, server không tự tạo version 0 đè store: trả 503 và yêu cầu xử lý môi trường. Một reset/hủy ledger trong lúc còn cache/run có thể làm giảm version và làm hỏng phép đo; chỉ bắt đầu môi trường đo mới sau khi xóa cache liên quan và ghi rõ reset.
- Không có giao dịch nguyên tử giữa snapshot và FCM: POST chỉ cập nhật snapshot, **không tự gửi push**. SEM-35 gửi tín hiệu riêng sau commit; SEM-40 có thể cố ý bỏ gửi có nhãn. Nếu client không nhận được response POST, kết quả commit chưa biết; retry cùng `update_id`, không tự sinh ID mới.
- CLI cập nhật đi qua API cùng ledger; không fallback tự ghi file khi HTTP lỗi, vì request có thể đã commit hoặc cạnh tranh với server. Khi server không khả dụng, ghi kết quả chưa xác định/không gửi được và giữ `update_id` để retry qua API.

## Lỗi và retry

Mọi response lỗi do API tạo dùng `application/json` và envelope cố định. `request_id` lấy từ header hợp lệ hoặc `null`; `message` là mô tả an toàn, không chứa payload, token, đường dẫn local hoặc stack trace. Ví dụ fixture:

```json
{"api_version":"2.0.0","error":{"code":"INVALID_ARGUMENT","message":"Invalid snapshot request","request_id":null}}
```

| HTTP | `error.code` | Điều kiện | Xử lý client |
|---|---|---|---|
| 400 | `INVALID_JSON`, `INVALID_ARGUMENT`, `INVALID_REQUEST_ID` | JSON sai / thiếu, thừa hoặc sai kiểu giá trị / correlation header sai | Không retry nguyên request; sửa input |
| 404 | `NOT_FOUND` | Không có route | Không retry; sửa base URL/path |
| 405 | `METHOD_NOT_ALLOWED` | Route có nhưng method không hỗ trợ; kèm `Allow` | Không retry; sửa method |
| 409 | `UPDATE_ID_CONFLICT`, `VERSION_EXHAUSTED`, `SNAPSHOT_FULL` | ID đã dùng cho request khác / không thể tăng version / đã có 100 item | Không retry nguyên request; điều tra ID hoặc môi trường |
| 413 / 415 | `PAYLOAD_TOO_LARGE` / `UNSUPPORTED_MEDIA_TYPE` | Body quá 1 MiB / POST không phải `application/json` | Không retry nguyên request; sửa input |
| 429 / 503 | `RATE_LIMITED` / `STORE_UNAVAILABLE` | Rate limit hoặc store tạm thời không sẵn sàng | Có thể retry hữu hạn, backoff; tôn trọng `Retry-After` nếu có |
| 500 | `INTERNAL` | Lỗi không phân loại được | Có thể retry hữu hạn; POST giữ `update_id` vì commit có thể chưa rõ |

Network timeout, mất kết nối hoặc HTTP 408/5xx không có envelope hợp lệ: giữ status/code nếu biết, phân loại tạm thời; không bịa provider error. Response 200 JSON sai schema, version ngoài miền, item trùng hoặc item version ngoài miền snapshot là **lỗi contract vĩnh viễn** cho response đó, không ghi cache và không retry vô hạn. Các lỗi 4xx khác không nêu trong bảng được coi là vĩnh viễn, trừ 408/429. Khi retry hết giới hạn, ghi failure theo event schema; chính sách số lần/cụ thể thuộc SEM-39.

Đối với POST, lỗi validation 400/409/413/415 không commit update. Với 5xx/timeout sau khi request đã gửi, caller không suy đoán commit hay chưa; retry cùng `update_id`. Không đưa response lỗi HTTP hoặc exception thô vào `reason`/log công khai.

## Phiên bản và bàn giao

### Delta `1.0.0` → `2.0.0`, ngày 02/11/2026

Bản `1.0.0` đã nằm trên `main` từ commit `5e7eb82` cùng scaffold SEM-23, dù SEM-26 còn Todo; đây là thay đổi **không tương thích**, chờ nhóm trưởng review, không tuyên bố server/Android đã nâng cấp. Giữ `GET /health`, `GET /api/bulletin`, `POST /api/bulletin/update` và mô hình thêm một bản tin. Thay đổi chính: thêm version header/body; POST yêu cầu `update_id`, `mode`, `device_alias` và idempotency bền vững; bỏ hành vi ngầm tạo title/body/run; khởi tạo store version 0 rỗng; chỉ 304 khi ETag thật khớp, không dùng `since_version` hoặc `"<version>"` như bản nháp; quy định lỗi/validation; event JSONL đổi tên và correlation theo [delta event](EVENT_SCHEMA.md#bàn-giao-và-thay-đổi-phiên-bản). Không có cơ chế tự nâng dữ liệu v1: SEM-27 phải tạo migration hoặc môi trường store/cache mới được ghi nhận và kiểm lại version trước khi thử. Client và server phải nâng cùng major trước khi chạy M1; không trộn run v1/v2.

Sau bàn giao, mọi thay đổi tiếp phải ghi **delta** (phiên bản cũ/mới, ngày, thay đổi, tương thích, task/run bị ảnh hưởng) tại đây và trong [EVENT_SCHEMA](EVENT_SCHEMA.md). Breaking change cần major version mới và các consumer cùng cập nhật; thêm trường không phá vỡ là minor, sửa văn bản không đổi wire là patch. Consumer từ chối major không hỗ trợ, không âm thầm parse sai; CI/build và run phải ghi đúng contract version.

| Consumer | Cần thực hiện |
|---|---|
| SEM-25 | GET/ETag, validate response, version metadata cho snapshot rỗng, transaction guard và event schema; cập nhật adapter Android nếu cần |
| SEM-27 | Server/store/API/CLI theo contract, atomic commit + ledger, lockfile và kiểm restart/concurrency/replay |
| SEM-24 | Xuất manifest/log theo event schema, không lộ định danh hoặc token |
| SEM-45 | Parse event version/mode/source/correlation, giữ timeout và các mốc tách biệt |

Đã có server và Android scaffold trên main nhưng **chưa được xác thực tuân thủ contract 2.0.0**; xem [CHECKS SEM-26](evidence/SEM-26/CHECKS.md). Task chỉ bàn giao tài liệu; phần code thuộc owner/task tương ứng.
