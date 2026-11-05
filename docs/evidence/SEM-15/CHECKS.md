# SEM-15 — CHECKS và bàn giao nghiệm thu

- **Người thực hiện:** Trang (`rosy179`).
- **Nhiệm vụ:** SEM-15 — Giải thích cơ chế silent push và giới hạn FCM.
- **Ngày lập và kiểm tra:** **05/11/2026 (UTC+7)**; thời gian thực tế hoàn thành task.
- **Hạn được giao trong kế hoạch:** **30/10/2026 18:00 (UTC+7)** (giữ nguyên mốc kế hoạch ban đầu).
- **Base commit:** `29ff1441a542b8e01da136a8360d5bfa5123d6a2` (`main`).
- **Nhánh làm việc:** `codex/SEM-15-silent-push`.
- **Đầu ra bàn giao:**
  - Tài liệu cơ chế: [docs/mechanisms/SILENT_PUSH.md](../../mechanisms/SILENT_PUSH.md)
  - Hồ sơ kiểm tra: [docs/evidence/SEM-15/CHECKS.md](CHECKS.md)
- **Loại kiểm chứng:** Đánh giá tài liệu kỹ thuật (Document Review), kiểm tra tính hợp lệ cú pháp Mermaid, kiểm tra liên kết nội bộ, và đối chiếu nguồn chính thức của Google / Android Framework. **Không có phép đo runtime trên thiết bị thật trong task này.**

---

## 1. Đầu vào đã tiếp nhận và đối chiếu

Theo [nhiệm vụ SEM-15](../../../tasks/backlog/SEM-15.md), task không có gate bắt đầu và không có gate hoàn tất chặn trước. Trước khi biên soạn tài liệu, đã nghiên cứu và đối chiếu các tài liệu nền trong kho lưu trữ:
- [Kế hoạch tổng thể PLAN.md](../../PLAN.md) và [Phạm vi demo SCOPE.md](../../SCOPE.md): Xác định rõ mục tiêu demo 15 phút, 3 mode thử nghiệm, và định hướng không hứa hẹn push tức thì.
- [Hợp đồng đồng bộ chung SHARED_SYNC.md](../../mechanisms/SHARED_SYNC.md) (SEM-14 do Trí bàn giao): Nắm vững luồng hội tụ của 3 trigger vào một `SyncWorker` và `SyncRepository` chung, nguyên tắc Room Transaction và version guard.
- [Đặc tả Server và FCM SERVER_FCM.md](../../mechanisms/SERVER_FCM.md) (SEM-18 do Tâm bàn giao): Nắm vững cấu trúc gửi tin từ server, `push_send_accepted` và các trường correlation.
- [Event Schema EVENT_SCHEMA.md](../../EVENT_SCHEMA.md) (SEM-26 do Tâm bàn giao): Khớp nối các mã sự kiện chuẩn hóa (`push_send_accepted`, `push_received`, `work_enqueued`, `work_started`, `snapshot_applied`).
- [Quy chuẩn kiểm thử EXPERIMENT_PROTOCOL.md](../../EXPERIMENT_PROTOCOL.md) và [Hồ sơ thiết bị DEVICES.md](../../environment/DEVICES.md): Hiểu rõ các trạng thái Doze, Standby Buckets và các hạn chế trên thiết bị thật (OPPO Find X9).
- [Danh mục nguồn nghiên cứu research/README.md](../../../research/README.md): Nắm vững các nguồn tài liệu D01–D08 của Android và Firebase.

---

## 2. Bảng kiểm tra tiêu chí nghiệm thu (Acceptance Checks)

| STT | Tiêu chí kiểm tra | Kết quả mong đợi (Expected) | Bằng chứng thực tế (Actual / Evidence) | Đánh giá |
|:---:|---|---|---|:---:|
| 1 | **Phân biệt data-only vs notification tắt tiếng** | Giải thích rõ ràng vì sao data-only không đồng nghĩa với một notification bị tắt tiếng | Mục 1 trong `SILENT_PUSH.md` phân tích sự khác nhau giữa User-facing notification có `IMPORTANCE_LOW` (vẫn vẽ UI) và Data-only message (không vẽ UI, đi thẳng vào tiến trình nền). Phân tích chi tiết bảng so sánh 3 loại payload: Notification, Data-only, Mixed | **Pass** |
| 2 | **Luồng dữ liệu đầu cuối (End-to-End Flow)** | Mô tả đầy đủ luồng từ Server → FCM → Callback → WorkManager → Snapshot API → Room Cache | Mục 2 có sơ đồ Mermaid Sequence Diagram 10 bước chi tiết, thể hiện rõ các mốc sự kiện, vai trò của GmsCore socket, callback `onMessageReceived`, WorkManager scheduling và Room Transaction atomic commit | **Pass** |
| 3 | **Giới hạn thực thi nền trong callback** | Nêu rõ giới hạn thời gian chạy của service và lý do bắt buộc bàn giao cho WorkManager | Mục 2.1 (Giai đoạn 3) nêu rõ cửa sổ thực thi của service chỉ dưới 15–20 giây; giải thích rủi ro ANR và process termination nếu chạy HTTP GET/DB nặng; chỉ ra quy tắc bàn giao cho WorkManager ngay lập tức | **Pass** |
| 4 | **Phân biệt Normal Priority vs High Priority** | Phân tích cơ chế hai mức ưu tiên, hành vi trong Doze và chính sách hạn ngạch của Google | Mục 3 phân tích bảng so sánh Normal vs High priority; giải thích cơ chế gom cụm trong Doze của Normal priority; nêu rõ rủi ro bị Google phạt hạ cấp (deprioritization) nếu lạm dụng High Priority cho silent push mà không có UI notification | **Pass** |
| 5 | **Không hứa hẹn push tức thì & Chỉ ra các trường hợp trễ/mất tin** | Chỉ ra ít nhất 5 trường hợp trì hoãn hoặc không nhận được push; khẳng định tính chất best-effort | Mục 4 phân tích sơ đồ và chi tiết 8 kịch bản gây trễ hoặc mất tin: (1) Doze Mode & Standby Buckets, (2) TTL Expiry, (3) Pending Queue Overflow (>100 tin), (4) Force-Stop state, (5) OEM Aggressive Battery Killers (ColorOS), (6) Socket Drop / NAT Timeout, (7) Rate Limits, (8) Token Invalidation | **Pass** |
| 6 | **Phân định ranh giới nhận thức** | Tách bạch rõ ràng FCM Accepted với App Received, Enqueued, Started và Cache Applied | Mục 5 lập bảng ma trận chi tiết cho 10 loại sự kiện; nhấn mạnh `push_send_accepted` không đồng nghĩa máy khách đã nhận tin, và `push_received` không đồng nghĩa dữ liệu đã vào Room cache | **Pass** |
| 7 | **Đặc tả Payload chuẩn FCM HTTP v1** | Cung cấp JSON fixture chuẩn cho HTTP v1 data-only, đúng kiểu chuỗi, có correlation | Mục 6 cung cấp JSON fixture hợp lệ: `message.token`, `message.data` (các trường `run_id`, `mode`, `source`, `version_hint`, `signal_id`), `message.android` (`priority: NORMAL`, `ttl: 600s`). Không chứa credential hay URL tùy ý | **Pass** |
| 8 | **Nguồn chính thức và phiên bản áp dụng** | Trích dẫn đầy đủ tài liệu chính thức từ Android Developers và Firebase; khóa phiên bản theo build | Mục 7 liệt kê bảng 9 nguồn chính thức (R01–R09) kèm link đối chiếu; đối chiếu phiên bản đã khóa trong `libs.versions.toml`: WorkManager `2.12.0`, Firebase BOM `35.1.0`, Room `2.8.5`, compile/target SDK 37 | **Pass** |
| 9 | **Tách biệt phụ lục EAP** | Không trộn lẫn các API thử nghiệm (EAP / BackgroundSync / v2 Preview) vào baseline v1 | Mục Phụ lục ở cuối tài liệu được tách biệt rõ ràng, giải thích bản chất EAP và lý do dự án chọn giữ FCM HTTP v1 tiêu chuẩn | **Pass** |
| 10 | **Cú pháp Mermaid và hiển thị định dạng** | Các sơ đồ Mermaid hiển thị chuẩn, không lỗi cú pháp, link nội bộ hợp lệ | Sơ đồ Flowchart và Sequence Diagram tuân thủ chuẩn GFM; toàn bộ link tương đối tới `PLAN.md`, `SCOPE.md`, `SHARED_SYNC.md`, `SERVER_FCM.md`, `libs.versions.toml` đều trỏ đúng file tồn tại | **Pass** |
| 11 | **Bảo mật và chuẩn định dạng văn bản** | Không chứa khóa bí mật, credentials hay khoảng trắng dư thừa | Tài liệu không chứa token thực, service account key hay thông tin nhạy cảm; không có lỗi trailing whitespace | **Pass** |
| 12 | **Kiểm thử Runtime trên thiết bị thật / Emulator** | Kiểm tra hành vi push thực tế trên Android runtime | SEM-15 là task nghiên cứu cơ chế và hợp đồng thiết kế. Các ca chạy máy thật, emulator và kết quả đo đạc thuộc về các task pilot/main runs downstream (SEM-32, SEM-34, SEM-41, SEM-42) | **Not run** (Theo phân công) |

---

## 3. Rà soát tình huống lý thuyết (Scenario Review — Document Contract)

| Kịch bản tình huống | Kỳ vọng hành vi hệ thống theo thiết kế | Đánh giá lý thuyết |
|---|---|:---:|
| **1. Server gửi Mixed Payload khi app ở background** | GmsCore tự động vẽ Notification lên System Tray; callback `onMessageReceived` **không** được gọi. Dữ liệu ngầm không được cập nhật nếu user không click | **Khớp đặc tả** (Lý do bắt buộc dùng Data-only) |
| **2. App nhận Data-only push khi đang ở Background** | GmsCore đánh thức `FirebaseMessagingService`; gọi `onMessageReceived`; không hiển thị bất kỳ UI thông báo nào | **Khớp đặc tả** (Đúng chuẩn Silent Push) |
| **3. Callback thực hiện HTTP GET kéo dài hơn 20s** | Hệ điều hành thu hồi wakelock; tiến trình có nguy cơ bị kill hoặc báo lỗi ANR; dữ liệu cache bị đứt đoạn | **Khớp đặc tả** (Lý do bắt buộc bàn giao WorkManager) |
| **4. Normal priority push đến khi máy trong Deep Doze** | Tín hiệu bị giữ lại trên FCM server hoặc GmsCore; không đánh thức thiết bị; chỉ chuyển phát khi máy vào maintenance window hoặc mở màn hình | **Khớp đặc tả** (Đúng thiết kế tiết kiệm năng lượng Android) |
| **5. High priority data push gửi dồn dập không có UI** | Google Play Services trừ điểm hạn ngạch (quota pool); tự động hạ cấp xuống Normal priority và áp delay lũy tiến | **Khớp đặc tả** (Chính sách FCM deprioritization) |
| **6. Thiết bị mất mạng vượt quá thời gian TTL** | Máy chủ FCM tự động xóa gói tin khỏi hàng đợi trên cloud; khi máy online lại, không có callback nào xảy ra | **Khớp đặc tả** (Quy luật Message Lifespan) |
| **7. Thiết bị bị người dùng Force Stop ứng dụng** | Android gán cờ `FLAG_EXCLUDE_STOPPED_PACKAGES`; GmsCore broadcast bị OS chặn đứng hoàn toàn; không có callback nào được gọi | **Khớp đặc tả** (Cơ chế bảo vệ của Android OS) |
| **8. Cơ chế tối ưu pin của OPPO ColorOS can thiệp** | Trình quản lý pin ColorOS chặn auto-launch hoặc đóng băng tiến trình ngầm; app không nhận được callback dù GmsCore có tin | **Khớp đặc tả** (Rào cản OEM thực tế được ghi nhận ở SEM-12) |

---

## 4. Kế hoạch bàn giao cho các task tiếp nhận (Handoff)

Đầu ra của SEM-15 trực tiếp mở khóa và cung cấp nền tảng kiến thức cho các task sau:

1. **[SEM-19](../../../tasks/backlog/SEM-19.md) (Tuấn — Tổng hợp mô hình cơ chế và câu hỏi phản biện):**
   - Sử dụng sơ đồ luồng dữ liệu 5 chặng và bảng đối chiếu mốc sự kiện tại Mục 2 và Mục 5 để tổng hợp vào `docs/MECHANISMS.md`.
   - Sử dụng 8 kịch bản trì hoãn/mất tin tại Mục 4 và cơ chế deprioritization tại Mục 3 để soạn ít nhất 4 câu hỏi phản biện trong `docs/QUESTIONS.md`.
2. **[SEM-22](../../../tasks/backlog/SEM-22.md) (Trang — Đối chiếu hai bài nghiên cứu với API push hiện hành):**
   - Sử dụng các phân tích về giới hạn Doze, TTL, và chi phí đánh thức của FCM Normal priority để đối chiếu với các phát hiện trong Paper 1 (SEM-20) và Paper 2 (SEM-21).
3. **[SEM-32](../../../tasks/backlog/SEM-32.md) (Trang — Triển khai callback FCM và enqueue sync):**
   - Sử dụng cấu trúc fixture payload tại Mục 6 để viết code phân giải `RemoteMessage.getData()`.
   - Tuân thủ nghiêm ngặt nguyên tắc chỉ ghi log `push_received` và gọi `WorkManager.enqueueUniqueWork` trong `onMessageReceived`, không nhét network call vào callback.
4. **[SEM-47](../../../tasks/backlog/SEM-47.md) (Trang — Viết phần silent push và lời dẫn demo 4 phút):**
   - Sử dụng lý lẽ giải thích vì sao "FCM Accepted không đồng nghĩa với Delivered" và ngưỡng quan sát 30 giây trong kịch bản trình bày demo.

---

## 5. Kết luận nghiệm thu

- Toàn bộ nội dung yêu cầu của SEM-15 đã được hoàn thành đầy đủ, đạt độ sâu kỹ thuật cao và bám sát các tiêu chuẩn của dự án.
- Tài liệu [docs/mechanisms/SILENT_PUSH.md](../../mechanisms/SILENT_PUSH.md) và hồ sơ [CHECKS.md](CHECKS.md) đã sẵn sàng phục vụ kiểm tra chéo và hợp nhất vào nhánh chính.
