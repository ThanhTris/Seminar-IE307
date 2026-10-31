# SEM-32 — Kiểm tra và bàn giao FCM Callback & Enqueue Sync

## Nhận dạng lần kiểm

- **Thời điểm:** 31/10/2026 (UTC+7).
- **Task:** [SEM-32](../../../tasks/backlog/SEM-32.md).
- **Người thực hiện:** Trang (`rosy179`) / Trí (`ThanhTris`).
- **Thành phần bàn giao:**
  - `BulletinFirebaseMessagingService.kt`: Xử lý callback FCM push data-only.
  - Khai báo service trong `AndroidManifest.xml`.
  - Enqueue `SyncWorker` chung với nguồn `SyncSource.PUSH`.

## Tiêu chí và Kết quả

| Yêu cầu kiểm tra | Expected | Actual | Trạng thái |
|---|---|---|:---:|
| Ghi nhận sự kiện tức thì | Ghi `push_received` ngay khi nhận callback vào Room DB | Ghi nhận timestamp epoch millis và UTC, `messageId`, `requestId` | Pass |
| Không đồng bộ dài trong callback | Không thực hiện network call dài trong `onMessageReceived` | Đẩy công việc vào `OneTimeWorkRequestBuilder<SyncWorker>` | Pass |
| Correlation IDs | Chuyển tiếp `run_id`, `version_hint`, `request_id`, `message_id` vào worker | Bọc vào `inputData` gửi cho `SyncWorker` | Pass |
| Token refresh | `onNewToken` lưu token vào `SyncMetadataEntity` | Đã hiện thực và lưu vào Room | Pass |

## Bàn giao tiếp theo
- Cung cấp thành phần cho **SEM-33** (Token refresh) và **SEM-34** (Pilot push E02).
