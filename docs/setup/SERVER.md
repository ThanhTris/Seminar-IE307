# SEM-27 — Chạy server snapshot và CLI

Server hiện thực [HTTP contract 2.0.0](../API.md) và phát event `server_updated` theo [schema 2.0.0](../EVENT_SCHEMA.md). POST chỉ cập nhật snapshot, không gửi push. Các lệnh bên dưới dành cho môi trường demo tin cậy: endpoint update không có auth, không mở trực tiếp ra Internet.

## Cài đặt và cấu hình

Trong `server/`, dùng Node.js 22 trở lên (lần kiểm SEM-27: Node 26.0.0/npm 11.12.1):

```sh
npm ci
npm run build
npm test
npm start
```

Mặc định `HOST=127.0.0.1`, `PORT=3000`, `STORE_DIR=./.local/server` tính theo thư mục chạy. Xem [.env.example](../../server/.env.example); file này chỉ minh họa biến shell, server không tự nạp `.env`. Ví dụ chạy với đường dẫn riêng:

```sh
HOST=127.0.0.1 PORT=3000 STORE_DIR=../.local/server-sem27 npm start
```

Store mới tạo snapshot version 0, danh sách rỗng và timestamp tạo thật. `state.json` chứa snapshot, ledger chống trùng và outbox event; `events.jsonl` là bản xuất để thu thập, có thể tái tạo từ state. Các file runtime nằm trong `.local/` bị Git bỏ qua; không commit dữ liệu run, credential hoặc token. Luôn lưu cả `state.json` và event output của run theo protocol.

Trước khi đổi tên file, server sync nội dung file tạm. Trên nền tảng khác Windows, server còn sync thư mục sau đổi tên; trên Windows bỏ bước sync thư mục do không được hỗ trợ trong môi trường nhóm trưởng kiểm tra. Do đó chưa có bằng chứng bảo đảm tương đương về độ bền sau mất điện trên Windows.

**Không có migration v1 → v2.** File `server/data/snapshot.json` có sẵn trên main là scaffold v1, không được tự nhập hoặc ghi đè. Khi bắt đầu môi trường v2 mới, dùng `STORE_DIR` riêng; không trộn cache/run v1 với v2, ghi nhận reset và xóa cache liên quan theo contract. Nếu thư mục store chỉ định có `snapshot.json` v1 nhưng chưa có state v2, server từ chối tạo store thay vì tự reset.

Chỉ một process server được mở một `STORE_DIR`; lock bảo vệ tuần tự hóa giữa các process. Tắt bằng SIGINT/SIGTERM để giải phóng lock. Nếu process bị kill/crash, lock có thể còn lại: kiểm PID trong `state.json.lock` và xác minh process đó đã dừng, giữ nguyên state và events, sau đó xóa **chỉ** file lock cũ trước khi khởi động lại. Không xóa lock nếu còn process đang dùng store. Sau restart, server xuất lại JSONL từ outbox; consumer deduplicate theo `event_id`. Nếu state/ledger bị hỏng hoặc mất trong khi còn event output, server trả 503 hoặc không khởi động; không tự đặt lại version. Khôi phục từ bản sao đầy đủ hoặc thiết lập môi trường đo mới một cách có chủ ý.

## Đọc và cập nhật

```sh
curl -sS http://127.0.0.1:3000/health
curl -i http://127.0.0.1:3000/api/bulletin
curl -i -H 'If-None-Match: "v0"' http://127.0.0.1:3000/api/bulletin
npm run update -- --update-id update-e01-01 --run run-e01-01 --mode PERIODIC --device emulator-01 --title 'Thông báo' --body 'Nội dung thử nghiệm' --request-id request-e01-01
```

`update_id`, `run`, `mode`, `device`, `title`, `body` là bắt buộc; `--request-id` tùy chọn là correlation header. CLI gửi HTTP tới `SERVER_URL` hoặc `--base-url` nếu truyền; nó không bao giờ ghi store trực tiếp. Sau timeout/lỗi không rõ kết quả, retry **cùng update_id và cùng toàn bộ nội dung**; dùng ID mới có thể tạo thêm update. Response replay giữ version của commit ban đầu, còn GET đọc snapshot hiện tại. Payload sai, ID xung đột hoặc store đầy được trả lỗi theo contract.

Để đánh dấu bỏ gửi push có chủ ý trong E06, dùng `--skip-push` với `--mode HYBRID` và file `--events` riêng. Xem [SEM-40: fault injection](../evidence/SEM-40/FAULT_INJECTION.md) để lấy lệnh, cách retry và thu bằng chứng. POST vẫn chỉ cập nhật snapshot; flag không chặn sender được chạy riêng bởi process khác.

## Kết nối từ thiết bị

- Emulator trên cùng host: base URL `http://10.0.2.2:3000`, server có thể giữ bind loopback. Chỉ kiểm khi emulator và app có cấu hình debug HTTP phù hợp.
- OPPO hoặc emulator qua ADB reverse: `adb -s <serial-local> reverse tcp:3000 tcp:3000`, app dùng `http://127.0.0.1:3000`; gỡ bằng `adb -s <serial-local> reverse --remove tcp:3000`. Không đưa serial vào log bàn giao.
- LAN tin cậy: `HOST=0.0.0.0`, client dùng IP LAN của host (không dùng `0.0.0.0` làm URL); kiểm firewall và cách ly Wi-Fi. Chỉ mở trong mạng thử nghiệm, vì route update không có auth.

Các đường Android và OPPO chưa được SEM-27 xác nhận. [Hồ sơ SEM-12](../evidence/SEM-12/CHECKS.md) ghi chưa có OPPO; không coi hướng dẫn là kết quả kết nối thật. FCM sender đang thuộc SEM-35 và chưa được SEM-27 kiểm nhận.
