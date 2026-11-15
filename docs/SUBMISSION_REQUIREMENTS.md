# Yêu cầu nộp Seminar của giảng viên — đối chiếu ngày 11/11/2026

Chủ đề 12: **Xử lý việc tìm nạp nền và thông báo đẩy im lặng**. Tài liệu này ghi lại yêu cầu giảng viên đã gửi và task nào chịu trách nhiệm cho từng mục. Đây là danh sách yêu cầu, chưa phải xác nhận các đầu ra đã có.

Nguyên tắc của giảng viên: seminar không chỉ giới thiệu công nghệ mà phải **chứng minh nhóm đã hiểu và triển khai/minh họa được chủ đề**. Phạm vi demo hiện tại (periodic WorkManager, FCM data-only, hybrid, có log thực nghiệm) phù hợp nguyên tắc này; phần thiếu nằm ở hình thức báo cáo và gói nộp.

## 1. Bố cục báo cáo bắt buộc

Báo cáo viết bằng **template LaTeX của môn**, ngoài các phần cơ bản của template phải có:

| Mục báo cáo | Nội dung bắt buộc | Nguồn trong repo | Task |
|---|---|---|---|
| 1. Giới thiệu đề tài | Bài toán, khái niệm fetch nền và silent push, mục tiêu | `docs/SCOPE.md`, `docs/MECHANISMS.md` | SEM-50 |
| 2. Hiện thực đề tài — Môi trường thực hiện | Máy build, emulator, OPPO, Node, Firebase | `docs/ENVIRONMENT.md`, `docs/environment/` | SEM-50 |
| 2 — Công cụ/công nghệ sử dụng | Kotlin, Compose, Room, WorkManager, FCM, Node.js | `docs/PLAN.md`, `docs/environment/ANDROID_BUILD.md` | SEM-50 |
| 2 — Các bước cài đặt | Clone, cài app và server | `docs/SETUP.md`, `docs/setup/` | SEM-50 |
| 2 — Cấu hình | Firebase, `.env`, token, mode | `docs/setup/`, `docs/PUSH.md`, `docs/PERIODIC.md` | SEM-50 |
| 2 — Các bước triển khai/thực thi | Chạy server, đổi snapshot, gửi push, chạy ca thử | `docs/DEMO_RUNBOOK.md` (SEM-52), `experiments/PROTOCOL.md` | SEM-50 |
| 2 — Kết quả đầu ra | Số liệu, timeline, giới hạn | `experiments/SUMMARY.md` (SEM-43), `experiments/results.csv` (SEM-45) | SEM-50 |
| 2 — Minh họa chức năng/thành phần chính | Ảnh màn hình app, timeline, sơ đồ kiến trúc, ba mode | `docs/SYNC_CORE_API.md`, `slides/inputs/` | SEM-50 |
| 2 — Vấn đề gặp phải và cách xử lý | Trễ periodic, Doze, token refresh, tín hiệu trùng, giới hạn OEM | `docs/evidence/*/CHECKS.md`, `docs/QUESTIONS.md` | SEM-50 |
| 2 — Video demo | Link video trên Drive | `release/VIDEO_MANIFEST.json` (SEM-53) | SEM-53 quay và upload; SEM-55 chèn link |
| 3. Kết luận và khuyến nghị | Dùng cơ chế nào khi nào, hạn chế, khuyến nghị | `docs/CLAIMS.md` | SEM-50 |
| Phụ lục: Bảng phân công công việc | Ai làm task nào | `docs/TEAM_ASSIGNMENTS.md`, `tasks/catalog.json` | SEM-50 |

Hai bài nghiên cứu đã đọc (SEM-20/21/22) đặt trong phần giới thiệu hoặc kết luận, không thay cho chương Hiện thực. Lưu ý của giảng viên về việc tập trung vào thiết kế thực nghiệm chỉ áp dụng cho nhóm có đồ án cuối kỳ theo hướng nghiên cứu.

## 2. Gói nộp bắt buộc

| Thành phần | Đầu ra trong repo | Task |
|---|---|---|
| PDF báo cáo | `report/seminar-ie307.pdf` | SEM-50, SEM-55 biên dịch lại sau khi chèn link |
| PPTX | `slides/seminar-ie307.pptx` | SEM-51 |
| Mã nguồn code | `android/`, `server/`, `experiments/scripts/` | SEM-55 đóng gói |
| Mã nguồn LaTeX | `report/latex/` | SEM-50 |
| Demo | APK (SEM-52) và video demo (SEM-53) | SEM-52, SEM-53 |
| File ZIP | `IE307.R11_Seminar_Nhom<X>.ZIP` | SEM-55 |

Quy tắc đóng gói:

- Nén tất cả thành một file ZIP, đặt tên đúng `IE307.R11_Seminar_NhomX.ZIP` với X là số nhóm.
- File hoặc video dung lượng lớn upload lên Drive, **chia sẻ quyền truy cập cho email giảng viên nêu trong thông báo seminar**, và đưa link vào file báo cáo. Email không ghi trong repo public.
- ZIP không chứa `.env`, service-account key, `google-services.json`, `node_modules/`, `build/`, `.gradle/` hay `.local/`.
- ZIP không commit vào repo; SEM-55 ghi SHA256 và nơi nộp trong `release/MANIFEST.json`.

## 3. Phần đã lệch so với yêu cầu tại ngày 11/11/2026

| Yêu cầu | Hiện trạng | Cách sửa |
|---|---|---|
| Báo cáo LaTeX theo template | Task SEM-50 chỉ yêu cầu `report/REPORT.md`; repo chưa có file `.tex` hay template | Đổi đầu ra SEM-50 sang `report/latex/` và PDF |
| Bố cục 3 chương và phụ lục | Bản nháp trên nhánh `codex/SEM-50-report-claims` theo bố cục bài nghiên cứu 8 mục, thiếu cài đặt, cấu hình, triển khai, vấn đề gặp phải, phụ lục phân công | SEM-50 sắp lại theo bảng mục 1 |
| Video demo là mục phải nộp | SEM-53 chỉ gọi là video dự phòng, chưa yêu cầu Drive và chia sẻ cho giảng viên | Bổ sung vào SEM-53 |
| ZIP đúng tên, link Drive trong báo cáo | SEM-55 chỉ có manifest và README | Bổ sung đóng gói ZIP và checklist vào SEM-55 |
| Bảng phân công đúng thực tế | PLAN, TEAM_ASSIGNMENTS, PRESENTATION_PLAN, EXPERIMENT_PROTOCOL còn ghi người phụ trách cũ | Đã sửa theo `tasks/catalog.json` và Project |

## 4. Thông tin còn thiếu

- Số nhóm X để đặt tên ZIP.
- File template LaTeX của môn chưa có trong repo; SEM-50 cần nhận template trước khi chuyển nội dung.
- Lịch: SEM-34, 36, 37, 41–45 và 50 đã quá hạn ghi trong `tasks/DEADLINES.md`; báo cáo không có mục Kết quả đầu ra thật nếu các lần chạy chính chưa xong.
