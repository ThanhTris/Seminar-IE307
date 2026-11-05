# SEM-27 — CHECKS server snapshot và update CLI

## Nhận dạng

- Người thực hiện: Tâm (`HoaiTam`). Đối chiếu và kiểm ngày 04/11/2026 (UTC+7).
- Base: `5e1c643550e35aee5f08cd74002be038ee3d4b9e`; commit source/build được kiểm: `a3575fc`.
- Đầu vào: SEM-13 và SEM-26 Done trên Project, các file môi trường, API/event schema và CHECKS có trên base. Chạy theo contract/schema 2.0.0, không dùng dữ liệu thử như dữ liệu demo.
- Host: macOS/Darwin ARM64, Node `v26.0.0`, npm `11.12.1`; TypeScript `5.9.3` theo lockfile. Không build APK, không kết nối Firebase/thiết bị thật.
- Test chạy server HTTP trên loopback với cổng ngẫu nhiên và store tạm trong thư mục hệ thống; không sử dụng credential/token hoặc store demo. `npm ci --ignore-scripts` thành công; `npm test` build TypeScript và chạy Node test runner.

## Kết quả

| Kiểm tra | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| Build và lockfile | Cài sạch, compile được | `npm ci --ignore-scripts` exit 0; `npm test` build exit 0; file `server/package-lock.json` có trong commit source | Pass |
| Test tự động | HTTP, store, retry và CLI đúng contract | 8 nhóm test pass, 0 fail: [server.test.js](../../../server/test/server.test.js) | Pass |
| Khởi tạo/GET/ETag | Version 0 rỗng; 200 và 304 đúng validator | Kiểm v0/ETag, weak validator, danh sách, `*`, validator sai và 304 body rỗng; header API version | Pass |
| Update, log, replay | Snapshot/ledger/event cùng commit; giữ response gốc | Update v1 rồi v2; event JSONL có request/run/update; retry v1 sau v2 và restart trả v1 `replayed=true`, không tạo event mới; conflict bị từ chối | Pass |
| Đồng thời và giới hạn | Version mới duy nhất; replay khi đầy vẫn hợp lệ | 25 update ID khác nhau nhận đủ v1–v25; 8 request cùng ID chỉ một commit; đến 100 item replay thành công, ID mới trả `SNAPSHOT_FULL` | Pass |
| Hỏng/mất store và crash | Không reset version; khôi phục outbox đã commit | Store sai/mất trả 503; server thứ hai bị lock; process thử bị SIGKILL, xác minh lock còn rồi gỡ lock cũ, tái mở state và phục hồi JSONL sau khi xóa bản export để mô phỏng mất export | Pass, có thao tác gỡ lock thủ công |
| Input/lỗi | Không commit input sai; lỗi không lộ dữ liệu | Kiểm field thừa/sai, ID sai, JSON trùng key, 413, 415, 404, 405/Allow, correlation không hợp lệ; version không tăng | Pass |
| CLI HTTP | Retry cùng ID; không ghi thẳng file khi không kết nối | CLI update thành công và replay; cổng không thể kết nối trả lỗi `commit=unknown`, version không thay đổi | Pass |
| Store scaffold v1 | Không ghi đè hoặc tự nhập dữ liệu cũ | Thư mục có `snapshot.json` v1 mà chưa có state v2 bị từ chối; hướng dẫn dùng store/cache mới | Pass |
| Giới hạn `VERSION_EXHAUSTED` | Không reset version khi tới giới hạn | Nhánh xử lý có trong source; không tạo state giả vượt giới hạn 100 item để tuyên bố đã kiểm end-to-end | Not run |
| Emulator/OPPO/FCM | Phải có app, máy và log thật | Không chạy trong SEM-27; SEM-12 ghi chưa có OPPO, FCM thật là task riêng | Not run |

Lần `npm test` trong sandbox bị từ chối bind `127.0.0.1` (`EPERM`); chạy lại ngoài sandbox với cổng loopback tạm cho kết quả 8/8 như trên. Không tính lần bị chặn là lỗi chức năng server.

`npm ci`/`npm audit` tại thời điểm kiểm báo **8 moderate**, không có high/critical, trong cây dependency `firebase-admin` đã có từ scaffold (`uuid` và các package Google Cloud). Server snapshot không import Firebase; SEM-35 cần đánh giá/nâng dependency phù hợp khi xử lý sender. Không tự nâng major Firebase hoặc tuyên bố sender hiện có đã được kiểm nhận. Log chi tiết audit giữ local, không chứa credential.

## Bàn giao và giới hạn

- [Hướng dẫn SERVER.md](../../setup/SERVER.md): cấu hình, lệnh chạy, HTTP, kết nối thiết bị, phục hồi lock và khác biệt store v1/v2.
- Source TypeScript, lockfile, cấu hình mẫu, CLI và test nằm trong `server/`; `server/data/snapshot.json` cũ không được sử dụng làm state v2. Không tự migrate hay reset cache của run đang tồn tại.
- Sau crash/SIGKILL, cần xác minh process cũ đã dừng và gỡ `state.json.lock` cũ trước khi chạy lại; state và outbox được giữ. Việc khôi phục đó không đồng nghĩa đã kiểm crash ở mọi thời điểm ghi hoặc mất điện vật lý.
- Cổng endpoint update không có auth; chỉ chạy trên host/LAN tin cậy. Hướng dẫn emulator/OPPO chưa được chứng minh bằng thiết bị trong task này.
- Đầu ra dành cho SEM-28, SEM-35, SEM-40 và SEM-49 sau khi trưởng nhóm kiểm nhận. Trưởng nhóm review và merge; không tự chuyển Done.

## Đồng bộ Review

- [PR #12](https://github.com/ThanhTris/Seminar-IE307/pull/12) đã gắn thẻ `@ThanhTris`; source được kiểm tại `a3575fc`, CHECKS tại `ee73a2e`.
- SEM-27 đã chuyển Review trên Project. Chạy `python3 scripts/update_task_snapshot.py --apply` và `--check`: exit 0, đối chiếu 45 task, 14 Done, 29 Todo, 2 Review; assignee khớp owner, không có chu trình dependency. Snapshot lúc 02:55:28 UTC ngày 04/11/2026.
- Sau bàn giao Review, chỉ sửa nội dung khi trưởng nhóm có comment yêu cầu; không tự merge hoặc chuyển Done.

## Cập nhật theo review của ThanhTris — 05/11/2026

- [Review PR #12](https://github.com/ThanhTris/Seminar-IE307/pull/12) yêu cầu sửa lỗi `fsync` thư mục trên Windows và xử lý xung đột snapshot với `main`. Đã nhập `origin/main` tại `9b5408b` vào nhánh SEM-27; giữ phiên bản snapshot mới từ main rồi đồng bộ lại từ Project. Không merge PR vào main.
- Commit `af60deb` giữ `fsync` file tạm trên mọi nền tảng và chỉ mở/sync thư mục sau rename khi `process.platform !== 'win32'`. [Hướng dẫn server](../../setup/SERVER.md) ghi rõ giới hạn về độ bền khi mất điện trên Windows.
- Trên macOS ARM64, Node `v26.0.0`, npm `11.12.1`, chạy `npm test` ngoài sandbox: build TypeScript thành công, **9/9 test pass**. Test thứ 9 mô phỏng `process.platform = win32` và giả lập lỗi khi mở thư mục; xác nhận khởi tạo/update không mở thư mục để sync. Tám test còn lại tiếp tục kiểm các hành vi đã ghi ở trên.
- **Windows/Linux native trên commit cập nhật: Not run trong lần này.** Review của trưởng nhóm mô tả đã kiểm bản vá đề xuất trên Windows và Linux; kết quả đó không thay thế kiểm thử native của chính commit `af60deb`. Chưa kiểm độ bền sau mất điện vật lý.
