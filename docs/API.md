# Hợp đồng API Snapshot Bảng tin — SEM-26

Tài liệu này đặc tả giao thức giao tiếp HTTP giữa ứng dụng Android và Snapshot Server trong khuôn khổ đề tài Seminar IE307 (Cơ chế đồng bộ dữ liệu: Periodic, Push, Hybrid).

- **Phiên bản hợp đồng:** `1.0.0`
- **Giao thức:** HTTP/1.1 hoặc HTTP/2 qua TCP
- **Định dạng dữ liệu:** JSON (`application/json; charset=utf-8`)
- **Mã hóa thời gian:** ISO 8601 UTC string kết thúc bằng `Z` (ví dụ `2026-10-31T17:00:00Z`)

---

## 1. Địa chỉ máy chủ (Base URLs)

| Môi trường | Base URL | Ghi chú |
|---|---|---|
| Host cục bộ (Node.js) | `http://127.0.0.1:3000` | Kiểm tra trực tiếp trên máy host |
| Android Emulator (AVD) | `http://10.0.2.2:3000` | Loopback ảo chuẩn của Android Emulator |
| Thiết bị thật qua ADB Reverse | `http://127.0.0.1:3000` | Sau khi chạy lệnh `adb reverse tcp:3000 tcp:3000` |
| Thiết bị thật qua LAN Wi-Fi | `http://<IP_MAY_HOST>:3000` | Yêu cầu mở tường lửa cổng 3000 |

---

## 2. Danh sách Endpoints

### 2.1. Kiểm tra trạng thái máy chủ (`GET /health`)

Kiểm tra server đang chạy và sẵn sàng nhận kết nối.

- **Method:** `GET`
- **Path:** `/health`
- **Headers:** Không yêu cầu
- **Response Headers:** `Content-Type: application/json`
- **Response Status:** `200 OK`
- **Response Body:**
  ```json
  {
    "status": "ok",
    "uptime_seconds": 3600.25,
    "server_time_utc": "2026-10-31T17:00:00Z"
  }
  ```

---

### 2.2. Lấy dữ liệu snapshot (`GET /api/bulletin`)

Endpoint chính để Android Client lấy dữ liệu bảng tin. Hỗ trợ kiểm tra version có điều kiện để tiết kiệm băng thông và tài nguyên.

- **Method:** `GET`
- **Path:** `/api/bulletin`
- **Headers yêu cầu / tùy chọn:**
  - `If-None-Match` *(tùy chọn)*: Phiên bản cache hiện tại của client dưới dạng `"v<version>"` hoặc `"<version>"` (ví dụ: `"42"` hoặc `"v42"`).
  - `X-Correlation-Request-Id` *(tùy chọn)*: Mã `request_id` do client sinh ra để theo dõi xuyên suốt (server sẽ echo lại header này).
- **Query Parameters (tùy chọn thay thế cho Header):**
  - `since_version` *(integer)*: Lấy snapshot nếu version server lớn hơn `since_version`.

#### Phản hồi khi có dữ liệu mới (`200 OK`):
Trả về khi client chưa có cache, hoặc version của server lớn hơn version client gửi lên.
- **Status:** `200 OK`
- **Response Headers:**
  - `Content-Type: application/json`
  - `ETag: "v<version>"`
  - `X-Correlation-Request-Id: <request_id_nếu_có>`
- **Response Body:**
  ```json
  {
    "version": 42,
    "last_modified_utc": "2026-10-31T17:00:00Z",
    "items": [
      {
        "id": "bulletin-1",
        "title": "Thông báo seminar IE307",
        "body": "Đã triển khai kiến trúc đồng bộ dữ liệu.",
        "version": 42
      }
    ]
  }
  ```

#### Phản hồi khi dữ liệu không đổi (`304 Not Modified`):
Trả về khi version của client gửi lên bằng đúng version hiện tại trên server. Client không cần tải lại danh sách tin.
- **Status:** `304 Not Modified`
- **Response Headers:**
  - `ETag: "v<version>"`
  - `X-Correlation-Request-Id: <request_id_nếu_có>`
- **Response Body:** Rỗng (Không có payload).

---

### 2.3. Cập nhật bản tin mới (`POST /api/bulletin/update`)

Dành cho CLI `update-cli` hoặc script thử nghiệm để đẩy nội dung mới lên server.

- **Method:** `POST`
- **Path:** `/api/bulletin/update`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "title": "Tiêu đề bản tin mới",
    "body": "Nội dung cập nhật mới",
    "run_id": "run-test-01"
  }
  ```
- **Xử lý:**
  - Server tự động gán ID duy nhất cho tin mới.
  - Server tự động **tăng version lên +1 đơn điệu**.
  - Server lưu snapshot vào file JSON bền vững (`bulletin_snapshot.json`).
- **Response Status:** `200 OK`
- **Response Body:** Trả về toàn bộ snapshot sau khi đã cập nhật (giống cấu trúc `GET /api/bulletin`).

---

## 3. Quy chuẩn lỗi (Error Responses)

Mọi mã lỗi HTTP 4xx hoặc 5xx đều trả về định dạng JSON thống nhất:

```json
{
  "error": {
    "code": "INVALID_ARGUMENT",
    "message": "Mô tả chi tiết nguyên nhân lỗi."
  }
}
```

Các mã lỗi chuẩn:
- `400 Bad Request`: `code = "INVALID_ARGUMENT"` — Tham số hoặc body không đúng định dạng.
- `404 Not Found`: `code = "NOT_FOUND"` — Endpoint không tồn tại.
- `500 Internal Server Error`: `code = "INTERNAL"` — Lỗi xử lý nội bộ server.
