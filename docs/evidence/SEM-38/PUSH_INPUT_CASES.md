# SEM-38 — Ca đầu vào push: duplicate / hint cũ / tín hiệu mới khi worker chạy

- **Revision:** base `origin/main` `abcfc89` + nhánh `codex/SEM-38-push-input-policy` (xem commit trong [CHECKS](CHECKS.md)).
- **Phạm vi:** phía messaging ([`PushSyncEnqueueAdapter`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushSyncEnqueueAdapter.kt), [`PushInputPolicy`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushInputPolicy.kt)). Không sửa `SyncRepository`, transaction hay version guard của core ([SEM-39](../SEM-39/CORE_CASES.md)).
- **Test:** [`PushInputPolicyTest`](../../../android/app/src/test/java/com/thanhtris/seminarie307/fcm/PushInputPolicyTest.kt) — fake DAO và enqueue giả lập, **không phải** FCM/WorkManager/thiết bị thật. Cột Actual ghi trạng thái chạy thật của từng ca (unit test JVM với JUnit 4.13.2 pass; chạy thiết bị E05 là **Not run**).

## Chính sách

| Quy tắc | Lý do |
|---|---|
| Chỉ coi là duplicate khi **cùng `run_id`** và (cùng `signal_id` **hoặc** cùng FCM `message_id`) đã được enqueue thành công trước đó. Ghi `push_received` (callback có thật), sau đó `trigger_rejected` / reason `DUPLICATE_SIGNAL`, không enqueue lần hai. | Sender giữ `signal_id` khi retry ([FCM_SENDER.md](../../setup/FCM_SENDER.md)); FCM có thể giao lại cùng message. Protocol E05-A. |
| **Không** bỏ tín hiệu vì `version_hint` cũ/bằng/thấp hơn cache. Vẫn enqueue, hint chỉ là correlation. | `version_hint` chỉ là gợi ý; worker phải GET snapshot hiện hành, version guard của core quyết định ([EVENT_SCHEMA](../../EVENT_SCHEMA.md) mục 87, protocol E05-B). Hint cũ có thể đi cùng server V+1. |
| Tín hiệu có `signal_id`/`message_id` chưa từng thấy luôn được enqueue, kể cả khi work trước đang chạy/chờ. | Không để mất bản mới (E05-C, EVENT_SCHEMA mục 84: không giả định `KEEP` đủ an toàn). Hai worker chạy song song vẫn an toàn nhờ guard trong transaction của core. |
| Chỉ ghi nhớ key **sau khi enqueue thành công**; ledger tối đa 64 key mới nhất, lưu Room `sync_metadata[pushSeenSignalKeys]` (sống qua process death). | Enqueue lỗi thì sender retry cùng `signal_id` vẫn được xử lý. |
| `signal_id` sai định dạng, hoặc không có cả `signal_id` lẫn `message_id` hợp lệ → không thể dedupe, vẫn enqueue. | Không đoán danh tính tín hiệu. |
| Rejection do `MODE_DISABLED` không tiêu thụ key. | Đổi sang mode cho phép rồi gửi lại cùng tín hiệu vẫn chạy. |
| Khóa tuần tự (`Mutex`) quanh "kiểm ledger → enqueue → ghi ledger". | Hai callback trùng đồng thời không cùng enqueue. Tín hiệu khác chỉ chờ bước enqueue ngắn, không chờ worker. |

## Ca kiểm

| # | Ca | Input | Expected | Test | Actual |
|---|---|---|---|---|---|
| A1 | Duplicate cùng `signal_id`, khác FCM message | `sig-1` (m-1) rồi `sig-1` (m-2), hint 6 | 1 enqueue; events `push_received`×2 + `trigger_rejected` `DUPLICATE_SIGNAL` (messageId m-2, version 6); kết quả `Rejected(DUPLICATE_SIGNAL)` | `sameSignalIdWithDifferentFcmMessageIdIsNotEnqueuedTwice` | Pass (unit test JVM — fake DAO); E05 thiết bị: Not run |
| A2 | Redelivery cùng message_id, không có signal_id | cùng `projects/p/messages/abc` hai lần | 1 enqueue | `sameFcmMessageIdWithoutSignalIdIsRecognisedAsRedelivery` | Pass (unit test JVM — fake DAO); E05 thiết bị: Not run |
| A3 | Duplicate sau khi process restart | adapter mới, cùng Room | Vẫn nhận ra duplicate | `duplicateIsRecognisedByNewAdapterInstanceBecauseLedgerIsPersisted` | Pass (unit test JVM — fake DAO); E05 thiết bị: Not run |
| A4 | Cùng `signal_id`, khác run | run-a và run-b | Cả hai được enqueue | `sameSignalIdInAnotherRunIsNotADuplicate` | Pass (unit test JVM — fake DAO) |
| A5 | 4 callback trùng đồng thời | cùng `signal_id`, enqueue chậm 50 ms | Đúng 1 `Enqueued`, 3 `DUPLICATE_SIGNAL` | `concurrentRedeliveryEnqueuesOnlyOnce` | Pass (unit test JVM — fake DAO) |
| A6 | Enqueue lỗi (null/exception) rồi retry cùng `signal_id` | — | Lần retry được enqueue | `failedEnqueueIsNotRemembered…`, `enqueueExceptionIsNotRemembered` | Pass (unit test JVM — fake DAO) |
| A7 | Mode disabled không tiêu thụ tín hiệu | PERIODIC → PUSH, cùng `signal_id` | Lần sau được enqueue | `modeDisabledRejectionDoesNotConsumeTheSignal` | Pass (unit test JVM — fake DAO) |
| A8 | Không có id dùng được | không signal/message, hoặc `signal_id` sai | Không bị bỏ, ledger không đổi | `signalsWithoutUsableIdsCannotBeDeduplicatedAndAreNotDropped` | Pass (unit test JVM — fake DAO) |
| A9 | Duplicate không phát sinh đường khác | — | Chỉ có event `push_received`/`trigger_rejected`, không notification, không engine riêng (chỉ lambda enqueue chung) | `duplicateNeverCreatesNotificationOrSecondEnginePath` | Pass (unit test JVM — fake DAO) |
| B1 | Hint cũ/bằng cache | cache 5; hint 3 và 5, signal mới | Cả hai `Enqueued`, `versionHint` giữ nguyên, không `trigger_rejected` | `hintOlderOrEqualToCacheIsStillEnqueued…` | Pass (unit test JVM — fake DAO); E05 thiết bị: Not run |
| B2 | Hint lặp, signal mới | hint 6 hai lần, `sig-1`/`sig-2` | Cả hai `Enqueued` | `repeatedHintWithNewSignalIdIsEnqueued` | Pass (unit test JVM — fake DAO) |
| C1 | Bản mới khi work trước còn chạy/chờ | hint 6 rồi hint 7, signal khác nhau | 2 enqueue, workId khác nhau, thứ tự 6→7 | `newerSignalWhileEarlierWorkIsPendingIsEnqueuedNotSkipped` | Pass (unit test JVM — fake DAO); E05-C race thật: Not run |
| P1 | Ledger | thêm 74 key | Giữ 64 mới nhất, không trùng key | `ledgerIsCappedToNewestEntriesAndKeepsKeysUnique` | Pass (unit test JVM) |
| P2 | Key | run-scope, id không hợp lệ | Chỉ id hợp lệ tạo key | `keysUseRunScopeAndOnlyUsableIds` | Pass (unit test JVM) |

## Giới hạn và chuyển giao

- **Không chứng minh được** race thật ở C1: adapter không biết worker đang chạy hay xong; test chỉ chứng minh tín hiệu mới không bị loại ở lớp messaging. Overlap thật (barrier/hook `INJECTED`, cache đến V+2) thuộc E05-C và test core [SEM-39](../SEM-39/CORE_CASES.md); lỗi version guard/transaction chuyển SEM-39.
- Evidence thiết bị cần log Android có `signal_ids`. `TimelineEventEntity` hiện **chưa có cột signal id**, nên event `push_received`/`trigger_rejected` chưa mang `signal_id` (schema yêu cầu một signal cho `push_received`). Đây là phần core/Room ngoài phạm vi SEM-38; cần chủ sở hữu core thêm trường (đổi schema Room) hoặc exporter nối theo `message_id`. Chưa sửa để không đổi schema Room.
- Duplicate giữa hai callback chỉ tạo `DUPLICATE_SIGNAL` khi lần đầu **đã enqueue thành công**; nếu work đó sau này thất bại cuối cùng (`sync_failed`/`RETRY_EXHAUSTED`) thì push cùng `signal_id` đến sau vẫn bị coi là duplicate. Retry thuộc WorkManager/core; muốn gửi lại sau thất bại hãy tạo `signal_id` mới.
- Ledger chỉ giữ 64 key mới nhất; duplicate quá xa (sau >64 tín hiệu) sẽ không nhận ra. Chấp nhận trong phạm vi E05 (vài tín hiệu mỗi run).
- `DUPLICATE_SIGNAL` là reason mới, đã thêm vào registry [EVENT_SCHEMA](../../EVENT_SCHEMA.md) như delta; exporter SEM-24 chỉ kiểm regex `^[A-Z][A-Z0-9_]{0,63}$` nên chấp nhận.
