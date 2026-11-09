# SEM-40 — CHECKS skip-push CLI

- Người thực hiện: Tâm (`HoaiTam`); kiểm ngày 09/11/2026 (UTC+7).
- Base: `8a0c743` từ main sau nghiệm thu SEM-35; nhánh `codex/SEM-40-skip-push`.
- Đầu vào: SEM-27 và SEM-35 Done trên Project; API/store/CLI/sender, schema 2.0.0 và CHECKS có trên base. Đã đối chiếu protocol E06: 2 lượt × 45 phút, không force-run/re-register.
- Môi trường: macOS ARM64, Node 26.0.0, npm 11.12.1; test build TypeScript từ lockfile có sẵn. Không build APK hoặc gửi FCM; không dùng credential/token.

| Check | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| Build và hồi quy | Compile, test server/sender cũ tiếp tục đạt | `npm test` exit 0: **22/22 pass**, gồm 18 test hiện hữu và 4 test mới | Pass |
| Update + skip qua CLI thật | Snapshot persist, event khớp version/run/update | HTTP loopback với store tạm; CLI trả v1, log `server_updated` và `push_send_skipped`, mở lại store giữ v1/item | Pass — local |
| Không gửi/không accepted | Skip path không gọi sender, ID FCM null | `update-cli` chỉ gọi POST và module `skip_push.js`, không import Firebase; cả hai file event kiểm trong test không có accepted; message/attempt null | Pass — local, không phải phép đo delivery |
| Idempotency | Retry không bump version hoặc nhân event | CLI chạy lại cùng update trả `replayed=true`, giữ version và event ID; conflict trả lỗi, không thêm skip | Pass |
| Phục hồi sau thiếu export | Retry nhận lại commit và ghi skip | Xóa bản log skip sau update rồi retry cùng ID; v1 giữ nguyên, skip được ghi lại. Không mô tả thao tác này là crash vật lý | Pass — mô phỏng |
| Input/log/network lỗi | Không ghi skip thành công giả | Mode khác HYBRID, log bị lock/hỏng bị từ chối trước update; HTTP không kết nối không đổi store, log rỗng | Pass |
| Schema | Event hợp validator SEM-24 | Test gọi validator thực qua executable `PYTHON` hoặc mặc định theo nền tảng | Pass |
| E06 trên app/thiết bị | Cần run/log thật để kết luận periodic phục hồi | Không thực hiện trong SEM-40 | **Not run** |
| Windows native/mất điện | Có bằng chứng riêng nếu đã kiểm | Không chạy Windows native hoặc thử mất điện vật lý | **Not run** |

Bằng chứng tái lập: [test/skip-push.test.js](../../../server/test/skip-push.test.js), [CLI](../../../server/bin/update-cli.js), [module log](../../../server/src/skip_push.js). Các dữ liệu run trong test là fixture trong thư mục tạm, không phải kết quả E06. Test mới kiểm cả schema bằng validator SEM-24 và không cần Firebase thật.

Đầu ra bàn giao: [FAULT_INJECTION.md](FAULT_INJECTION.md) ghi lệnh, xử lý retry/log/lock, phương pháp ghép evidence và điều kiện chạy E06 cho SEM-36/37/49 và các task đo. CLI thêm flag và log local, không thay HTTP/event contract 2.0.0.

Giới hạn: log CLI tách giao dịch khỏi server; crash sau commit trước ghi event cần retry cùng update ID. Lock cũ cần xác minh process dừng trước khi gỡ. Không chặn sender do một process/người khác chạy riêng; người đo kiểm soát luồng gửi trong cửa sổ E06. Không có blocker triển khai local; kết quả app/periodic phải do task thực nghiệm cung cấp.

Trưởng nhóm kiểm nhận/merge; task chỉ bàn giao đến Review, không tự chuyển Done.

## Đồng bộ bàn giao

- Commit source/test được kiểm: `cc4ce58`; [PR #21](https://github.com/ThanhTris/Seminar-IE307/pull/21) đã tag `@ThanhTris`, chờ kiểm nhận.
- SEM-40 đã chuyển Review. Script `--apply` và `--check` exit 0: 45 task, 23 Done, 20 Todo, 2 Review; assignee khớp owner, không có chu trình dependency. Snapshot lúc **07:09:48 UTC ngày 09/11/2026**.
