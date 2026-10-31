# SEM-13 — CHECKS và bàn giao

- Người thực hiện: Tâm (`HoaiTam`).
- Ngày kiểm tra: **31/10/2026 (UTC+7)**; HTTPS lúc 19:30:24, SDK/loopback lúc 19:33:17.
- Hạn được giao: 30/10/2026 12:00 (UTC+7); giữ nguyên hạn, không ghi lùi ngày kiểm tra.
- Base: `ff8f11148d5d2cfe0f2602bb6b58db00ca194f64` (`main`, đã fetch trước khi làm).
- Nhánh: `codex/SEM-13-server-firebase`.
- Artifact: [SERVER_FIREBASE.md](../../environment/SERVER_FIREBASE.md), cùng CHECKS này trong commit bàn giao SEM-13; tra commit bằng `git log -- docs/environment/SERVER_FIREBASE.md`.
- Phạm vi: audit môi trường và bàn giao kết quả/blocker theo [yêu cầu SEM-13](../../../tasks/backlog/SEM-13.md); không tuyên bố app/server/sender đã chạy end-to-end.

## Kiểm chứng thực tế

| Check | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| OS và runtime | Có phiên bản thực của máy kiểm tra | macOS 26.6.2 / 25G83, Darwin 25.6.0 arm64; Node v26.0.0; npm 11.12.1; pnpm 11.25.0 | Pass |
| Package manager | Có thể lấy và cài dependency bằng công cụ đã chọn | npm đọc metadata `firebase-admin@14.5.0`, engine `>=22`; install vào `.local/sem13/sdk-probe/` thành công, 172 packages, tạo lockfile local | Pass (install; không chạy security audit) |
| Admin SDK load/init | Runtime có thể import app/messaging và tạo client | Import `firebase-admin/app`, `firebase-admin/messaging`; initialize/delete app fixture `sem13-local-fixture`; `typeof messaging.send = function`; không gọi `send` hay lấy access token | Pass (offline SDK; không chứng minh auth) |
| Host HTTP | Node tạo listener và đọc response trên loopback | Cổng tự cấp trên 127.0.0.1, GET trả 200 với `{"probe":"sem13-only","snapshotApi":false}`; listener đóng sau probe | Pass (môi trường; không phải SEM-27) |
| Registry network | DNS/TLS/HTTP hoạt động từ host | npm registry HTTP 200, curl exit 0, TLS verify 0 | Pass (host) |
| FCM/OAuth network | Host liên hệ được endpoint công khai | `fcm.googleapis.com/` và `oauth2.googleapis.com/` trả HTTP 404 ở root, curl exit 0, TLS verify 0; không có Authorization/payload | Pass (host transport); auth Not run |
| Firebase project/config inventory | Xác định project/quyền hoặc ghi blocker cụ thể | Sáu biến Firebase/Google kiểm tra đều chưa đặt; các file cấu hình repo và session Firebase/ADC ở vị trí thông thường không hiện diện; không đọc/in secret | Pass (audit); B1 còn mở |
| FCM API/IAM/credential | Có quyền gửi thật đã xác nhận | Chưa xác nhận project ID, Android registration hoặc principal/role/credential; chưa gọi API có xác thực | Not run — B1 |
| FCM send / message ID | Có response thật nếu đã gửi | Không gửi message; `message_id = null`; không có accepted/received/applied runtime | Not run — B1/B2/B3 |
| ADB/SDK | Có công cụ và thiết bị cho phép chạy reverse | ADB không có trên PATH; `~/Library/Android/sdk` không có; ANDROID_HOME/ANDROID_SDK_ROOT chưa đặt; không tìm toàn máy | Not run — B2 |
| LAN/reverse/device Internet | Thiết bị truy cập server và FCM riêng biệt | Chưa chạy emulator/OPPO, chưa có runtime server trên base; bảng mapping và bước kiểm lại trong artifact | Not run — B2/B3 |
| Cấu hình local và ranh giới | Có cách cấp riêng cho app/server, mẫu không chứa dữ liệu thật | Package ID lấy từ SEM-11; project ID để placeholder; phân tách service-account JSON, Google Services config và registration token; không sửa app/server của task khác | Pass (tài liệu) |
| Secret handling | File thật không được đưa vào Git | Chỉ hai tài liệu Markdown được bàn giao; dependency/cache/probe nằm trong `.local/` được ignore; kiểm ignore bằng đường dẫn fixture | Pass |
| Markdown và cấu hình mẫu | Link nội bộ đọc được, không lỗi khoảng trắng hoặc credential-shaped content | 5 link nội bộ tồn tại; hai tài liệu có newline cuối, code fence cân bằng, không trailing whitespace; scan private-key/API-key/GitHub-token patterns không có match | Pass |
| Git ignore | Cấu hình local/probe được bỏ qua, mẫu vẫn track được | 7 đường dẫn fixture `.env`/local/token/Google Services/local properties/probe bị ignore; `.env.example` không bị ignore | Pass |

## Lệnh và giới hạn tái lập

Chạy từ root repo. Lệnh inventory không cần cài thêm công cụ:

```sh
sw_vers
uname -srm
node --version
npm --version
pnpm --version
command -v node npm corepack pnpm yarn firebase gcloud adb
npm view firebase-admin version engines --json --cache .local/sem13/npm-cache
npm install --prefix .local/sem13/sdk-probe --cache .local/sem13/npm-cache --ignore-scripts --no-audit --no-fund --save-exact firebase-admin@14.5.0
```

Cài thử dùng `--ignore-scripts`, không thêm dependency hoặc lockfile vào server chưa triển khai. npm báo deprecation từ dependency bắc cầu `glob@10.5.0` và `node-domexception@1.0.0`; không thay dependency upstream trong task audit.

Probe SDK có thể chạy lại sau install bằng đoạn sau, trong thư mục `.local/sem13/sdk-probe/`:

```js
const { initializeApp, deleteApp } = require('firebase-admin/app');
const { getMessaging } = require('firebase-admin/messaging');
const app = initializeApp({ projectId: 'sem13-local-fixture' }, 'sem13-local-fixture');
console.log(typeof getMessaging(app).send); // function; không gọi send
deleteApp(app).catch(() => { process.exitCode = 1; });
```

Kiểm transport host không xác thực:

```sh
curl --silent --show-error --output /dev/null --connect-timeout 5 --max-time 15 --write-out 'http=%{http_code} tls_verify=%{ssl_verify_result}\n' https://fcm.googleapis.com/
curl --silent --show-error --output /dev/null --connect-timeout 5 --max-time 15 --write-out 'http=%{http_code} tls_verify=%{ssl_verify_result}\n' https://oauth2.googleapis.com/
```

Probe đầy đủ và kết quả JSON đã chạy giữ local tại `.local/sem13/probe.mjs` và `.local/sem13/probe-results.json`; bảng trên ghi các kết quả cần bàn giao để người clone không phải có file local. Fixture project ID chỉ dùng khởi tạo offline, không phải project thật. Không có phép đo delivery, quyền gửi hoặc snapshot runtime trong các probe này.

Sandbox mặc định chặn DNS ngoài máy và socket listener (`EPERM`); đã chạy lại các probe cần mạng/socket ngoài sandbox và ghi kết quả thành công ở trên. Lỗi sandbox không được gán thành lỗi mạng/Node của máy.

## GitHub Project và kiểm tra snapshot

- GitHub đọc được bằng tài khoản `HoaiTam`, quyền repo `WRITE`. Token có `read:project` nhưng thiếu scope `project` cho cập nhật Project; không phải lỗi đăng nhập.
- Lệnh chuyển SEM-13 sang In Progress bằng `gh project item-edit` và phép thử GraphQL riêng đều bị từ chối vì thiếu scope `project`. Lần đọc lại nguồn lúc audit cho thấy SEM-13 là **In Progress**; không quy thay đổi này cho lệnh đã thất bại.
- `python3 scripts/update_task_snapshot.py --check` đã chạy và **Fail** với `SEM-11: Input/status snapshot differs; review or refresh`. Rà read-only thấy Project dùng timestamp snapshot `2026-10-30 20:34:26 UTC`, còn catalog của base là `2026-10-30 12:33:46 UTC`; nguồn có 3 Done / 1 In Progress / 41 Todo lúc kiểm tra. Đây là sai lệch đã có trước khi thêm hai artifact SEM-13.
- Không chạy `--apply` khi thiếu quyền ghi Project, không sửa tay các snapshot để giả trạng thái đồng bộ. Không sửa script hoặc task của người khác để làm check này xanh.
- Để hoàn tất workflow: tài khoản thực hiện cần bổ sung scope `project` qua `gh auth refresh -h github.com -s project` và có quyền edit Project, hoặc người quản lý Project thực hiện bước đó. Sau kiểm nhận đầu ra, chuyển trạng thái đúng thực tế, chạy `python3 scripts/update_task_snapshot.py --apply` rồi `--check` trên base đã cập nhật. Không coi task là Done chỉ vì có PR.

## Bàn giao và blocker còn mở

- **SEM-19:** dùng môi trường đã đo và các giới hạn B1/B2/B3 khi tổng hợp; không nói Firebase đã gửi được.
- **SEM-26:** nhận package ID/baseline host và ranh giới cấu hình; định nghĩa API/event schema theo SEM-14. Firebase project ID còn chưa xác nhận, correlation chưa có ID thật phải nullable.
- **SEM-27:** nhận Node/npm, SDK đã thử và phương án kết nối; tạo server/lockfile/config mẫu thật trong task riêng. Kiểm lại health từ Android khi có thiết bị.
- **SEM-33:** cần config Android và token từ project thật; chưa coi app registration hoặc refresh đã hoạt động.
- **SEM-35:** cần gỡ B1, nhận runtime SEM-27 và thiết bị phù hợp; kiểm API/IAM/credential và response gửi thật. Host HTTPS 404 không thay được bước này.

B1 = thiếu xác nhận project/quyền/cấu hình Firebase; B2 = thiếu kiểm chứng ADB/thiết bị; B3 = runtime app/server/sender chưa có trên base. Task SEM-13 cho phép bàn giao audit có blocker; các blocker này vẫn chặn những phần tích hợp cần quyền hoặc thiết bị thật. Không thực hiện SEM-18/26/27/33/35 thay cho owner/task tương ứng trong lần này.
