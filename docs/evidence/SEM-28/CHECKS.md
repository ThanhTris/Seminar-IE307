# SEM-28 — Kiểm tra và bàn giao Manual Sync đầu cuối

## Nhận dạng lần kiểm

- **Thời điểm:** 31/10/2026 (UTC+7).
- **Task:** [SEM-28](../../../tasks/backlog/SEM-28.md).
- **Người thực hiện:** Trí (`ThanhTris`).
- **Thành phần bàn giao:**
  - `docs/SETUP.md`: Hướng dẫn chạy trọn bộ Server và Android.
  - `docs/ENVIRONMENT.md`: Chỉ mục cấu hình môi trường toàn dự án.
  - `docs/evidence/SEM-28/M1.md`: Hồ sơ kiểm chứng cột mốc M1.
  - Mã nguồn tích hợp: `RealBulletinUiGateway.kt`, `AppContainer.kt`, `SeminarApp.kt`.

## Tiêu chí và Kết quả

| Yêu cầu kiểm tra | Expected | Actual | Trạng thái |
|---|---|---|:---:|
| Build debug Android | APK debug biên dịch thành công kèm Room và WorkManager | `:app:assembleDebug` tạo `app-debug.apk` (12.3 MB) | Pass |
| Unit tests Android | Không có regression test nào | `:app:testDebugUnitTest` 2/2 tests pass | Pass |
| Nối nút manual với SyncWorker | Bấm nút xếp lịch `OneTimeWorkRequest` và ghi nhận `work_enqueued` | `RealBulletinUiGateway.enqueueManual` gọi WorkManager và ghi event vào Room | Pass |
| Offline Persistence | Mở lại app hiển thị từ DB, không auto-fetch | `MainActivity` chỉ collect Flow từ Gateway | Pass |
| Chỉ mục môi trường và Setup | Tạo đủ `SETUP.md` và `ENVIRONMENT.md` | Đã tổng hợp đầy đủ các bước cho Server và Client | Pass |

## Bàn giao tiếp theo
- Cung cấp nền tảng hoạt động thực tế để bắt đầu **SEM-30** (Unique Periodic Work) và **SEM-32** (FCM Push Callback).
