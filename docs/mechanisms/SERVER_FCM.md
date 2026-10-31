# Server, FCM accepted và correlation — SEM-18

Tâm (`HoaiTam`), đối chiếu nguồn ngày **31/10/2026**. Đây là giải thích cơ chế và đề xuất cho các task triển khai, **không phải log thực nghiệm hoặc xác nhận đã gửi push**. Baseline của [PLAN](../PLAN.md) là FCM HTTP v1, `AndroidConfig` v1, data-only, normal priority; không trộn `AndroidConfigV2`/BackgroundSync hoặc callback EAP. Xem [phạm vi API mới](https://firebase.google.com/docs/cloud-messaging/send/v2-api).

Luồng và bất biến bám [SHARED_SYNC](SHARED_SYNC.md); điều kiện đo theo [EXPERIMENT_PROTOCOL](../EXPERIMENT_PROTOCOL.md). Endpoint snapshot, wire format, tên event và các trường mở rộng bên dưới phải được SEM-26 chốt trong API/event schema trước code. SEM-18 không thay hợp đồng đó bằng ví dụ.

## Từ cập nhật snapshot đến cache Android

1. **Server commit snapshot:** cập nhật nội dung và version tăng đơn điệu vào persistent store; chỉ ghi `server_updated` sau khi persist thành công. Nếu persist lỗi, không gửi tín hiệu như thể version mới đã tồn tại. SEM-27 triển khai store và quy tắc qua restart.
2. **Server chuẩn bị tín hiệu:** lấy version vừa commit, run/mode/device alias của ca thử, tạo ID tín hiệu của ứng dụng và ghi một send attempt. Push mang hint để app lấy snapshot; không phải bản cache mới được áp dụng sẵn.
3. **Gửi qua FCM:** server dùng credential local được cấp quyền và Admin SDK stable để gửi data-only. Không đặt `notification` ở message hoặc `android.notification`. [Hồ sơ SEM-13](../environment/SERVER_FIREBASE.md) ghi điều kiện project/IAM/cấu hình chưa xác nhận.
4. **Nhận kết quả gửi:** response thành công của FCM chỉ xác nhận chấp nhận để phân phối. HTTP v1 trả trường `name`; Admin SDK `send(message)` resolve chuỗi ID. Lưu nguyên giá trị thật đã trả và `push_send_accepted`; có lỗi rõ ràng từ FCM thì ghi `push_send_rejected`. Chưa có response thì ID vẫn null. Nguồn: [HTTP v1](https://firebase.google.com/docs/cloud-messaging/send/v1-api), [Admin SDK send](https://firebase.google.com/docs/reference/admin/node/firebase-admin.messaging.messaging#messagingsend).
5. **App nhận callback:** với baseline v1 data-only, `FirebaseMessagingService.onMessageReceived` ghi `push_received` và correlation rồi enqueue sync. Callback có cửa sổ xử lý ngắn; không thực hiện toàn bộ GET/sync dài trong callback. [Firebase receive messages](https://firebase.google.com/docs/cloud-messaging/android/receive-messages).
6. **WorkManager nhận yêu cầu:** ghi `work_enqueued` khi enqueue được chấp nhận và đã biết ID tương ứng. Đây vẫn chưa phải worker chạy. Khi trigger không hợp mode/run, ghi lý do từ chối; không gán tín hiệu cũ vào run hiện hành.
7. **Worker chạy:** ghi `work_started`; dùng cùng SyncWorker/SyncRepository như periodic/manual, rồi GET snapshot hiện hành. Snapshot trả về có thể mới hơn version hint nếu server đã cập nhật thêm.
8. **Room áp dụng:** so version trong transaction, chỉ áp dụng khi mới hơn cache; cache update và `snapshot_applied` cùng transaction, chỉ quan sát sau commit. Bằng nhau ghi unchanged, thấp hơn giữ cache và ghi stale. UI chỉ đọc cache, mở UI không tự tạo GET. Các quy tắc này thuộc [shared sync contract](SHARED_SYNC.md).

Persist snapshot và gửi FCM là hai thao tác khác nhau: persist thành công nhưng gửi lỗi thì snapshot vẫn tồn tại cho GET/periodic, không rollback dữ liệu chỉ vì push chưa gửi được. Cố ý không gửi push thuộc SEM-40 và phải có nhãn fault injection, không gọi là FCM làm mất tin.

| Event | Bằng chứng cho phép ghi | Điều chưa được kết luận |
|---|---|---|
| `server_updated` | Store đã commit version mới | Chưa biết FCM đã nhận request |
| `push_send_accepted` | Send thật có response thành công/ID từ FCM | Chưa biết app đã nhận, worker chạy hay cache đổi |
| `push_received` | Callback trên Android đã nhận RemoteMessage | Chưa biết enqueue/sync có thành công |
| `work_enqueued` | WorkManager chấp nhận yêu cầu, có receipt/ID | Chưa biết thời điểm chạy |
| `work_started` | Worker thật bắt đầu | Chưa biết GET/transaction thành công |
| `snapshot_applied` | Transaction cache và event đã commit version mới | Không bảo đảm mọi tín hiệu đều được nhận hoặc áp dụng riêng |

Callback có thể được ghi trước khi server kịp nhận/lưu response gửi. Bảng trên là ranh giới bằng chứng, không áp đặt thứ tự timestamp giữa hai máy. [Firebase nêu rõ message ID không có nghĩa đã delivered](https://firebase.google.com/docs/cloud-messaging/customize-messages/setting-message-lifespan#lifetime_of_a_message).

## Payload minh họa và kết quả trả về

**Fixture minh họa, chưa gửi.** Token là placeholder, run/signal ID do ứng dụng đặt để giải thích, không phải ID do FCM cấp. `signal_id` là đề xuất mở rộng cho SEM-26. Ví dụ HTTP v1 gửi tới `POST https://fcm.googleapis.com/v1/projects/<project-id>/messages:send` sau khi có quyền thật:

```json
{
  "message": {
    "token": "<registration-token-local>",
    "data": {
      "run_id": "ILLUSTRATIVE-RUN",
      "mode": "PUSH",
      "source": "PUSH",
      "version_hint": "42",
      "signal_id": "ILLUSTRATIVE-SIGNAL"
    },
    "android": {
      "priority": "NORMAL",
      "ttl": "600s"
    }
  }
}
```

Các giá trị `data` là string. Tín hiệu không chứa snapshot đầy đủ, credential hay URL tùy ý để callback truy cập. Không đặt `message_id` giả vào payload; ID FCM chỉ lấy từ response/callback. Trong mẫu này không đặt collapse key; nếu task sau chọn dùng thì ghi rõ cấu hình trong run manifest và kiểm tác động riêng.

| Cấu hình | HTTP v1 JSON | Firebase Admin Node `Message` |
|---|---|---|
| Normal priority | `android.priority: "NORMAL"` | `android.priority: "normal"` |
| TTL minh họa 10 phút | `android.ttl: "600s"` | `android.ttl: 600000` (milliseconds) |
| Data-only | `message.data`; không có notification | `data`; không có notification |

Hai biểu diễn theo [FCM REST AndroidConfig](https://firebase.google.com/docs/reference/fcm/rest/v1/projects.messages#AndroidConfig) và [Admin Node AndroidConfig](https://firebase.google.com/docs/reference/admin/node/firebase-admin.messaging.androidconfig). Không truyền nguyên JSON HTTP v1 có wrapper `message` vào `send(message)` hoặc lấy số milliseconds làm số seconds.

HTTP v1 response có tên tài nguyên dạng `projects/{project-id}/messages/{id-from-fcm}`. Đây là **mô tả định dạng**, không phải response quan sát được. Đến lúc triển khai sender, giữ nguyên chuỗi FCM thật trong log đã loại token; ở SEM-18, mọi `message_id` runtime vẫn **null / Not run**. `send(message, true)` là dry-run validation, không được ghi thành accepted của một lần phân phối thật. [Admin SDK API](https://firebase.google.com/docs/reference/admin/node/firebase-admin.messaging.messaging#messagingsend).

## TTL và khoảng chưa biết app đã nhận

TTL giới hạn thời gian FCM giữ/thử phân phối tin, không phải thời hạn hoàn tất worker. Android/Web hỗ trợ 0–2.419.200 giây; không đặt TTL thì tối đa mặc định bốn tuần. TTL 0 bỏ tin không phân phối ngay được, không dùng để làm demo trông nhanh hơn. Khi thiết bị offline hoặc bị trì hoãn, accepted có thể không dẫn tới callback trong cửa sổ quan sát. Nguồn: [message lifespan](https://firebase.google.com/docs/cloud-messaging/customize-messages/setting-message-lifespan).

Normal priority có thể bị trì hoãn trong Doze; không đổi high priority để che sự trì hoãn. [Android priority](https://firebase.google.com/docs/cloud-messaging/android-message-priority). Giá trị 600 giây trong fixture chỉ minh họa đơn vị; SEM-35 chốt TTL dùng thật và ghi cùng cấu hình từng run, đặc biệt ca mất mạng E04. Đến cuối cửa sổ mà chưa có callback thì ghi “chưa quan sát được”, không tự suy ra TTL hết hoặc FCM làm mất tin. TTL hết không hủy worker mà app đã enqueue trước đó.

## Correlation từ server sang Android

Giữ các trường tối thiểu của PLAN: `run_id`, `event_id`, `source`, `mode`, `device_alias`, `data_version`, UTC timestamp, monotonic phía Android, IDs khi có, `outcome`/`reason`. Trường chưa biết để null theo schema, không điền 0/chuỗi ID tự nghĩ ra để làm log có vẻ đủ.

| ID / giá trị | Ai tạo, phạm vi | Quy tắc nối và nullable |
|---|---|---|
| `run_id` | Protocol/điều phối run | Có trước update/send; giữ nguyên qua callback/worker; thiếu hoặc sai thì từ chối, không dùng run đang active thay thế |
| `signal_id` (đề xuất) | Server, mỗi tín hiệu cập nhật logic | Gửi trong data để nối sender ↔ callback khi response FCM chưa có; giữ qua retry gửi cùng tín hiệu; không dùng thay `message_id` |
| `send_attempt_id` (đề xuất) | Server, mỗi lần gọi send | Một tín hiệu có thể có nhiều attempt; không dùng `request_id` của worker cho HTTP send attempt chưa liên quan |
| `message_id` | FCM response; Android từ `RemoteMessage.getMessageId()` | Null trước response hoặc khi callback không có; giữ raw value mỗi phía, coi opaque, không mặc định hai biểu diễn giống nhau |
| `request_id` | Enqueuer/core, mỗi yêu cầu sync logic | Sender chưa có thì null; tạo khi enqueue, giữ qua worker retry; mỗi chu kỳ periodic có request ID mới |
| `work_id` | WorkManager | Chưa có ở server/receipt sớm thì null; lấy ID thật lúc có; periodic có thể dùng lại work ID qua nhiều chu kỳ |
| `event_id` | Thành phần ghi event | Mỗi sự kiện có ID riêng; không tái sử dụng một event ID cho accepted/received/started/applied |
| `version_hint` / `data_version` | Hint từ server / version thật của event | Hint chỉ gợi ý; GET và version guard quyết định cache. Version server đã update khác với version cache đang có |

[RemoteMessage API](https://firebase.google.com/docs/reference/android/com/google/firebase/messaging/RemoteMessage#getMessageId()) xác nhận ID nullable và không nên dựa vào định dạng ổn định. `signal_id` giúp nối sự kiện ứng dụng; FCM ID vẫn được lưu riêng để đối chiếu khi đã biết. Nếu coalesce nhiều tín hiệu vào một work, cần giữ quan hệ nhiều tín hiệu → yêu cầu/work; không ghi đè một message ID duy nhất làm mất nguồn khác. SEM-26 chốt cách biểu diễn quan hệ, SEM-38/39 thực hiện và kiểm race theo shared contract.

Retry sau timeout gửi có thể tạo nhiều FCM message cho cùng tín hiệu. App phải chịu được tín hiệu trùng và giữ version không giảm; có hai `push_received` không có nghĩa phải có hai lần ghi snapshot. Không join log bằng timestamp hoặc version đơn lẻ vì nhiều attempt/run có thể trùng các giá trị đó.

## Đồng hồ và cách đọc timeline

Server và Android cùng ghi UTC có timezone rõ ràng, ví dụ ISO 8601 kết thúc `Z`. Đo và lưu clock offset trước/sau phiên theo protocol; thứ tự UTC giữa hai máy có thể bị lệch hoặc log tới muộn. Không lấy `received_utc - accepted_utc` làm độ trễ chính xác nếu chưa kiểm soát clock offset; FCM accepted cũng không phải mốc app nhận.

Android ghi thêm `SystemClock.elapsedRealtime()` (milliseconds kể từ boot, có tính deep sleep) tại callback, worker start và cache commit. Cùng thiết bị/cùng boot: `started_mono - received_mono` mô tả thời gian từ nhận đến worker bắt đầu; `applied_mono - started_mono` mô tả khoảng từ start đến commit, nếu đủ event đúng request/work. Không trừ monotonic của server với Android, không gộp qua reboot; ghi boot/session alias không định danh nếu cần phân tách. Nguồn: [Android SystemClock](https://developer.android.com/reference/android/os/SystemClock).

## Accepted, rejected và lỗi chưa xác định

| Tình huống | Cách ghi đề xuất | Hướng xử lý bàn giao |
|---|---|---|
| Send thật trả thành công | `push_send_accepted`, ID FCM thật, attempt/run/version | Chờ evidence phía app; không tự ghi received/applied |
| Validate local lỗi trước RPC | Send failure với `reason=local_validation`, message ID null | Sửa payload/cấu hình; không nói FCM đã nhận và từ chối |
| FCM trả `INVALID_ARGUMENT`, `UNREGISTERED`, `SENDER_ID_MISMATCH` | `push_send_rejected`, HTTP/FCM code và reason đã loại dữ liệu nhạy cảm | Sửa payload/project hoặc cập nhật token; không retry mù token đã unregistered |
| Auth/permission lỗi | Failure phân biệt credential local với response từ provider | Kiểm project/IAM/credential theo SEM-13, không đưa credential vào log |
| FCM trả `QUOTA_EXCEEDED`, `UNAVAILABLE`, `INTERNAL` | Rejected/failure cho attempt có response lỗi; giữ code, Retry-After khi có | Sender áp dụng retry hữu hạn, backoff/jitter và hướng dẫn từng mã; không tạo vòng lặp gửi vô hạn |
| Timeout/mất response sau khi gửi | Outcome **unknown** với `reason=response_not_observed`, ID null | Không khẳng định rejected hoặc chưa delivered; giữ attempt/signal để nhận diện trùng khi retry |
| Accepted nhưng chưa có callback | Accepted vẫn giữ; run timeout/không quan sát được nhận | Không tạo `push_received`, không tự gán lỗi delivery chỉ từ log thiếu |

Tên event/outcome bổ sung cho local failure và unknown là đề xuất, SEM-26 cần chuẩn hóa để parser không ép mọi lỗi thành rejected. Bảng lỗi dùng mã HTTP v1; SDK dùng các mã `messaging/...` và cần lưu đúng code thực nhận, không đổi tên tùy ý. Hướng xử lý cụ thể theo [FCM error codes](https://firebase.google.com/docs/cloud-messaging/error-codes). HTTP 404 ở root FCM không phải response `UNREGISTERED` của send API có xác thực.

## Bàn giao và giới hạn kiểm chứng

- **SEM-19 (Tuấn):** dùng luồng persist → FCM → callback → shared worker → Room, bảng event và khoảng chưa biết; không biến mô tả cơ chế thành kết quả đo.
- **SEM-35 (Tâm):** hiện thực sender, log accepted/rejected/unknown, TTL và IDs thật; nhận thêm đầu vào SEM-13/27, không gửi test khi thiếu quyền/cấu hình/token.
- **SEM-49 (Tâm):** dùng kiến trúc và lập luận accepted khác delivered; nội dung cuối phải khớp runtime được bàn giao sau này.
- **SEM-26 (Tâm):** đối chiếu các đề xuất signal/attempt và nullable correlation khi chốt schema; tài liệu này không tự thêm trường bắt buộc cho core của người khác.

Các ca thật gửi FCM, Android callback, worker, Room và Doze đều **Not run** trong SEM-18. Các blocker project/quyền/thiết bị đã ghi ở SEM-13 vẫn áp dụng; task này không cần gửi push thật để hoàn tất phần giải thích cơ chế. Xem [CHECKS SEM-18](../evidence/SEM-18/CHECKS.md) để phân biệt review tài liệu với chạy thực nghiệm. Đầu ra đang chờ nhóm trưởng review; chưa coi là bàn giao cuối để vượt gate task phụ thuộc.
