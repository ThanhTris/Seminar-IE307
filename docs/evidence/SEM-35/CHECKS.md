# SEM-35 — CHECKS FCM sender

## Nhận dạng và đầu vào

- Người thực hiện: Tâm (`HoaiTam`); ngày kiểm 05/11/2026 (UTC+7); base `33e3bf7` trên `origin/main`, sau merge SEM-27.
- SEM-13, SEM-18, SEM-27 Done trên Project; đã đối chiếu môi trường Firebase, giải thích FCM, HTTP/event schema 2.0.0 và server/CHECKS. Task không thay đổi server snapshot hay chạy thực nghiệm E02.
- Host macOS ARM64, Node `v26.0.0`, npm `11.12.1`, Firebase Admin `14.5.0`; lockfile trong `server/`. Lệnh kiểm: `npm ci --ignore-scripts` và `npm test` từ `server/`, dùng loopback và thư mục tạm, không chứa token thật.
- Kiểm sự hiện diện ngày 05/11: `FIREBASE_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`, `FCM_TOKEN_FILE` chưa đặt; không thấy ADC mặc định hoặc file credential/token tại các đường dẫn ví dụ. Đây chỉ là kết quả ở máy/tiến trình này, không kết luận nhóm chưa có Firebase ở nơi khác.

## Expected / actual

| Kiểm tra | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| Cài/build | Lockfile cài sạch, TypeScript server build | `npm ci --ignore-scripts`, `npm test` exit 0; Firebase Admin 14.5.0 | Pass |
| Bộ test | Không hồi quy server, kiểm sender | 18 test pass: 9 test sender, 9 test SEM-27; [fcm-sender.test.js](../../../server/test/fcm-sender.test.js); event giả lập được kiểm bằng validator SEM-24 | Pass |
| Payload | data-only, `normal`, TTL tính ms | Test kiểm data string, không notification, TTL mặc định 86400000; `--validate-only` không gửi | Pass — fixture |
| Trạng thái send | Accepted chỉ khi SDK trả ID, tách rejected/unknown/local | Test inject SDK giả lập trả ID, lỗi token, lỗi network và thiếu cấu hình; kiểm event/schema/correlation và không in token. Không phải FCM thật | Pass — fixture |
| Update trước push | Chỉ gửi khi snapshot và event `server_updated` tương ứng | Test preflight đúng/sai update/version; test CLI thật kết nối server loopback, thiếu Firebase tạo `push_send_failed_local`, không có message/attempt | Pass — local |
| An toàn log | Không ghi token, error text hay giả ID | Test token/exception giả không xuất hiện; test lỗi ghi log không gửi lại và không bịa rejection | Pass — fixture |
| Runtime Firebase / callback | Response thật hoặc blocker | Không có project ID, credential và token được xác nhận ở máy kiểm; chưa gọi FCM, không có message ID thật, Android callback Not run | **Not run — blocker B1** |
| npm audit | Ghi cảnh báo thực tế | `npm ci` báo 6 moderate, 0 high/critical; `npm audit fix` vẫn báo 6 moderate trong glob/minimatch và các dependency bắc cầu. Chưa nâng ép hoặc thay override ngoài phạm vi | Có giới hạn |

B1: cần người quản lý xác nhận project/app/quyền FCM và cung cấp credential local an toàn cùng registration token thiết bị theo [hướng dẫn](../../setup/FCM_SENDER.md). Không gửi token hoặc service-account key qua chat/repo. Vì acceptance cho phép **response thật hoặc blocker**, task có thể đề nghị Review với B1 và Not run được ghi rõ; không tuyên bố đã gửi hay nhận thành công.

Nguồn đối chiếu ngày 05/11: [Admin send](https://firebase.google.com/docs/reference/admin/node/firebase-admin.messaging.messaging), [AndroidConfig](https://firebase.google.com/docs/reference/admin/node/firebase-admin.messaging.androidconfig), [FCM error codes](https://firebase.google.com/docs/cloud-messaging/error-codes) và [Admin error handling/retry](https://firebase.google.com/docs/reference/admin/error-handling). Test giả lập không khẳng định error code hoặc response đã được quan sát từ FCM.

## Bàn giao và giới hạn

- `server/bin/fcm-sender.js`, `server/src/fcm_sender.js`, test và lockfile; [FCM_SENDER.md](../../setup/FCM_SENDER.md) có cấu hình, lệnh và cách thu event cho SEM-24/34/36/40.
- Sender log tách file khỏi outbox SEM-27; nếu crash sau response trước khi ghi event thì kết quả có thể không được ghi nhận. SDK có thể tự retry HTTP nội bộ; attempt ID ghi theo mỗi lần gọi SDK. Phải giữ signal ID khi retry và không suy mất event là chưa gửi.
- Không tự merge hoặc chuyển Done; sau bàn giao Review chỉ sửa theo comment của nhóm trưởng.

## Đồng bộ bàn giao

- Commit nội dung được kiểm: `ea01a6a`; [PR #16](https://github.com/ThanhTris/Seminar-IE307/pull/16) đã tag `@ThanhTris`, chờ nhóm trưởng kiểm nhận.
- SEM-35 đã chuyển Review. `python3 scripts/update_task_snapshot.py --apply` và `--check` exit 0: 45 task, 19 Done, 24 Todo, 1 In Progress, 1 Review; assignee khớp owner, không có vòng lặp dependency. Snapshot đối chiếu 08:02:58 UTC ngày 05/11/2026.

## Cập nhật theo review ThanhTris — 09/11/2026

- Review ngày 05/11 trên PR #16 yêu cầu sửa test validator khi Windows có lệnh `python` thay vì `python3`. Commit `aa1cf23` ưu tiên `process.env.PYTHON`; mặc định Windows dùng `python`, các nền tảng khác dùng `python3`. Tài liệu setup bổ sung cách chọn executable, kể cả Python Launcher `py`.
- Đã nhập `origin/main` tại `9c4383f` vào nhánh PR bằng commit `cd8f7c7`; giải quyết 48 file snapshot xung đột bằng phiên bản mới từ main, rồi sinh lại theo Project. Không merge PR vào main.
- `npm test` trên macOS ARM64: build thành công, **18/18 pass**. Chạy riêng test validator với `PYTHON` là đường dẫn executable lấy từ `command -v python3`: **1/1 pass**. Không gọi FCM thật trong các test này.
- Windows native trên commit cập nhật: **Not run trong lần kiểm này**. Kết quả Windows/macOS của bản vá đề xuất trong review là bằng chứng do trưởng nhóm cung cấp; không trình bày thành lần chạy Windows của máy hiện tại.
- `git diff --check` cho bản sửa không báo lỗi. Các dòng whitespace kế thừa từ main trong merge commit không thuộc bản sửa Python.
