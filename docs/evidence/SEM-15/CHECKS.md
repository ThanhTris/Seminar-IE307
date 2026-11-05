# SEM-15 — CHECKS và Bàn giao Nghiệm thu Chuyên sâu

- **Người thực hiện:** Trang (`rosy179`).
- **Nhiệm vụ:** SEM-15 — Giải thích cơ chế silent push và giới hạn FCM.
- **Thuộc đề tài:** Seminar IE307 (Chủ đề 12: *Xử lý việc tìm nạp nền và thông báo đẩy im lặng, minh họa trên Android*).
- **Ngày lập và kiểm tra:** **05/11/2026 (UTC+7)**; thời gian thực tế hoàn thành task.
- **Hạn được giao trong kế hoạch:** **30/10/2026 18:00 (UTC+7)** (mốc deadline gán ban đầu).
- **Base commit:** `29ff1441a542b8e01da136a8360d5bfa5123d6a2` (`main`).
- **Nhánh làm việc:** `codex/SEM-15-silent-push`.
- **Đầu ra bắt buộc:**
  - Tài liệu cơ chế & nghiên cứu chuyên sâu: [docs/mechanisms/SILENT_PUSH.md](../../mechanisms/SILENT_PUSH.md)
  - Hồ sơ kiểm tra & nghiệm thu: [docs/evidence/SEM-15/CHECKS.md](CHECKS.md)
- **Loại kiểm chứng:** Đánh giá tài liệu kỹ thuật (Document Review), kiểm tra tính hợp lệ cú pháp Mermaid, kiểm tra liên kết nội bộ, và đối chiếu nguồn chính thức của Google / Android Framework. **Không có phép đo runtime trên thiết bị thật trong task này.**

---

## 1. Đầu vào đã tiếp nhận và đối chiếu

Theo [nhiệm vụ SEM-15](../../../tasks/backlog/SEM-15.md), task không có gate bắt đầu và không có gate hoàn tất chặn trước. Trước khi biên soạn tài liệu, đã nghiên cứu và đối chiếu các tài liệu nền trong kho lưu trữ:
- [Kế hoạch tổng thể PLAN.md](../../PLAN.md) và [Phạm vi demo SCOPE.md](../../SCOPE.md): Xác định rõ mục tiêu demo 15 phút, 3 mode thử nghiệm, và định hướng không hứa hẹn push tức thì.
- [Hợp đồng đồng bộ chung SHARED_SYNC.md](../../mechanisms/SHARED_SYNC.md) (SEM-14 do Trí bàn giao): Nắm vững luồng hội tụ của 3 trigger vào một `SyncWorker` và `SyncRepository` chung, nguyên tắc Room Transaction và version guard.
- [Đặc tả Server và FCM SERVER_FCM.md](../../mechanisms/SERVER_FCM.md) (SEM-18 do Tâm bàn giao): Nắm vững cấu trúc gửi tin từ server, `push_send_accepted` và các trường correlation.
- [Event Schema EVENT_SCHEMA.md](../../EVENT_SCHEMA.md) (SEM-26 do Tâm bàn giao): Khớp nối các mã sự kiện chuẩn hóa (`push_send_accepted`, `push_received`, `work_enqueued`, `work_started`, `snapshot_applied`).
- [Quy chuẩn kiểm thử EXPERIMENT_PROTOCOL.md](../../EXPERIMENT_PROTOCOL.md), [Ma trận Protocol 1.0.0](../../../experiments/PROTOCOL.md) và [Hồ sơ thiết bị DEVICES.md](../../environment/DEVICES.md): Hiểu rõ các trạng thái Doze, Standby Buckets và các hạn chế trên thiết bị thật (OPPO Find X9 chạy ColorOS).
- [Danh mục nguồn nghiên cứu research/README.md](../../../research/README.md): Nắm vững các nguồn tài liệu D01–D08 của Android và Firebase.

---

## 2. Bảng kiểm tra tiêu chí nghiệm thu (Acceptance Checks)

| STT | Tiêu chí kiểm tra | Kết quả mong đợi (Expected) | Bằng chứng thực tế (Actual / Evidence) | Đánh giá |
|:---:|---|---|---|:---:|
| 1 | **Phân biệt data-only vs notification tắt tiếng** | Giải thích rõ ràng vì sao data-only không đồng nghĩa với một notification bị tắt tiếng | Mục 1 trong `SILENT_PUSH.md` phân tích sự khác biệt về mặt kiến trúc hệ điều hành giữa User-facing notification có `IMPORTANCE_LOW` (vẫn vẽ UI trên Notification Shade) và Data-only message (không vẽ UI, routing thẳng vào tiến trình ngầm). Bảng so sánh toàn diện 3 loại payload: Notification, Data-only, Mixed | **Pass** |
| 2 | **Kiến trúc hạ tầng kết nối & Modem vô tuyến** | Mô tả rõ cơ chế kết nối socket dài hạn của GmsCore và trạng thái RRC của modem di động | Mục 2 phân tích cơ chế multiplexed TCP socket trên cổng 5228 của GmsCore, cơ chế Heartbeat Alarms, và chuyển trạng thái RRC (`IDLE` -> `CONNECTED` -> `TAIL`) cùng tác động của Tail Energy đến thời lượng pin | **Pass** |
| 3 | **Luồng dữ liệu đầu cuối (End-to-End Flow)** | Mô tả đầy đủ luồng từ Server → FCM → Callback → WorkManager → Snapshot API → Room Cache | Mục 3 có sơ đồ Mermaid Sequence Diagram 10 bước chi tiết, thể hiện rõ các mốc sự kiện, vai trò của GmsCore socket, callback `onMessageReceived`, WorkManager scheduling và Room Transaction atomic commit | **Pass** |
| 4 | **Giới hạn thực thi nền trong callback** | Nêu rõ giới hạn thời gian chạy của service và lý do bắt buộc bàn giao cho WorkManager | Mục 4 nêu rõ cửa sổ thực thi an toàn của service chỉ dưới 10–20 giây; giải thích rủi ro CPU sleep, ANR và Process termination (`SIGKILL` từ AMS) nếu chạy HTTP GET/DB nặng; chỉ ra quy tắc bàn giao cho WorkManager dưới 100ms | **Pass** |
| 5 | **Phân biệt Normal Priority vs High Priority** | Phân tích cơ chế hai mức ưu tiên, hành vi trong Doze và chính sách hạn ngạch của Google | Mục 5 phân tích sơ đồ và bảng so sánh Normal vs High priority; giải thích cơ chế gom cụm trong Doze của Normal priority; nêu rõ cơ chế tính điểm quota pool và nguy cơ bị Google phạt hạ cấp (deprioritization) nếu gửi ngầm liên tục mà không có UI notification | **Pass** |
| 6 | **Không hứa hẹn push tức thì & Chỉ ra 8 nguyên nhân trễ/mất tin** | Chỉ ra ít nhất 5 trường hợp trì hoãn hoặc không nhận được push; khẳng định tính chất best-effort | Mục 6 phân tích sơ đồ và chi tiết 8 kịch bản gây trễ hoặc mất tin: (1) Doze Mode & Standby Buckets, (2) TTL Expiry (24h), (3) Pending Queue Overflow (>100 tin), (4) Force-Stop state (`FLAG_EXCLUDE_STOPPED_PACKAGES`), (5) OEM Aggressive Battery Killers (ColorOS trên OPPO Find X9), (6) Socket Drop / NAT Timeout, (7) Rate Limits (240 msg/min), (8) Token Invalidation | **Pass** |
| 7 | **Phân định ranh giới nhận thức** | Tách bạch rõ ràng FCM Accepted với App Received, Enqueued, Started và Cache Applied | Mục 7 lập bảng ma trận chi tiết cho 10 loại sự kiện; nhấn mạnh `push_send_accepted` không đồng nghĩa máy khách đã nhận tin, và `push_received` không đồng nghĩa dữ liệu đã vào Room cache | **Pass** |
| 8 | **Đặc tả Payload chuẩn FCM HTTP v1 & Code Blueprints** | Cung cấp JSON fixture chuẩn và mã nguồn mẫu cho Android Service và Node.js Admin SDK | Mục 8 cung cấp mã nguồn hoàn chỉnh Kotlin `AppFirebaseMessagingService` cho SEM-32 và Node.js TypeScript `sendSilentPushSignal` cho SEM-35, lưu ý bẫy cú pháp TTL (mili-giây vs chuỗi giây) và Priority (chữ thường vs chữ hoa) | **Pass** |
| 9 | **Bộ 10 câu hỏi phản biện chuyên sâu (Defense Q&A)** | Cung cấp ít nhất 8 câu hỏi kèm câu trả lời kỹ thuật có chiều sâu để chuẩn bị bảo vệ | Mục 9 cung cấp trọn bộ 10 câu hỏi phản biện kèm đáp án chi tiết phục vụ Tuấn (SEM-19) tổng hợp vào `docs/QUESTIONS.md` | **Pass** |
| 10 | **Nguồn chính thức và phiên bản áp dụng** | Trích dẫn đầy đủ tài liệu chính thức từ Android Developers, Firebase và AOSP; khóa phiên bản theo build | Mục 10 liệt kê danh mục 9 nguồn tài liệu chính thức kèm link URL truy cập; đối chiếu phiên bản đã khóa trong `libs.versions.toml`: WorkManager `2.12.0`, Firebase BOM `35.1.0`, Room `2.8.5`, compile/target SDK 37 | **Pass** |
| 11 | **Tách biệt phụ lục EAP** | Không trộn lẫn các API thử nghiệm (EAP / BackgroundSync / v2 Preview) vào baseline v1 | Mục Phụ lục ở cuối tài liệu được tách biệt rõ ràng, giải thích bản chất EAP và lý do dự án chọn giữ FCM HTTP v1 tiêu chuẩn | **Pass** |
| 12 | **Cú pháp Mermaid và hiển thị định dạng** | Các sơ đồ Mermaid hiển thị chuẩn, không lỗi cú pháp, link nội bộ hợp lệ | 4 sơ đồ Mermaid (Flowchart, Sequence, StateDiagram) tuân thủ chuẩn GFM; toàn bộ link tương đối tới các file trong dự án đều trỏ đúng file tồn tại | **Pass** |
| 13 | **Bảo mật và chuẩn định dạng văn bản** | Không chứa khóa bí mật, credentials hay khoảng trắng dư thừa | Tài liệu không chứa token thực, service account key hay thông tin nhạy cảm; không có lỗi trailing whitespace | **Pass** |
| 14 | **Kiểm thử Runtime trên thiết bị thật / Emulator** | Kiểm tra hành vi push thực tế trên Android runtime | SEM-15 là task nghiên cứu cơ chế và hợp đồng thiết kế. Các ca chạy máy thật, emulator và kết quả đo đạc thuộc về các task pilot/main runs downstream (SEM-32, SEM-34, SEM-41, SEM-42) | **Not run** (Theo phân công) |

---

## 3. Rà soát tình huống lý thuyết (Scenario Review — Document Contract)

| Kịch bản tình huống | Kỳ vọng hành vi hệ thống theo thiết kế | Đánh giá lý thuyết |
|---|---|:---:|
| **1. Server gửi Mixed Payload khi app ở background** | GmsCore tự động vẽ Notification lên System Tray; callback `onMessageReceived` **không** được gọi. Dữ liệu ngầm không được cập nhật nếu user không click | **Khớp đặc tả** (Lý do bắt buộc dùng Data-only) |
| **2. App nhận Data-only push khi đang ở Background** | GmsCore đánh thức `FirebaseMessagingService`; gọi `onMessageReceived`; không hiển thị bất kỳ UI thông báo nào | **Khớp đặc tả** (Đúng chuẩn Silent Push) |
| **3. Callback thực hiện HTTP GET kéo dài hơn 20s** | Hệ điều hành thu hồi wakelock; tiến trình có nguy cơ bị kill hoặc báo lỗi ANR; dữ liệu cache bị đứt đoạn | **Khớp đặc tả** (Lý do bắt buộc bàn giao WorkManager) |
| **4. Normal priority push đến khi máy trong Deep Doze** | Tín hiệu bị giữ lại trên FCM server hoặc GmsCore; không đánh thức thiết bị; chỉ chuyển phát khi máy vào maintenance window hoặc mở màn hình | **Khớp đặc tả** (Đúng thiết kế tiết kiệm năng lượng Android) |
| **5. High priority data push gửi dồn dập không có UI** | Google Play Services trừ điểm hạn ngạch (quota pool); tự động hạ cấp xuống Normal priority và áp delay lũy tiến | **Khớp đặc tả** (Chính sách FCM deprioritization) |
| **6. Thiết bị mất mạng vượt quá thời gian TTL 24h** | Máy chủ FCM tự động xóa gói tin khỏi hàng đợi trên cloud; khi máy online lại, không có callback nào xảy ra | **Khớp đặc tả** (Quy luật Message Lifespan) |
| **7. Thiết bị bị người dùng Force Stop ứng dụng** | Android gán cờ `FLAG_EXCLUDE_STOPPED_PACKAGES`; GmsCore broadcast bị OS chặn đứng hoàn toàn; không có callback nào được gọi | **Khớp đặc tả** (Cơ chế bảo vệ của Android OS) |
| **8. Cơ chế tối ưu pin của OPPO ColorOS can thiệp** | Trình quản lý pin ColorOS chặn auto-launch hoặc đóng băng tiến trình ngầm; app không nhận được callback dù GmsCore có tin | **Khớp đặc tả** (Rào cản OEM thực tế được ghi nhận ở SEM-12) |
| **9. Hai gói push đến đảo lộn thứ tự (Version 11 trước, 10 sau)** | Version Guard trong Room Transaction áp dụng Version 11; khi Version 10 tới sẽ bị từ chối và ghi log `snapshot_stale` | **Khớp đặc tả** (Bảo vệ tính đơn điệu của cache) |
| **10. Mạng bị ngắt sau khi callback enqueue WorkManager** | WorkManager lưu yêu cầu vào SQLite nội bộ; khi có mạng trở lại (`NetworkType.CONNECTED`), worker mới chạy fetch snapshot | **Khớp đặc tả** (Bảo đảm tính bền vững của WorkManager) |

---

## 4. Kế hoạch bàn giao cụ thể cho các thành viên và task kế thừa (Handoff)

Đầu ra chuyên sâu của SEM-15 trực tiếp mở khóa và cung cấp nền tảng kỹ thuật vững chắc cho các thành viên trong nhóm:

1. **[SEM-19](../../../tasks/backlog/SEM-19.md) (Tuấn — Tổng hợp mô hình cơ chế và câu hỏi phản biện):**
   - Sử dụng sơ đồ luồng dữ liệu 10 bước tại Mục 3 và bảng đối chiếu mốc sự kiện tại Mục 7 để tổng hợp vào `docs/MECHANISMS.md`.
   - Trực tiếp kế thừa trọn vẹn **Bộ 10 câu hỏi phản biện chuyên sâu tại Mục 9** để đưa vào `docs/QUESTIONS.md`, phục vụ diễn tập thuyết trình và phản biện.

2. **[SEM-22](../../../tasks/backlog/SEM-22.md) (Trang — Đối chiếu hai bài nghiên cứu với API push hiện hành):**
   - Sử dụng các phân tích chuyên sâu về trạng thái modem vô tuyến RRC (`IDLE` vs `CONNECTED`), chi phí năng lượng đuôi (Tail Energy) tại Mục 2, và giới hạn Doze Mode tại Mục 5 & 6 để đối chiếu với bài báo nghiên cứu thứ nhất (SEM-20) và bài báo nghiên cứu thứ hai (SEM-21).

3. **[SEM-32](../../../tasks/backlog/SEM-32.md) (Trang — Triển khai callback FCM và enqueue sync trên Android):**
   - Sử dụng mã nguồn khung Kotlin mẫu chuẩn tại Mục 8.1 (`AppFirebaseMessagingService.kt`) để hiện thực hóa adapter nhận push trên Android.
   - Tuân thủ nghiêm ngặt nguyên tắc chỉ ghi log `push_received` và gọi `WorkManager.enqueueUniqueWork` trong callback dưới 50–100ms.

4. **[SEM-35](../../../tasks/backlog/SEM-35.md) (Tâm — Làm CLI gửi FCM data-only normal priority từ backend):**
   - Sử dụng bảng đối chiếu cú pháp và mã nguồn Node.js TypeScript mẫu tại Mục 8.2 để xây dựng công cụ CLI gửi push chuẩn xác, tránh lỗi cú pháp về định dạng TTL (mili-giây) và Priority (`normal` viết thường).

5. **[SEM-47](../../../tasks/backlog/SEM-47.md) (Trang — Viết phần silent push và lời dẫn demo 4 phút):**
   - Sử dụng luận điểm cốt lõi "FCM Accepted không đồng nghĩa với Delivered" và phân tích 8 rào cản kỹ thuật tại Mục 6 để giải thích hiện tượng trễ trong kịch bản demo 4 phút.

6. **[SEM-16](../../../experiments/PROTOCOL.md) & [SEM-34/42](../../../docs/environment/DEVICES.md) (Vinh — Pilot & Main Experiment Protocol trên OPPO/Emulator):**
   - Khớp nối các điều kiện thử nghiệm: TTL 24 giờ (`86400s`), cờ trạng thái `stopped=true` khi force-stop, và hành vi đóng băng tiến trình của ColorOS trên OPPO Find X9.

---

## 5. Kết luận nghiệm thu

- Toàn bộ nội dung yêu cầu của SEM-15 đã được hoàn thành với mức độ chi tiết học thuật vượt trội, minh chứng đầy đủ nguồn tài liệu chính thức, và cung cấp giá trị sử dụng trực tiếp cho toàn bộ 5 thành viên còn lại trong nhóm.
- Tài liệu [docs/mechanisms/SILENT_PUSH.md](../../mechanisms/SILENT_PUSH.md) và hồ sơ [CHECKS.md](CHECKS.md) hoàn toàn sẵn sàng cho quá trình kiểm tra chéo và hợp nhất vào nhánh chính.
- PR #13 đã được nhóm trưởng `ThanhTris` review, nghiệm thu và merge vào `main` tại merge commit `8f85e8f496eb52fcff34b419b78a9c24097435f3`.
- Trạng thái task SEM-15 trên GitHub Project 3 đã được cập nhật sang **Done** (item `PVTI_lAHOCnL5Fs4BpUDUzhEiW8w`).
