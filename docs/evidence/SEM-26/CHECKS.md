# SEM-26 — Kiểm tra và bàn giao hợp đồng API & Event Schema

> Phần ngay dưới đây là hồ sơ có sẵn trên `main` tại commit nền `68db745`, ghi lại bản nháp 31/10. Giữ nguyên để truy vết; lần rà soát của Tâm ngày 02/11 và giới hạn kiểm chứng được ghi riêng ở cuối file.

## Nhận dạng lần kiểm

- **Thời điểm:** 31/10/2026 (UTC+7).
- **Task:** [SEM-26](../../../tasks/backlog/SEM-26.md).
- **Người thực hiện:** Tâm (`HoaiTam`) / Trí (`ThanhTris`).
- **Tài liệu bàn giao:**
  - `docs/API.md`: Hợp đồng API HTTP snapshot (`GET /api/bulletin`, `GET /health`, `POST /api/bulletin/update`).
  - `docs/EVENT_SCHEMA.md`: Cấu trúc JSON chuẩn hóa các sự kiện timeline và correlation IDs.

## Tiêu chí và Kết quả

| Yêu cầu kiểm tra | Expected | Actual | Trạng thái |
|---|---|---|:---:|
| Định dạng endpoint snapshot | GET /api/bulletin hỗ trợ If-None-Match, ETag và since_version | Đã đặc tả chi tiết trong `docs/API.md`, mã 200 khi có tin mới, 304 khi không đổi | Pass |
| Quy chuẩn sự kiện timeline | Phân tách riêng biệt: `accepted`, `received`, `started`, `applied`, `unchanged`, `stale`, `failed` | Đã chuẩn hóa 7 loại sự kiện trong `docs/EVENT_SCHEMA.md` | Pass |
| Correlation IDs | Hỗ trợ 3 mã định danh: `requestId`, `workId`, `messageId` | Đã quy định rõ cấu trúc correlation object | Pass |
| Mã lỗi thống nhất | Trả về JSON `{ error: { code, message } }` | Đã định nghĩa chuẩn mã lỗi trong API.md | Pass |
| Loại bỏ token/secret | Không để lộ private token/key trong tài liệu | Đã rà quét, không có credential nào | Pass |

## Bàn giao tiếp theo
- Cung cấp đầu vào cho **SEM-25** (Xây Room, Repository và Worker trên Android).
- Cung cấp đầu vào cho **SEM-27** (Triển khai Server và update CLI).

## Rà soát và bàn giao SEM-26 ngày 02/11/2026

- **Người thực hiện lần này:** Tâm (`HoaiTam`). Hạn được giao: 30/10/2026 17:00 UTC+7; không ghi lùi thời điểm.
- **Base:** `68db745def039d2277640c560b9b1e4e28ed3c92` (`origin/main`, đã fetch); nhánh `codex/SEM-26-api-event-schema`.
- **Đầu vào đã nhận:** SEM-11 — [phạm vi](../../SCOPE.md), [Android build](../../environment/ANDROID_BUILD.md), [CHECKS](../SEM-11/CHECKS.md), artifact commit `7b502c0`; SEM-13 — [server/Firebase](../../environment/SERVER_FIREBASE.md), [CHECKS](../SEM-13/CHECKS.md), artifact `b9da9a0`; SEM-14 — [shared sync](../../mechanisms/SHARED_SYNC.md), [CHECKS](../SEM-14/CHECKS.md), artifact `3bf7dcf`. Các task nguồn đều Done trên Project khi bắt đầu.
- **Nguồn bổ sung:** [SEM-18](../../mechanisms/SERVER_FCM.md), artifact `22c393f`; [protocol](../../EXPERIMENT_PROTOCOL.md); baseline server/Android thực tế trên main. SEM-18 không phải gate bắt đầu của SEM-26.
- **Đầu ra:** [API.md](../../API.md), [EVENT_SCHEMA.md](../../EVENT_SCHEMA.md), CHECKS này và [validate_fixtures.py](validate_fixtures.py). Contract `2.0.0` là **đề xuất chờ review**, không khẳng định code đã tuân thủ.

### Soát tiêu chí và kiểm tra

| Check | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| Endpoint và response | Health, GET, update, JSON, status/error đủ rõ để client/server triển khai | API quy định đường dẫn, request/response, validation, ETag/304, error envelope, retry và response version; giữ đường dẫn update đã có | Pass — đặc tả |
| Version/restart/race | Version không lùi, replay không nhân đôi, event nhất quán | API quy định store rỗng v0, append, version item, transaction state/ledger/event, outbox, replay và khóa serialized; phân biệt snapshot version với item version | Pass — đặc tả, chưa chạy server v2 |
| Room và snapshot rỗng | Không mất version khi không có item; equal/stale phân biệt | API yêu cầu metadata version độc lập, re-read trong transaction; 200 bằng cache là unchanged, thấp hơn là stale, 304 không tự áp dụng | Pass — đặc tả, chưa chạy Android v2 |
| Event/correlation | Tách accepted/received/started/applied; đủ nullable, UTC/monotonic và outcome/reason | Schema định nghĩa key, kiểu, origin/source, từng event, signal/attempt/request/work/fetch IDs, clock/boot và các giá trị null; ID FCM chỉ nhận khi được cấp | Pass — đặc tả |
| JSON/JSONL fixture | Ví dụ parse được và không mâu thuẫn với nhau | `python3 docs/evidence/SEM-26/validate_fixtures.py`: 5 JSON API, 4 JSONL events, nối run/signal/request/version; phát hiện 3 snapshot và 4 event fixture sai, cùng duplicate JSON key | Pass — fixture offline |
| Phiên bản | Không ghi đè lặng lẽ baseline cũ | API/event ghi delta `1.0.0 → 2.0.0`, các thay đổi không tương thích, migration và consumer/run ảnh hưởng. Bản `1.0.0` đã có trong commit `5e7eb82` dù SEM-26 còn Todo | Pass — tài liệu, chờ nhóm trưởng review |
| Nguồn và cơ chế | HTTP conditional, JSON integer và timestamp có cơ sở; FCM outcome đúng | Đối chiếu RFC 9110/8259/3339; tham khảo SEM-18 đã đối chiếu Firebase. Không gửi request đến FCM hoặc thay payload API Firebase | Pass — đối chiếu tài liệu |
| Link/secret/diff | Link nội bộ tồn tại, không commit secret, whitespace sạch | Quét hai contract, CHECKS và script: 32 link nội bộ tồn tại; newline, fence, credential patterns và `git diff --cached --check` đều đạt | Pass — kiểm file |
| Runtime contract 2.0.0 | Chỉ báo Pass nếu các consumer thật chạy đúng | Server và Android scaffold trên base chưa tuân thủ đầy đủ v2; không build app, không khởi chạy server hay test FCM/device trong SEM-26 | **Not run** |

Lệnh tái lập kiểm fixture (Python 3.10+, không dùng `python -O` vì script dùng assertions):

```sh
python3 docs/evidence/SEM-26/validate_fixtures.py
git diff --cached --check
```

Script chỉ kiểm ví dụ và correlation được nêu, **không phải validator đầy đủ hoặc bộ test implementation**. Fixture ID/UTC/message ID là giả lập có nhãn; không coi là kết quả đo hoặc FCM đã trả ID thật.

### Tình huống đã soát trong contract

| Tình huống | Quy định cần implementation chứng minh sau review | Kiểm tra |
|---|---|---|
| Khởi tạo version 0, snapshot rỗng; mở app lại | Lưu metadata version độc lập với items; không ghi lặp vì cache rỗng | Pass — review contract |
| GET có ETag bằng, cũ hơn hoặc lớn hơn version server | 304 chỉ khi validator khớp; không khớp trả 200 để version guard phát hiện stale | Pass — review contract |
| GET 304 nhưng cache tương ứng không còn | GET lại không điều kiện; không ghi applied từ 304 | Pass — review contract |
| Hai update ID khác nhau cùng lúc | Tuần tự hóa và cấp hai version khác nhau; snapshot/event nhất quán | Pass — review contract |
| Response POST bị mất sau commit và retry cùng update ID | Replay trả response cũ, không tăng version hay tạo event update thứ hai; vẫn replay được khi store đầy | Pass — review contract |
| Một update ID dùng hai payload khác nhau | 409, không thay đổi store | Pass — review contract |
| Crash giữa commit và export event | State/ledger/outbox commit chung; export lại cùng event ID, consumer deduplicate | Pass — review contract |
| FCM accepted nhưng chưa có callback; timeout mất response | Không suy delivered; timeout send là unknown, không bịa message ID | Pass — review contract |
| Push trùng/coalesce hoặc hint cũ | Giữ signal IDs, logical request IDs và GET thật; version guard không giảm cache | Pass — review contract |
| Malformed response, lỗi mạng, retry hết hạn | Invalid contract là failure; lỗi mạng/408/429/5xx retry hữu hạn, hết lượt ghi failure | Pass — review contract |

### Khác biệt đã thấy trong code trên main — cần task sở hữu xử lý

Đây là đối chiếu tĩnh trên base `68db745`, không khẳng định đã tái hiện runtime; SEM-26 không sửa code của task khác:

- [Server GET](../../../server/src/server.js) hiện trả 304 khi version client `>=` server, thay vì chỉ validator khớp; [store](../../../server/src/snapshot_store.js) có fallback snapshot mặc định khi đọc lỗi. Chưa có ledger/outbox/idempotency theo v2. SEM-27 cần xử lý và kiểm lại restart/race; CLI hiện còn fallback ghi thẳng file khi HTTP lỗi tại [update-cli.js](../../../server/bin/update-cli.js).
- [Android repository](../../../android/app/src/main/java/com/thanhtris/seminarie307/sync/SyncRepository.kt) hiện lấy version từ `MAX(item.version)` và gộp response version bằng vào stale; [remote datasource](../../../android/app/src/main/java/com/thanhtris/seminarie307/data/remote/SnapshotRemoteDataSource.kt) bắt mọi exception là transient. SEM-25/39 cần ánh xạ schema v2, version rỗng, equal/stale và lỗi parse theo contract.
- [FCM service](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/BulletinFirebaseMessagingService.kt) hiện fallback `run_id`, ghi `work_enqueued` trước khi gọi enqueue, và `onNewToken` ghi token vào Logcat. SEM-32/33/38 cần đối chiếu callback/schema, loại việc ghi token và xác nhận enqueue trước khi dùng log làm evidence. Không có token thật được ghi vào tài liệu này.

### Workflow và bàn giao

SEM-26 đã bắt đầu trên nhánh riêng; sau khi hoàn tất kiểm tra, chuyển **Review** và đồng bộ snapshot theo script của repo. Theo yêu cầu HoaiTam, nhóm trưởng `ThanhTris` kiểm nhận và quyết định merge/Done. Không tự merge, không tự đánh dấu Done; chỉ sửa tiếp khi có comment yêu cầu fix từ nhóm trưởng.

- **SEM-24:** event keys, nullability và manifest cho exporter; đầu vào SEM-12 vẫn cần nhận riêng.
- **SEM-25:** endpoint/ETag, version guard, metadata snapshot rỗng, canonical JSONL và các khác biệt Android nêu trên.
- **SEM-27:** contract HTTP, idempotency/outbox, xử lý store lỗi và migration baseline v1/v2.
- **SEM-45:** parse schema version, correlation, timeout và mốc tách biệt; không trộn fixture vào tập main.

Firebase project/quyền/thiết bị vẫn chưa được kiểm trong lần này; hồ sơ SEM-13 ghi blocker tại thời điểm audit. Các đầu ra chờ nhóm trưởng review; các task phụ thuộc vẫn phải tuân thủ gate và nhận artifact/commit/CHECKS được chấp thuận.
