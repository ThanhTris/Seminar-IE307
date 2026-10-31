# SEM-26 — Kiểm tra và bàn giao hợp đồng API & Event Schema

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
