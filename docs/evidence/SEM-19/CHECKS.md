# SEM-19 — CHECKS phần thực hiện độc lập

## Cập nhật hoàn tất theo ba bước - 06/11/2026

1. **Đã thực hiện:** [tiếp nhận/đối chiếu đủ đầu vào](INPUT_REVIEW.md), ghi cách chuẩn hóa các khác biệt giữa blueprint, contract và source.
2. **Tiếp theo:** chốt MECHANISMS/QUESTIONS, thay nhãn chờ SEM-15 bằng nội dung đã đối chiếu.
3. **Tiếp theo:** kiểm cuối, render sơ đồ, ghi bàn giao và acceptance; commit riêng sau từng bước theo yêu cầu người dùng.

Phần dưới giữ lịch sử bản chuẩn bị ngày 03/11. Trạng thái và kết quả cuối sẽ được cập nhật ở bước 3; không dùng các dòng Todo/thiếu SEM-15 của lịch sử để mô tả đầu vào ngày 06/11.

- Người thực hiện: Tuấn (`mtuan2491`).
- Ngày thực hiện: **03/11/2026 (UTC+7)**.
- Nhánh: `codex/SEM-19-mechanisms-questions`, theo mẫu `codex/SEM-XX-ten-ngan` trong [task board](../../../tasks/README.md).
- Base: `5e1c643550e35aee5f08cd74002be038ee3d4b9e` (`main` tại lúc tạo nhánh).
- Phạm vi người dùng giao: bắt đầu SEM-19, thực hiện trước phần không cần chờ đầu ra chưa bàn giao; không thực hiện SEM-20 trong nhánh này.
- GitHub Project đọc trực tiếp trong lần làm: SEM-19 **Todo / Sẵn sàng**, SEM-20 **Todo / Sẵn sàng**, SEM-15 **Todo / Sẵn sàng**. Snapshot cục bộ vẫn ghi SEM-19 Chuẩn bị trước; không tự sửa trường/dependency hoặc chạy đồng bộ toàn Project trong task này.
- Trạng thái đầu ra: **bản làm trước phần độc lập; chưa nghiệm thu toàn bộ SEM-19**. Không thay đổi workflow Status trên Project.

## Đầu ra trong nhánh

| Artifact | Nội dung đã viết | Phần để bổ sung sau |
|---|---|---|
| [MECHANISMS.md](../../MECHANISMS.md) | Thuật ngữ, hai sơ đồ trigger-to-cache, ranh giới event, shared core/version guard, lifecycle, phiên bản và bảng giả thuyết/evidence | Đối chiếu cuối phần silent push với artifact/CHECKS SEM-15; số liệu runtime chỉ từ task đo có provenance |
| [QUESTIONS.md](../../QUESTIONS.md) | 23 câu hỏi, đáp án ngắn, nguồn, case hoặc giới hạn; câu push có nhãn chờ đối chiếu | Đối chiếu câu 5–9 với SEM-15 trước bàn giao cuối |
| CHECKS này | Ghi base, input đã đọc, loại kiểm tra và ranh giới bàn giao | Cập nhật kiểm chứng cuối sau khi nhận đầu vào còn thiếu |

## Đầu vào đã đọc và giới hạn kiểm nhận

Các đường dẫn dưới tồn tại ở base; đọc tài liệu và CHECKS để tổng hợp, không chạy lại kiểm tra môi trường/runtime của owner khác.

| Nguồn | Artifact / CHECKS | Cách dùng trong SEM-19 |
|---|---|---|
| SEM-11 | [SCOPE](../../SCOPE.md), [ANDROID_BUILD](../../environment/ANDROID_BUILD.md), [CHECKS](../SEM-11/CHECKS.md) | Scope, package và baseline; phân biệt môi trường đã ghi với môi trường đang thực hiện |
| SEM-12 | [DEVICES](../../environment/DEVICES.md), [CHECKS](../SEM-12/CHECKS.md) | Emulator đã được kiểm môi trường; OPPO chưa có máy và hành vi OEM còn Not run |
| SEM-13 | [SERVER_FIREBASE](../../environment/SERVER_FIREBASE.md), [CHECKS](../SEM-13/CHECKS.md) | Phân biệt probe host với quyền Firebase, token và send thực tế |
| SEM-14 | [SHARED_SYNC](../../mechanisms/SHARED_SYNC.md), [CHECKS](../SEM-14/CHECKS.md) | Luồng chung, source/mode, version guard, UI đọc cache và giới hạn race |
| SEM-15 | Chưa có `docs/mechanisms/SILENT_PUSH.md` hoặc `docs/evidence/SEM-15/CHECKS.md` ở cây đang đọc; Project còn Todo | Chỉ soạn khung push từ SEM-14/18, contract và nguồn chính thức; không gọi đây là bàn giao của Trang |
| SEM-16 | [PROTOCOL](../../../experiments/PROTOCOL.md), [RUN_SCHEDULE](../../../experiments/RUN_SCHEDULE.md), [CHECKS](../SEM-16/CHECKS.md) | Lifecycle, E01–E06, clock/window/phase và giới hạn suy luận; không lấy phát hiện source cũ làm kết luận về build hiện tại |
| SEM-17 | [PERIODIC_FETCH](../../mechanisms/PERIODIC_FETCH.md), [CHECKS](../SEM-17/CHECKS.md) | Scheduler/constraint, lịch khác execution và kết quả review được ghi trước đó |
| SEM-18 | [SERVER_FCM](../../mechanisms/SERVER_FCM.md), [CHECKS](../SEM-18/CHECKS.md) | Accepted/received/start/apply, TTL, correlation, persist khác send |
| Contract tham chiếu | [API](../../API.md), [EVENT_SCHEMA](../../EVENT_SCHEMA.md), [CHECKS SEM-26](../SEM-26/CHECKS.md) | Dùng tên event/wire 2.0.0; không tuyên bố mọi module runtime đã tuân thủ |
| Source cấu hình | [app build](../../../android/app/build.gradle.kts), [version catalog](../../../android/gradle/libs.versions.toml) | Đọc package/SDK/dependency tại base, không build hoặc xác nhận APK |

## Nguồn chính thức đã đối chiếu

Đọc ngày 03/11/2026: Android Developers về [work requests](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work), [managing work](https://developer.android.com/develop/background-work/background-tasks/persistent/how-to/manage-work), [Doze](https://developer.android.com/training/monitoring-device-state/doze-standby), [process lifecycle](https://developer.android.com/guide/components/activities/process-lifecycle), [Room Transaction](https://developer.android.com/reference/androidx/room/Transaction), [SystemClock](https://developer.android.com/reference/android/os/SystemClock); Firebase về [nhận Android message](https://firebase.google.com/docs/cloud-messaging/android/receive-messages), [priority](https://firebase.google.com/docs/cloud-messaging/android-message-priority), [message lifespan](https://firebase.google.com/docs/cloud-messaging/customize-messages/setting-message-lifespan) và [điều kiện Android mở lại sau force-quit](https://firebase.google.com/docs/cloud-messaging/flutter/receive-messages). Nguồn Flutter cuối cùng chỉ dùng mô tả trạng thái nền tảng, không dùng API Flutter.

Nguồn đặt cạnh luận điểm trong hai artifact; không dùng lời giải của SEM-19 như số đo, không thêm payload/FCM ID hoặc run giả.

## Kiểm tra thực hiện

| Check | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| Nhánh và phạm vi diff | Nhánh SEM-19; chỉ ba artifact của task | Nhánh đúng tên/base; ba file mới của task, không có thay đổi file tracked; `project.md` đã untracked trước task được giữ nguyên | Pass — Git status/diff |
| Hai luồng / thuật ngữ / lifecycle | Giải thích được trigger → worker → cache mà không đọc source | MECHANISMS có hai sequence diagram, glossary, bảng event, lifecycle và version; tách mô hình với evidence | Pass — review nội dung |
| Câu hỏi phản biện | Ít nhất 10, có đáp án ngắn và nguồn | QUESTIONS có 23 câu; các câu silent push đánh dấu chờ SEM-15 | Pass — review nội dung |
| Schema và phạm vi version | Không trộn event v1/v2 hoặc coi contract là runtime | Dẫn API/event 2.0.0, source config tại base, baseline FCM v1; không chép ví dụ 600s thành TTL đo 24 giờ | Pass — review tài liệu |
| Missing input | Chỉ rõ phần còn chờ, không tự hoàn tất task phụ thuộc | Chưa có artifact SEM-15, chờ đối chiếu mục push/câu 5–9; không chỉnh phần owner khác | Pass — kiểm file và Project |
| Link / fence / định dạng | Các link nội bộ hợp lệ, fence cân, không whitespace lỗi | 94 link nội bộ và 1 fragment hợp lệ; 9 bảng đúng số cột; 23 câu đánh số liên tiếp đều có nguồn; UTF-8/newline/fence/whitespace và scan mẫu credential đạt | Pass — kiểm tĩnh 3 file |
| Mermaid | Hai diagram parse được | Mermaid 12.3.0 parse thành công cả hai sequence diagram | Pass — cú pháp; chưa render/kiểm layout |
| Build / FCM / run thiết bị | Không nhận Pass nếu không chạy | Không chạy app/server, không gửi push, không điều khiển thiết bị, không tạo dataset | **Not run — ngoài phạm vi phần tài liệu** |

Lần kiểm tĩnh dùng Node.js và Mermaid 12.3.0 cài trong `.local/sem19-tools/` với `--ignore-scripts`; không đổi dependency Android/server. Lệnh đã chạy: `node .local/sem19/validate-docs.mjs`, `git diff --check`, `git status --short`, `git branch --show-current`. Script và kết quả máy đọc được nằm ở `.local/sem19/`, được Git bỏ qua; đây là dụng cụ kiểm cục bộ, không phải artifact đo hoặc dependency bắt buộc của người nhận.

Để soát lại trên máy khác, kiểm các link relative từ thư mục chứa từng file, anchor trong MECHANISMS, 23 tiêu đề câu hỏi có nguồn và hai block `mermaid`; dùng `mermaid.parse` với phiên bản trên nếu cần lặp kiểm cú pháp. `git diff --check` chỉ xét diff tracked nên đã kiểm riêng trailing whitespace/newline/UTF-8 cho cả ba file mới. Không suy việc parse sơ đồ thành kiểm chứng runtime hoặc kiểm layout đã render.

## Bàn giao tiếp theo

SEM-50 có thể dùng bản này để chuẩn bị khung cơ chế và câu hỏi, với nhãn bản nháp và các giới hạn hiện có. Sau khi nhận **SEM-15 đúng artifact/revision/CHECKS**, đối chiếu phần push, cập nhật bảng nguồn/khác biệt và CHECKS rồi mới đề nghị nghiệm thu SEM-19. Trạng thái Sẵn sàng cho phép bắt đầu theo yêu cầu nhóm trưởng/người dùng, không thay thế artifact hoặc bằng chứng runtime.

Theo cập nhật của người dùng, phần độc lập đã thực hiện được bàn giao bằng commit cục bộ trên nhánh SEM-19, không push. Commit này chưa xác nhận hoàn tất toàn bộ SEM-19; không tạo PR hoặc thay trạng thái task.
