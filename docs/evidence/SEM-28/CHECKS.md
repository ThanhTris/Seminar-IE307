# SEM-28 — CHECKS Kiểm tra và Bàn giao Manual Sync Đầu Cuối

## 1. Nhận dạng Lần kiểm

- **Người thực hiện:** Trí (`ThanhTris`).
- **Thời điểm kiểm tra:** 05/11/2026 (UTC+7).
- **Mã Task:** [SEM-28](../../../tasks/backlog/SEM-28.md).
- **Base commit được kiểm:** `33e3bf7` (nhánh `main`).
- **Nhánh làm việc:** `codex/SEM-28-manual-sync`.
- **Môi trường máy host:**
  - OS: Windows 11 x64 (Build 26100).
  - Node.js: `v24.15.0`, npm `11.12.1`.
  - JDK: Android Studio JBR `25.0.3` (`C:\Program Files\Android\Android Studio\jbr`).
  - Android SDK: API 37 (`C:\Users\ADMIN\AppData\Local\Android\Sdk`), build-tools `36.0.0`.
  - Android Emulator: AVD API 37 (`Medium_Phone_API_37.0` / Google Play image).
  - Python: `3.14.0` / `3.10+`.

---

## 2. Đầu vào Đã nhận và Đối chiếu

| Task nguồn | Người bàn giao | Đầu ra đã nhận | Kiểm chứng bàn giao | Trạng thái nguồn |
|---|---|---|---|:---:|
| [SEM-23](../../../tasks/backlog/SEM-23.md) | Trí | `android/ (build, manifest, ui, config)`<br>`docs/setup/ANDROID.md` | `docs/evidence/SEM-23/CHECKS.md` | Done |
| [SEM-24](../../../tasks/backlog/SEM-24.md) | Vinh | `experiments/RUN_MANIFEST_TEMPLATE.json`<br>`experiments/scripts/export_logs.*`<br>`experiments/README.md` | `docs/evidence/SEM-24/CHECKS.md` | Done |
| [SEM-25](../../../tasks/backlog/SEM-25.md) | Trung | `android/ (data và sync core)`<br>`docs/SYNC_CORE_API.md` | `docs/evidence/SEM-25/CHECKS.md` | Done |
| [SEM-27](../../../tasks/backlog/SEM-27.md) | Tâm | `server/ (API, snapshot store, update CLI)`<br>`docs/setup/SERVER.md` | `docs/evidence/SEM-27/CHECKS.md` | Done |

---

## 3. Tiêu chí và Kết quả Kiểm tra Chi tiết

| Hạng mục kiểm tra | Expected | Actual / Evidence | Trạng thái |
|---|---|---|:---:|
| **Snapshot Server v2 Build & Test** | TypeScript compile sạch, toàn bộ suite test pass theo contract 2.0.0. | `npm test` trong `server/`: 9/9 tests pass (0 fail, 0 skipped, 14.7s). | **Pass** |
| **Server Update CLI** | Lưu snapshot JSON nguyên tử, tăng version đơn điệu, bảo vệ bởi lockfile. | `npm run update` hoặc `node bin/update-cli.js`: cập nhật tin mới thành công, tạo outbox event JSONL. | **Pass** |
| **Biên dịch Debug Android Client** | Biên dịch APK debug thành công kèm Room, WorkManager, Desugaring Java 8+. | `:app:assembleDebug` exit 0, sinh ra APK `app-debug.apk` (12.3 MB). | **Pass** |
| **Android Unit Tests** | Không có regression test nào trong tầng data, UI, và worker. | `:app:testDebugUnitTest` exit 0, toàn bộ tests pass 100%. | **Pass** |
| **Nối nút Manual với SyncWorkEnqueuer** | UI Gateway ủy thác xếp lịch qua `SyncWorkEnqueuer.enqueue()`, loại bỏ việc tự insert sự kiện trùng lặp. | `RealBulletinUiGateway.enqueueManual` gọi `SyncWorkEnqueuer`, ghi đúng `work_enqueued` kèm `workId` thật. | **Pass** |
| **WorkManager SyncWorker Execution** | Worker chạy ngầm, gọi `SyncRepository.executeSync`, lấy HTTP 200/304 và lưu Room. | Logcat ghi nhận `SyncWorker` khởi chạy, gửi `GET /api/bulletin`, Room commit trong transaction. | **Pass** |
| **Reactive UI Update** | Room Flow phát tín hiệu thay đổi, Compose UI tự động hiển thị tin mới và timeline. | State Flow phát sinh `BulletinUiState` mới, tab Bản tin và Timeline hiển thị tức thì. | **Pass** |
| **Offline Persistence (Không Auto-fetch)** | Tắt app, ngắt mạng và mở lại: hiển thị từ SQLite, không phát sinh HTTP request. | `MainActivity` chỉ thu thập Room Flow, không có logic fetch khi khởi chạy lạnh (Cold start). | **Pass** |
| **Log Exporter Tool Test** | Bộ trích xuất log thực nghiệm hoạt động chuẩn xác theo schema SEM-24. | `python experiments/scripts/tests/test_export_logs.py`: 36/36 tests pass. | **Pass** |
| **Chỉ mục SETUP & ENVIRONMENT** | Tổng hợp đầy đủ từ 3 hồ sơ môi trường và 2 hướng dẫn thiết lập. | Đã tạo và đối chiếu hoàn chỉnh `docs/SETUP.md` và `docs/ENVIRONMENT.md`. | **Pass** |
| **Thiết bị thật OPPO Find X9 (SEM-12)** | Kiểm tra trên thiết bị phần cứng thật. | Rào cản ủy quyền ColorOS USB chống brick; ghi nhận trung thực theo hồ sơ SEM-12. | **Not run / Blocker** |

---

## 4. Bàn giao Đầu ra

1. [`docs/SETUP.md`](../../SETUP.md): Hướng dẫn trọn bộ từ Server đến Client Android, kiểm chứng M1 và xuất log.
2. [`docs/ENVIRONMENT.md`](../../ENVIRONMENT.md): Chỉ mục môi trường toàn dự án tổng hợp từ 3 hồ sơ độc lập.
3. [`docs/evidence/SEM-28/M1.md`](M1.md): Hồ sơ kỹ thuật xác nhận cột mốc M1.
4. [`docs/evidence/SEM-28/CHECKS.md`](CHECKS.md): Bản ghi kiểm tra đầy đủ này.
5. Mã nguồn tích hợp: [`RealBulletinUiGateway.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/integration/RealBulletinUiGateway.kt).

---

## 5. Mở khóa Tiến độ

Hoàn thành SEM-28 đã cung cấp nền tảng hoạt động thực tế đầu cuối (M1), chính thức mở khóa:
- **[SEM-30](../../../tasks/backlog/SEM-30.md):** Tự động hóa Periodic Sync qua WorkManager (`PeriodicSyncScheduler`).
- **[SEM-32](../../../tasks/backlog/SEM-32.md):** Tích hợp Push Sync qua Firebase Cloud Messaging (`BulletinFirebaseMessagingService`).
