# SEM-30 — Kiểm tra và bàn giao Unique Periodic Work

## Nhận dạng lần kiểm

- **Thời điểm:** 31/10/2026 (UTC+7).
- **Task:** [SEM-30](../../../tasks/backlog/SEM-30.md).
- **Người thực hiện:** Trung (`TrungNQ2645`) / Trí (`ThanhTris`).
- **Thành phần bàn giao:**
  - `PeriodicSyncScheduler.kt`: Lớp quản lý lịch lặp duy nhất (`enqueueUniquePeriodicWork`).
  - Tái sử dụng `SyncWorker` chung với nguồn `SyncSource.PERIODIC`.
  - Hỗ trợ bật/tắt/truy vấn trạng thái lịch lặp.

## Tiêu chí và Kết quả

| Yêu cầu kiểm tra | Expected | Actual | Trạng thái |
|---|---|---|:---:|
| Unique work registration | Đăng ký lặp duy nhất theo tên `periodic_bulletin_sync` | Dùng `ExistingPeriodicWorkPolicy.UPDATE` | Pass |
| Ràng buộc mạng (Network Constraints) | Chỉ chạy khi có mạng (`NetworkType.CONNECTED`) | Đã cấu hình qua `Constraints.Builder` | Pass |
| Không tạo sync engine riêng | Tái sử dụng `SyncWorker` và `SyncRepository` | Chạy cùng logic Version Guard và ghi Room DB | Pass |
| Thao tác hủy lịch | Tắt periodic hủy work duy nhất, không để lịch cũ sót lại | `cancelPeriodicSync()` gọi `cancelUniqueWork` và ghi event timeline | Pass |

## Bàn giao tiếp theo
- Cung cấp thành phần cho **SEM-29** (Chạy pilot periodic E01 trên thiết bị) và **SEM-36** (Tích hợp 3 mode).
