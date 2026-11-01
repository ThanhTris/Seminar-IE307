# Hướng dẫn Chạy Snapshot Server & Update CLI — SEM-27

Tài liệu hướng dẫn khởi chạy máy chủ Snapshot và công cụ CLI phát hành bản tin phục vụ thử nghiệm các cơ chế đồng bộ (Manual, Periodic, Push, Hybrid).

---

## 1. Yêu cầu môi trường

- Node.js version 22+ hoặc 24+ (đã xác thực trên macOS Node 26.0.0 và Windows Node 24.15.0).
- Không yêu cầu cài thêm package ngoài; server sử dụng hoàn toàn module chuẩn của Node.js (`node:http`, `node:fs`).

---

## 2. Khởi chạy máy chủ

Di chuyển vào thư mục `server/`:

```bash
cd server
npm start
```

Mặc định server sẽ lắng nghe trên cổng `3000`:
- Local host: `http://127.0.0.1:3000`
- Android Emulator: `http://10.0.2.2:3000`

### Chạy cổng tùy chỉnh:
```bash
PORT=8080 npm start
```

---

## 3. Sử dụng công cụ `update-cli`

CLI cho phép phát hành bản tin mới và tự động tăng `version` đơn điệu.

```bash
# Cập nhật nhanh với nội dung mặc định
npm run update

# Cập nhật với tiêu đề và nội dung chỉ định
npm run update -- --title "Thông báo bảo trì" --body "Bảo trì server lúc 00:00" --run "run-e01"
```

*Lưu ý:* Nếu server đang chạy trên cổng 3000, CLI sẽ gửi qua HTTP POST `/api/bulletin/update`. Nếu server đang tắt, CLI sẽ cập nhật trực tiếp vào file `server/data/snapshot.json`.

---

## 4. Kiểm tra (Unit Tests)

Chạy bộ test kiểm tra snapshot store, HTTP 200, ETag và HTTP 304:

```bash
npm test
```
