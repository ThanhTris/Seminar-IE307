# Quy chuẩn Sự kiện Đồng bộ (Event Schema) — SEM-26

Tài liệu này định nghĩa cấu trúc dữ liệu cho các sự kiện đồng bộ (Timeline Events) được ghi nhận trong ứng dụng Android và server trong đề tài Seminar IE307.

- **Phiên bản:** `1.0.0`
- **Mục tiêu:** Đảm bảo tách biệt rõ ràng các mốc trong vòng đời đồng bộ: `accepted` (đã xếp lịch), `received` (đã nhận push), `started` (worker bắt đầu chạy), `applied` (đã ghi cache thành công), `unchanged` (dữ liệu không đổi), và `failed` (thất bại).

---

## 1. Cấu trúc trường sự kiện (Event Fields)

Mỗi sự kiện được ghi nhận vào cơ sở dữ liệu Room và xuất ra file log theo cấu trúc sau:

| Tên trường | Kiểu dữ liệu | Bắt buộc | Mô tả |
|---|---|:---:|---|
| `eventId` | String (UUID) | Có | Mã định danh duy nhất của sự kiện. |
| `source` | String (Enum) | Có | Nguồn kích hoạt: `MANUAL`, `PERIODIC`, `PUSH`. |
| `mode` | String (Enum) | Có | Chế độ thử nghiệm tại thời điểm chạy: `PERIODIC`, `PUSH`, `HYBRID`. |
| `runId` | String | Có | Mã lượt chạy thử nghiệm (ví dụ: `run-e01-01`). Không được để trống. |
| `eventType` | String (Enum) | Có | Loại sự kiện (xem mục 2). |
| `occurredAtEpochMillis` | Long | Có | Thời điểm xảy ra theo Unix epoch (milliseconds). |
| `occurredAtUtc` | String | Có | Thời điểm xảy ra định dạng ISO 8601 UTC kết thúc bằng `Z`. |
| `elapsedMonotonicNanos` | Long | Tùy chọn | Thời gian đồng hồ monotonic (System.nanoTime) để tính độ trễ chính xác không bị nhảy giờ do NTP. |
| `version` | Long | Tùy chọn | Phiên bản snapshot liên quan (ví dụ version vừa cập nhật). |
| `outcome` | String | Tùy chọn | Kết quả tóm tắt: `applied`, `unchanged`, `stale`, `rejected`, `failure`. |
| `reason` | String | Tùy chọn | Lý do chi tiết (nếu bị reject hoặc lỗi). |
| `correlation` | Object | Tùy chọn | Nhóm các mã định danh tương quan (Correlation IDs, xem mục 3). |

---

## 2. Vòng đời loại sự kiện (`eventType`)

Các loại sự kiện được phân định rành mạch, không được gộp lẫn:

1. `sync_requested`: Khi UI bấm "Đồng bộ thủ công" hoặc FCM nhận push trigger.
2. `work_enqueued`: Khi WorkManager chấp nhận xếp lịch công việc (`OneTimeWorkRequest` hoặc `PeriodicWorkRequest`). Ghi nhận `work_id`.
3. `work_started`: Khi `SyncWorker.doWork()` thực sự bắt đầu chạy nền.
4. `snapshot_applied`: Khi server trả về snapshot có version mới hơn và đã lưu thành công vào Room database trong cùng một transaction.
5. `snapshot_unchanged`: Khi server trả về HTTP 304 hoặc version bằng với cache hiện tại (không có thay đổi dữ liệu).
6. `snapshot_stale`: Khi server trả về version nhỏ hơn version hiện có trong cache (bảo vệ version guard không cho ghi đè).
7. `sync_failed`: Khi có lỗi mạng, lỗi phân tích cú pháp hoặc lỗi cơ sở dữ liệu.

---

## 3. Khối Correlation IDs

Dùng để liên kết một hành động từ server -> push -> client -> worker:

```json
{
  "requestId": "req-1793426400-01",
  "workId": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "messageId": "0:1793426400000000%12345678f9012345"
}
```

- `requestId`: Mã do client sinh cho mỗi chu kỳ hoặc request đồng bộ (giữ nguyên khi retry).
- `workId`: ID do Android `WorkManager` tự động cấp cho Worker.
- `messageId`: ID do Firebase Cloud Messaging gán khi gửi push (chỉ có khi `source = PUSH`).

---

## 4. Ví dụ JSON Event Payload

### Sự kiện cập nhật thành công (`snapshot_applied`)
```json
{
  "eventId": "c71a3962-d273-455b-bf49-59eb4e41e549",
  "source": "MANUAL",
  "mode": "HYBRID",
  "runId": "run-e01-01",
  "eventType": "snapshot_applied",
  "occurredAtEpochMillis": 1793426405120,
  "occurredAtUtc": "2026-10-31T17:00:05.120Z",
  "version": 42,
  "outcome": "applied",
  "reason": "Áp dụng thành công snapshot v42 từ server.",
  "correlation": {
    "requestId": "req-8910",
    "workId": "f295b9d2-7c98-4c12-8f15-08e1a141b712",
    "messageId": null
  }
}
```
