# SEM-25 — Kiểm tra và bàn giao Data Layer & Sync Core

## Nhận dạng lần kiểm

- **Thời điểm:** 31/10/2026 (UTC+7).
- **Task:** [SEM-25](../../../tasks/backlog/SEM-25.md).
- **Người thực hiện:** Trung (`TrungNQ2645`) / Trí (`ThanhTris`).
- **Môi trường:** Android SDK API 37, Gradle 9.6.0, JBR 25.0.3, KSP 2.3.12, Room 2.8.5, WorkManager 2.12.0.
- **Thành phần bàn giao:**
  - Cơ sở dữ liệu Room: `AppDatabase`, `BulletinEntity`, `TimelineEventEntity`, `SyncMetadataEntity`.
  - Room DAOs: `BulletinDao`, `TimelineDao`, `SyncMetadataDao`.
  - Remote Data Source: `SnapshotRemoteDataSource` (HTTP 200/304, ETag).
  - Sync Core: `SyncRepository` (Version Guard, Room transaction), `SyncWorker` (`CoroutineWorker`).
  - Giao diện UI Gateway: `RealBulletinUiGateway` (kết nối Room Flow với UI Compose).
  - Tài liệu: `docs/SYNC_CORE_API.md`.

## Tiêu chí và Kết quả

| Yêu cầu kiểm tra | Expected | Actual | Trạng thái |
|---|---|---|:---:|
| Room schema & Entity | Tạo đủ 3 bảng: bản tin, sự kiện timeline, metadata | Entities và DAOs được biên dịch thành công qua KSP | Pass |
| Version Guard | Chỉ áp dụng snapshot khi `version_server > version_local` | Được kiểm tra và bảo vệ trong transaction `database.withTransaction` của Room | Pass |
| Cơ chế HTTP 304 | Khi server báo 304 Not Modified thì không xóa cache, ghi nhận sự kiện `snapshot_unchanged` | `RemoteSnapshotResult.NotModified` cập nhật `lastSyncAtUtc` và ghi nhận event `snapshot_unchanged` | Pass |
| Correlation Tracking | Giữ nguyên `run_id`, `request_id`, `work_id`, `message_id` trong timeline | `TimelineEventEntity` lưu trữ đầy đủ bộ correlation IDs | Pass |
| UI Gateway kết nối | `RealBulletinUiGateway` phát Flow dữ liệu sống từ Room | UI tự cập nhật khi Room thay đổi; manual enqueue qua WorkManager | Pass |
| Biên dịch và Test | `:app:assembleDebug` và `:app:testDebugUnitTest` thành công | Đạt (Pass) | Pass |

## Bàn giao tiếp theo
- Cung cấp toàn bộ Data Layer & Worker cho **SEM-28** (Ghép nối Manual Sync đầu cuối - Mốc M1).
- Cung cấp Worker cho **SEM-30** (Periodic WorkManager) và **SEM-32** (Firebase Cloud Messaging push callback).
