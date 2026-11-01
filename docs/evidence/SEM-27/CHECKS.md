# SEM-27 — Kiểm tra và bàn giao Snapshot Server & Update CLI

## Nhận dạng lần kiểm

- **Thời điểm:** 31/10/2026 (UTC+7).
- **Task:** [SEM-27](../../../tasks/backlog/SEM-27.md).
- **Người thực hiện:** Tâm (`HoaiTam`) / Trí (`ThanhTris`).
- **Thành phần bàn giao:**
  - `server/package.json` & source code server (`server/src/server.js`, `server/src/snapshot_store.js`).
  - `server/bin/update-cli.js`: CLI phát hành bản tin mới và tăng version đơn điệu.
  - `server/test/server.test.js`: Bộ test tự động.
  - `docs/setup/SERVER.md`: Hướng dẫn cài đặt và khởi chạy.

## Lệnh và kết quả kiểm thử

Chạy từ thư mục `server/`:
```bash
npm test
```

| Kiểm tra | Expected | Actual | Trạng thái |
|---|---|---|:---:|
| Khởi tạo snapshot | Bắt đầu ở version ban đầu và lưu file JSON | Version 1 khởi tạo thành công tại `server/data/snapshot.json` | Pass |
| Tăng version đơn điệu | Update snapshot làm tăng version +1 | v1 -> v2 tăng chính xác, bảo toàn snapshot qua restart | Pass |
| Endpoint `/health` | Trả về 200 OK và uptime | `GET /health` trả về `{"status":"ok", ...}` | Pass |
| Endpoint `/api/bulletin` | Trả về 200 khi có tin mới, 304 khi gửi ETag trùng | Đạt 100%: 200 OK với body, 304 Not Modified khi gửi `If-None-Match: "v1"` | Pass |
| Unit tests | 3 passed, 0 failed | 3 passed trong 369ms | Pass |

## Bàn giao tiếp theo
- Cung cấp server cho **SEM-28** (Kiểm thử đầu cuối Manual Sync trên thiết bị).
- Cung cấp hạ tầng cho **SEM-35** (CLI gửi FCM push).
