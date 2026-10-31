# Môi trường Node, Firebase và kết nối — SEM-13

Kiểm tra ngày **31/10/2026 (UTC+7)** bởi Tâm (`HoaiTam`). Đây là hồ sơ môi trường trên máy macOS của Tâm, không thay thế hồ sơ Windows ở [ANDROID_BUILD.md](ANDROID_BUILD.md) hoặc hồ sơ thiết bị thuộc SEM-12. Kết quả và bàn giao: [SEM-13/CHECKS.md](../evidence/SEM-13/CHECKS.md).

**Kết luận:** Node/npm chạy được, Firebase Admin cài và khởi tạo được, HTTP loopback và HTTPS từ máy tới FCM/OAuth hoạt động. Chưa xác nhận Firebase project, Android app registration, IAM, credential và token thiết bị; chưa gửi FCM. ADB và SDK chưa tìm thấy trong các vị trí đã kiểm tra, nên LAN/ADB reverse và Internet/FCM trên thiết bị còn **Not run**.

## Môi trường thực tế

| Thành phần | Kết quả | Phạm vi kiểm chứng |
|---|---|---|
| OS | macOS `26.6.2`, build `25G83`, Darwin `25.6.0`, arm64 | `sw_vers`, `uname -srm` |
| Node.js | `v26.0.0`, `/opt/homebrew/bin/node` | Runtime đã chạy probe; không gọi đây là bản vá mới nhất |
| npm | `11.12.1`, `/opt/homebrew/bin/npm` | Cài được package; chọn npm cho phần server sắp triển khai |
| pnpm | `11.25.0` | Có trong runtime của Codex; không lấy làm điều kiện setup cho thành viên khác |
| Corepack / Yarn | Không tìm thấy qua PATH | Không bắt buộc với phương án npm |
| Firebase Admin | `14.5.0`, `engines.node >=22` | Metadata npm và cài thử; import app/messaging, initialize/delete thành công, không gọi API có xác thực |
| Firebase CLI / Google Cloud CLI | Không tìm thấy qua PATH | Không bắt buộc để chạy Admin SDK khi đã có credential local |
| ADB / Android SDK | ADB không có trên PATH; chưa có SDK tại `~/Library/Android/sdk`; `ANDROID_HOME`/`ANDROID_SDK_ROOT` chưa đặt | Chưa kết luận máy không có SDK ở vị trí khác; không chạy `adb devices` được |
| HTTP trên host | Listener tạm trên `127.0.0.1`, cổng tự cấp, GET trả `200` | Chỉ probe môi trường, không phải health API hay server của SEM-27 |

Package và lockfile thử nghiệm nằm trong `.local/sem13/sdk-probe/`, bị Git bỏ qua. SEM-27 cần tạo `server/package.json`, `package-lock.json` và script thật, khóa dependency khi triển khai và kiểm lại; probe này chưa chứng minh server TypeScript hoặc sender FCM hoạt động. Không cài hoặc nâng cấp Node/package manager toàn máy trong SEM-13.

[Firebase Admin setup](https://firebase.google.com/docs/admin/setup) mô tả runtime và cách khởi tạo SDK. Phiên bản package được đọc từ npm ngày kiểm tra, không suy từ tài liệu Android.

## Firebase project và quyền gửi test

Firebase project là nơi liên kết Android app với dịch vụ FCM và định danh mà server dùng khi gửi. Tài khoản GitHub không cấp quyền Firebase.

| Hạng mục | Trạng thái thực tế | Cần có trước khi test thật |
|---|---|---|
| Firebase project ID | Chưa xác nhận | Project riêng cho demo hoặc project nhóm đã đồng ý dùng; không tự đặt ID giả làm project thật |
| Android registration | Chưa xác nhận | Đăng ký package `com.thanhtris.seminarie307` đã chốt ở SEM-11 |
| FCM HTTP v1 API | Chưa kiểm quyền xem/bật API | Xác nhận `fcm.googleapis.com` được bật trong đúng project |
| Principal gửi / IAM | Chưa xác nhận | Service account của server có quyền `cloudmessaging.messages.create` trên project đích |
| Credential server | Chưa có ở các vị trí kiểm tra | Credential local cho principal đó; project đích và credential phải được đối chiếu |
| Cấu hình Android / registration token | Chưa có ở repo | `google-services.json` local đúng app và token của thiết bị test được cấp riêng |
| Gửi test / FCM message ID | **Not run / null** | Chỉ ghi accepted khi API trả thành công; chưa suy ra delivered hoặc applied |

Các biến `FIREBASE_PROJECT_ID`, `GCLOUD_PROJECT`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_APPLICATION_CREDENTIALS`, `FIREBASE_CONFIG`, `FIREBASE_TOKEN` chưa đặt trong tiến trình kiểm tra. Không có `.env`, `.env.local`, `google-services.json`, `app/google-services.json` trong checkout lúc bắt đầu. Không tìm thấy session Firebase CLI ở `~/.config/configstore/firebase-tools.json` hoặc ADC ở `~/.config/gcloud/application_default_credentials.json`. Chỉ kiểm sự hiện diện, không đọc/in credential. Các kiểm tra này không chứng minh nhóm chưa có project ở tài khoản/máy khác.

### Phương án thiết lập khi nhóm xác nhận project

1. Mở [Firebase Console](https://console.firebase.google.com/), chọn project nhóm hoặc tạo project dành riêng cho demo nếu chưa có. Ghi project ID và người quản lý; không cần thêm Firestore, Hosting hoặc Cloud Functions cho backend snapshot local.
2. Đăng ký Android app với package đã chốt. Cấp `google-services.json` trực tiếp cho người build Android qua kênh riêng; đặt ở module app local. Trí tích hợp Gradle theo SEM-23, Trang kiểm token/callback theo SEM-32/33.
3. Người có quyền quản lý project xác nhận FCM HTTP v1 API và cấp quyền cho service account gửi. Role Firebase Cloud Messaging API Admin (`roles/firebasecloudmessaging.admin`) chứa quyền `cloudmessaging.messages.create`; ghi role thực tế sau khi xem IAM, không coi việc xem console là bằng chứng gửi được. Tham chiếu [FCM HTTP v1](https://firebase.google.com/docs/cloud-messaging/send/v1-api) và [Firebase IAM roles](https://firebase.google.com/docs/projects/iam/roles-predefined-product#firebase-cloud-messaging-roles).
4. Với máy local, nếu dùng service-account JSON thì lưu `.local/secrets/fcm-service-account.json` và trỏ `GOOGLE_APPLICATION_CREDENTIALS` đến đường dẫn tuyệt đối. Không đưa khóa vào app Android, Git, log hoặc CHECKS; không dùng `FIREBASE_TOKEN` của Firebase CLI thay credential của Admin SDK. Cách cấp file được mô tả trong [Admin SDK setup](https://firebase.google.com/docs/admin/setup#initialize_the_sdk_in_non-google_environments).
5. Khi có app/device và sender SEM-35, test data-only normal priority theo [PLAN](../PLAN.md). Lưu run/version, accepted/rejected và message ID đã trả; callback nhận, worker chạy và cache áp dụng cần evidence Android riêng. Không dùng notification composer của console để thay cho bài test data-only.

Chưa thực hiện các thao tác tạo project, đăng ký app, cấp IAM hoặc tạo key trong lần audit này.

## Cấu hình local và cách cấp cho app/server

Mẫu dưới đây là hướng dẫn môi trường, chưa phải giao diện cấu hình runtime của server SEM-27. Chạy từ root repo sau khi đã nhận file local thật:

```sh
export FIREBASE_PROJECT_ID='replace-with-confirmed-project-id'
export GOOGLE_APPLICATION_CREDENTIALS="$PWD/.local/secrets/fcm-service-account.json"
```

Server SEM-27/35 dùng `projectId` đã xác nhận và `applicationDefault()`; không tự rơi về project mẫu khi thiếu cấu hình. File `.env` không được Node tự động đọc nếu chưa có bước nạp cấu hình; SEM-27 cần ghi rõ script hoặc cách export biến. Mọi ví dụ trong repo chỉ chứa placeholder.

| Cấu hình | Nơi giữ/cấp | Người nhận |
|---|---|---|
| Firebase project ID và package ID | Ghi giá trị đã xác nhận trong hồ sơ; hiện chỉ có package ID | SEM-26/27/33/35 |
| Service-account key / ADC | Local trên máy chạy server; cấp riêng cho người được quyền chạy sender | Tâm, người chạy demo được cấp quyền |
| `google-services.json` | File local trong module app; không commit kể cả đây không phải service-account private key | Trí/Trang, người build Android |
| Registration token | File riêng như `.local/secrets/device-token.txt`, cập nhật khi token refresh; không in lên log public | Sender SEM-35; cách đăng ký/refresh thuộc SEM-33 |
| Base URL của snapshot server | Cấu hình debug Android, chọn theo bảng kết nối bên dưới | Trí/Trung/Trang; runtime cuối do task tương ứng chốt |

`.gitignore` đã có `.env`, `.env.*`, `google-services.json`, `*service-account*.json`, `.local/`, `local.properties` và keystore. `.env.example` được phép track nhưng chỉ được chứa mẫu. Không cần commit cấu hình thật để bàn giao task.

## Kết nối server và Internet/FCM

Cổng `3000` dưới đây là ví dụ, chưa chốt HTTP contract hoặc cổng runtime thay SEM-26/27. Chỉ thử với health endpoint thật sau khi SEM-27 bàn giao.

| Đường kết nối | Thiết lập dự kiến | Trạng thái / điều kiện xác nhận |
|---|---|---|
| Host → server | Server bind `127.0.0.1`, client dùng `http://127.0.0.1:3000` | Probe host loopback đã Pass; API SEM-27 chưa có |
| Emulator → host | `http://10.0.2.2:3000` | Not run; cần emulator đang chạy trên chính máy host server |
| OPPO/emulator → ADB reverse | `adb -s <device-serial-local> reverse tcp:3000 tcp:3000`; app dùng `http://127.0.0.1:3000` | Not run; cần ADB và thiết bị ở trạng thái `device`; server phải chạy trên host ADB |
| OPPO → LAN | Server bind `0.0.0.0`; app dùng `http://<host-lan-ip>:3000` | Not run; cùng LAN, firewall cho cổng server, Wi-Fi không cách ly client; không dùng `0.0.0.0` làm URL client |
| Tunnel HTTPS | Chỉ fallback nếu LAN/reverse không dùng được; tunnel tới server local | Chưa cấu hình/Not run; ghi URL và cấu hình riêng theo run, không công khai route cập nhật thiếu bảo vệ |

Với `adb -s`, dùng serial thật local và chỉ lưu device alias trong evidence public. Xem mapping bằng `adb -s <device-serial-local> reverse --list`; sau thử gỡ đúng mapping bằng `adb -s <device-serial-local> reverse --remove tcp:3000`. Nếu ADB host khác máy server, mapping này không tự nối tới máy server còn lại.

Nếu dùng HTTP local, phần Android cần quyền Internet và cấu hình cho phép cleartext ở **debug** theo host/phương án đã chọn; chưa thay manifest hay security config của người khác trong SEM-13. Cơ sở mapping: [Android local server access](https://developer.android.com/develop/ui/views/layout/webapps/access-local-server).

Kiểm HTTPS từ host lúc **31/10/2026 19:30:24 (UTC+7)**, không dùng credential, không gửi message:

| Endpoint | HTTP / TLS | Diễn giải |
|---|---|---|
| `https://registry.npmjs.org/firebase-admin/latest` | `200`, verify result `0` | Host truy cập registry được |
| `https://fcm.googleapis.com/` | `404`, verify result `0` | DNS/TLS/HTTP tới FCM root hoạt động; root không phải send API |
| `https://oauth2.googleapis.com/` | `404`, verify result `0` | DNS/TLS/HTTP tới OAuth root hoạt động; chưa cấp access token |

HTTP 404 ở root **không** là FCM rejection hoặc bằng chứng quyền gửi. Probe HTTPS host không chứng minh thiết bị truy cập được FCM. ADB reverse chỉ nối cổng server local, không cung cấp Internet cho FCM. Thiết bị còn phải có Google Play services phù hợp, lấy token được và nhận data message thật; xem [Android FCM setup](https://firebase.google.com/docs/cloud-messaging/android/get-started) và [FCM network configuration](https://firebase.google.com/docs/cloud-messaging/network-configuration). Chưa xác nhận các điều kiện đó trên OPPO/emulator.

## Blocker và phạm vi bàn giao tiếp

| Blocker | Bước gỡ | Task chịu ảnh hưởng |
|---|---|---|
| B1 — Chưa xác nhận Firebase project/app/IAM/credential | Tâm nhận project ID, người quản lý và quyền/cấu hình local; kiểm API/IAM và ghi cập nhật có ngày | SEM-33/35 không thể chứng minh token/gửi thật; SEM-26/27 dùng cấu hình placeholder khi chuẩn bị |
| B2 — Chưa có ADB/thiết bị được kiểm tra trên máy Tâm | Nhận hồ sơ SEM-12, xác định máy host và đường ADB/SDK; chạy health từ từng thiết bị, kiểm Internet/FCM riêng | Kết nối Android ↔ server và E2E còn Not run |
| B3 — Chưa có runtime server/client trong nhánh gốc audit | SEM-27 bàn giao API thật, SEM-23/25/32/33 bàn giao app/core/messaging; chạy lại các bước liên quan | Không lấy probe môi trường làm bằng chứng M1 hoặc push hoàn tất |

SEM-19 nhận sự phân biệt giữa môi trường host đã kiểm và thiết bị/quyền chưa xác nhận. SEM-26/27 có thể dùng hồ sơ này làm đầu vào môi trường, nhưng không coi B1/B2 đã được giải quyết. SEM-33/35 phải kiểm lại cấu hình và quyền thật trước nghiệm thu tích hợp. Contract HTTP/events và code server vẫn thuộc task riêng, không triển khai trong SEM-13.

Các tài liệu web được đối chiếu ngày 31/10/2026; phiên bản, quyền và mạng phải ghi lại khi môi trường thay đổi.
