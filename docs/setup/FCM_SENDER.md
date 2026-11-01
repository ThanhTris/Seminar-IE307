# Hướng dẫn Gửi Push FCM Data-Only — SEM-35

Tài liệu hướng dẫn sử dụng công cụ CLI `fcm-sender.js` để phát tín hiệu push phục vụ thử nghiệm cơ chế đồng bộ Push và Hybrid.

---

## 1. Nguyên tắc Payload Data-Only

Theo yêu cầu của đề tài và [kế hoạch SEM-18/35](../mechanisms/SERVER_FCM.md):
- **Không có `notification` block:** Không hiển thị popup banner thông báo của hệ thống Android nhằm đo lường chính xác độ trễ và khả năng đánh thức ngầm của thiết bị.
- **Normal priority:** Giữ mức ưu tiên chuẩn (`normal`), không dùng `high priority` để đối chiếu trung thực với bài báo nghiên cứu và hành vi Doze mode.
- **TTL:** 86400 giây (24 giờ).

---

## 2. Cách chạy CLI

Từ thư mục `server/`:

```bash
# Chạy mô phỏng kiểm tra cấu trúc payload
node bin/fcm-sender.js

# Gửi tới device token cụ thể
node bin/fcm-sender.js --token "<DEVICE_FCM_TOKEN>" --run "run-e02-01" --version 42
```

### Thiết lập thông tin xác thực (Production/Live Test):
```bash
export GOOGLE_APPLICATION_CREDENTIALS="$PWD/.local/secrets/fcm-service-account.json"
node bin/fcm-sender.js --token "<DEVICE_FCM_TOKEN>"
```
