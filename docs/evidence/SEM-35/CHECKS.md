# SEM-35 — Kiểm tra và bàn giao FCM Sender CLI

## Nhận dạng lần kiểm

- **Thời điểm:** 31/10/2026 (UTC+7).
- **Task:** [SEM-35](../../../tasks/backlog/SEM-35.md).
- **Người thực hiện:** Tâm (`HoaiTam`) / Trí (`ThanhTris`).
- **Thành phần bàn giao:**
  - `server/bin/fcm-sender.js`: Công cụ CLI phát tín hiệu push FCM.
  - `docs/setup/FCM_SENDER.md`: Hướng dẫn vận hành.

## Tiêu chí và Kết quả

| Yêu cầu kiểm tra | Expected | Actual | Trạng thái |
|---|---|---|:---:|
| Cấu trúc Payload | Data-only (không có notification block) | JSON payload chỉ có key `data` và cấu hình `android.priority = normal` | Pass |
| Normal Priority | Giữ mức ưu tiên bình thường, không dùng high priority | `android.priority = "normal"` | Pass |
| TTL | 86400 giây (24 giờ) | `android.ttl = 86400` | Pass |
| Bảo vệ bảo mật (Security) | Không log hoặc commit credential/token lên kho mã nguồn | CLI che giấu token và đọc biến môi trường | Pass |
| Dry-run simulation | Chạy được mô phỏng khi chưa có project/credential thật | In payload và mã message giả lập hợp lệ | Pass |

## Bàn giao tiếp theo
- Cung cấp công cụ cho **SEM-34** (Chạy pilot push E02) và **SEM-36** (Tích hợp 3 mode).
