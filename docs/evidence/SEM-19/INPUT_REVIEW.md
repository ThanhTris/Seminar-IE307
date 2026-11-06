# SEM-19 - Tiếp nhận và đối chiếu đầu vào

Tuấn (`mtuan2491`), **06/11/2026 (UTC+7)**. Base tiếp nhận `a26d2706f2ad7588b054bd845386ddf20d4fab36` trên `codex/SEM-19-mechanisms-questions`, chứa main `319cc67cb44f2ca9abb7d7c2778650f1a14d3130`. Đây là bước 1/3 hoàn tất tài liệu SEM-19, không phải phép đo app hoặc đánh giá lại nghiệm thu task nguồn.

## 1. Bộ đầu vào đã có

Đối chiếu [task SEM-19](../../../tasks/backlog/SEM-19.md) và [catalog](../../../tasks/catalog.json): tám dependency hoàn tất đều Done. Đã kiểm sự hiện diện của **18 artifact/CHECKS** và đọc các phần được dùng trong bản tổng hợp. Hash dưới là Git blob của tài liệu chính ở base, không phải SHA của APK hay kết quả đo.

| Nguồn / owner | Tài liệu và CHECKS đã nhận | Blob tài liệu chính | Phần dùng cho SEM-19 |
|---|---|---|---|
| SEM-11 / Trí | [SCOPE](../../SCOPE.md), [ANDROID_BUILD](../../environment/ANDROID_BUILD.md), [CHECKS](../SEM-11/CHECKS.md) | `c65612bb58` | Phạm vi, package, cấu hình và giới hạn nền tảng. |
| SEM-12 / Vinh | [DEVICES](../../environment/DEVICES.md), [CHECKS](../SEM-12/CHECKS.md) | `c3202a3807` | Phân biệt emulator đã kiểm môi trường và OPPO chưa có máy để xác nhận. |
| SEM-13 / Tâm | [SERVER_FIREBASE](../../environment/SERVER_FIREBASE.md), [CHECKS](../SEM-13/CHECKS.md) | `96740daac8` | Phân biệt kiểm transport/công cụ với quyền gửi, token và FCM thật. |
| SEM-14 / Trí | [SHARED_SYNC](../../mechanisms/SHARED_SYNC.md), [CHECKS](../SEM-14/CHECKS.md) | `dd41cee03a` | Hai luồng cùng core; source/mode/run, version guard, transaction và race invariants. |
| SEM-15 / Trang | [SILENT_PUSH](../../mechanisms/SILENT_PUSH.md), [CHECKS](../SEM-15/CHECKS.md) | `9c3dc2931d` | Data-only/notification/mixed, callback, priority, các nguyên nhân trễ và câu hỏi phản biện. |
| SEM-16 / Vinh | [PROTOCOL](../../../experiments/PROTOCOL.md), [RUN_SCHEDULE](../../../experiments/RUN_SCHEDULE.md), [CHECKS](../SEM-16/CHECKS.md) | `5174f4e5b1` | Lifecycle, cửa sổ E01-E06, phân loại evidence và clock; lịch không thay run thật. |
| SEM-17 / Trung | [PERIODIC_FETCH](../../mechanisms/PERIODIC_FETCH.md), [CHECKS](../SEM-17/CHECKS.md) | `8db037da26` | Interval/constraint, unique periodic và thời điểm đăng ký khác thực thi. |
| SEM-18 / Tâm | [SERVER_FCM](../../mechanisms/SERVER_FCM.md), [CHECKS](../SEM-18/CHECKS.md) | `bf8d5a6e7a` | Persist khác send; accepted/received/start/apply và correlation nullable. |

Các tài liệu bổ sung đã đối chiếu: [API 2.0.0](../../API.md), [EVENT_SCHEMA 2.0.0](../../EVENT_SCHEMA.md), [SYNC_CORE_API](../../SYNC_CORE_API.md), [app build](../../../android/app/build.gradle.kts), [version catalog](../../../android/gradle/libs.versions.toml), [SyncWorkEnqueuer](../../../android/app/src/main/java/com/thanhtris/seminarie307/sync/SyncWorkEnqueuer.kt) và [remote datasource](../../../android/app/src/main/java/com/thanhtris/seminarie307/data/remote/SnapshotRemoteDataSource.kt).

## 2. Chi tiết phải chuẩn hóa trước khi tổng hợp

Một artifact đã nghiệm thu vẫn cần đối chiếu khi ghép vào tài liệu khác. Bảng này ghi cách SEM-19 sử dụng nguồn; không sửa file của owner nguồn hoặc tự tuyên bố có lỗi runtime đã tái hiện.

| Mã | Khác biệt hoặc rủi ro diễn giải ở nguồn | Quyết định trong bản SEM-19 |
|---|---|---|
| I1 | Sơ đồ SEM-15 ghi `GET /api/snapshot`; API 2.0.0 và remote datasource dùng `/api/bulletin` | Dùng **GET /api/bulletin** trong cả hai luồng; không tạo endpoint khác. |
| I2 | Blueprint SEM-15 fallback `mode` thành PUSH và có ví dụ policy REPLACE | Run/mode cần capture/validate theo schema; không gán run mặc định. Chỉ nói enqueue qua API chung; policy trong blueprint không được gọi là bảo đảm mất tín hiệu đã giải quyết. |
| I3 | Blueprint/sơ đồ SEM-15 ghi callback dưới 50ms, phần mô tả có các mốc 100ms hoặc 10-20 giây | Không dùng làm SLA hay cửa sổ được OS bảo đảm. Nói callback có thời gian ngắn và offload công việc kéo dài; [Firebase receive messages](https://firebase.google.com/docs/cloud-messaging/android/receive-messages) không cung cấp bảo đảm 50/100ms cho demo. |
| I4 | Ví dụ REPLACE và diễn giải version guard dễ bị dùng thành bảo đảm tuyệt đối cho race/process death | Version guard chống rollback; bảo toàn tín hiệu cần chiến lược và evidence riêng. [Managing work](https://developer.android.com/develop/background-work/background-tasks/persistent/how-to/manage-work) mô tả REPLACE hủy work cũ. Source shared enqueuer ở base dùng one-time `enqueue`, không chốt một unique policy cho mọi producer. |
| I5 | Một số câu SEM-15 nêu hành vi OPPO/ColorOS như đã quan sát | Theo hồ sơ SEM-12, OS/ColorOS và hành vi máy thật vẫn Not run. Chỉ nêu rủi ro OEM và case phải kiểm, không trình bày một lỗi OPPO đã đo. |
| I6 | Fixture sender hoặc sơ đồ có message ID minh họa; server/Android timestamps có thể lệch | Chỉ ghi ID thật hoặc null, không coi fixture là accepted thật. Giữ source/origin và accepted/received/enqueued/started/applied riêng; không ép thứ tự UTC liên máy. |

Callback có run/config xác định nhưng mode không cho phép vẫn có thể ghi receipt rồi `trigger_rejected`. Callback không xác định được run/config hợp lệ ghi diagnostic local ngoài tập experiment. Đây là quy tắc [EVENT_SCHEMA](../../EVENT_SCHEMA.md), không dùng fallback để tạo một run có vẻ đầy đủ.

Các luận điểm được giữ từ SEM-15: data-only khác notification bị tắt tiếng; baseline v1/normal; callback chuyển việc sang worker; Doze/force-stop/mạng/token có thể ảnh hưởng; FCM accepted chưa chứng minh receipt. [Tài liệu priority](https://firebase.google.com/docs/cloud-messaging/android-message-priority) và [define work requests](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work) được kiểm lại ngày 06/11 để giữ đúng phạm vi lập luận.

## 3. Ranh giới bằng chứng

- Hồ sơ thiết bị/môi trường và CHECKS đã có được dùng đúng ngày/revision của chúng. Không suy rằng SEM-19 đã lặp lại build, nhận push hoặc chạy Doze.
- [M1 SEM-28](../SEM-28/M1.md) ghi bàn giao manual end-to-end; manual setup không thay bằng chứng periodic/push tự nhiên. Bản SEM-19 vẫn tách mô hình mục tiêu với runtime đã được đo bởi task khác.
- Không cần chờ candidate hoặc E01-E06 để hoàn tất task giải thích cơ chế. Số liệu thực nghiệm, hành vi OEM và tính đúng của race vẫn cần evidence của các task sở hữu trước khi đưa thành kết quả trong bài nói.

## 4. Tiêu chí cho hai bước tiếp theo

Bước 2 hoàn tất MECHANISMS và QUESTIONS: dẫn đúng SEM-14..18; có hai luồng dễ theo dõi, thuật ngữ/lifecycle/version, payload routing, nguyên nhân trễ và ít nhất 10 đáp án có nguồn; không còn nhãn chờ SEM-15. Bước 3 kiểm link/cú pháp và render sơ đồ, ghi CHECKS cuối, đánh dấu acceptance đã thực hiện và bàn giao cho SEM-50.

**Kết luận bước 1:** đủ đầu vào để chốt tài liệu SEM-19; các chi tiết I1-I6 đã có hướng chuẩn hóa, không còn blocker nhận artifact. Kiểm này là review tài liệu/source, không phải runtime test.
