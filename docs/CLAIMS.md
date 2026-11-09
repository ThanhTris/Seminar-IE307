# WIP — SEM-50 chưa hoàn thành, chưa đủ điều kiện merge

Tuấn (`mtuan2491`), 09/11/2026. Bảng này chốt cách dùng nguồn cho báo cáo dự thảo. **Kết quả thực nghiệm còn chờ CSV/CHECKS SEM-45 và SUMMARY/CHECKS SEM-43.** Mỗi claim được cập nhật cùng vị trí evidence khi nhận bàn giao. [Yêu cầu SEM-50](../tasks/backlog/SEM-50.md)

## 1. Cách đọc trạng thái

| Trạng thái | Phạm vi dùng trong báo cáo |
|---|---|
| SOURCE_SUPPORTED | Có nguồn nghiên cứu hoặc documentation cho phát biểu đúng bối cảnh nguồn |
| DESIGN | Quyết định hoặc yêu cầu thiết kế của project đã có artifact |
| HYPOTHESIS | Ý tưởng nhóm cần đối chiếu với case và dữ liệu thực |
| PENDING_RUN | Đang chờ dữ liệu để xác nhận kết quả của demo |

Vị trí REPORT ở bảng dưới dùng số mục để người viết ghép đúng nội dung. Citation key theo references.bib đã tổng hợp. [Bibliography](../research/references.bib)

## 2. Ma trận claim, nguồn và evidence

| ID | Phát biểu được dùng | Nguồn và vị trí | Case / vị trí REPORT | Evidence hoặc đầu vào tiếp theo | Trạng thái |
|---|---|---|---|---|---|
| P1-C1 | Server log Mendeley trong paper có 96.792/100.000 cycle rỗng | `Simon2017DiffsyncEnergy`, §7.2, tr. 8, [PAPER_1](../research/notes/PAPER_1.md) | E01, REPORT §2 và §6 | GET/applied/unchanged của workload demo để đối chiếu riêng | SOURCE_SUPPORTED |
| P1-C2 | Paper đề xuất kích hoạt sync theo thay đổi để giảm chu kỳ rỗng trong bối cảnh nghiên cứu | `Simon2017DiffsyncEnergy`, §6–7, [PAPER_1](../research/notes/PAPER_1.md) | E01/E02, REPORT §2 và §6 | Số request và điều kiện update được kiểm soát của nhóm | SOURCE_SUPPORTED |
| P1-C3 | `loopOnceMore` trong Mendeley gợi ý cần giữ tín hiệu tới lúc cycle đang bận | `Simon2017DiffsyncEnergy`, §7.1, tr. 7, [PAPER_1](../research/notes/PAPER_1.md) | E05-C, REPORT §2 và §6 | Overlap, signal/request IDs và cache tới target mới trong run của nhóm | HYPOTHESIS |
| P1-C4 | Demo dùng push để yêu cầu worker lấy snapshot hiện hành | Paper §4/§6, [SHARED_SYNC](mechanisms/SHARED_SYNC.md) và [API](API.md) | E02/E04, REPORT §3 | Payload và GET/correlation trong candidate, log thật từ SEM-45 | DESIGN |
| P2-C1 | Thí nghiệm alarm mỗi phút của paper ghi nhận thiếu lượt trên bốn thiết bị Android 7–9 | `GonzalezPerez2022AndroidScheduling`, §4.1, bảng 1–2, tr. 13, [PAPER_2](../research/notes/PAPER_2.md) | E01, REPORT §2 | Chu kỳ thực và cấu hình của demo để đối chiếu scheduler theo từng nền tảng | SOURCE_SUPPORTED |
| P2-C2 | Demo chọn WorkManager/FCM theo scope, paper sử dụng AlarmManager/wake lock/NTD | Paper §2–3 và [SCOPE](SCOPE.md) | E01/E03, REPORT §2 và §3 | Pin công cụ và candidate theo phạm vi đã chọn | DESIGN |
| P2-C3 | Kết quả paper thay đổi theo thiết bị, ứng dụng và điều kiện đo | `GonzalezPerez2022AndroidScheduling`, §4.2–4.3, tr. 13–17, [PAPER_2](../research/notes/PAPER_2.md) | E01/E02 thiết bị, REPORT §6 | Evidence OPPO/emulator từ SEM-42/45 | SOURCE_SUPPORTED |
| P2-C4 | Hình 4 của paper lược 77 ngoại lệ để hiển thị, cần đọc cùng mô tả đầy đủ | `GonzalezPerez2022AndroidScheduling`, §4.2, tr. 14, [PAPER_2](../research/notes/PAPER_2.md) | E01–E06, REPORT §4 và §6 | CSV giữ timeout/late và bảng loại run có lý do | SOURCE_SUPPORTED |
| A1 | Periodic có repeat interval tối thiểu 15 phút, thời điểm chạy phụ thuộc constraints và hệ thống | `AndroidDefineWork`, mục Schedule periodic work và Effect of Constraints, [tài liệu Android](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work) | E01, REPORT §3 | Cấu hình thực và lần chạy tự nhiên trong log | SOURCE_SUPPORTED |
| A2 | Data-only v1 được route tới callback khi được delivery, công việc kéo dài cần cơ chế xử lý phù hợp lifecycle | `FirebaseReceiveMessages`, bảng message types và onMessageReceived, [tài liệu Firebase](https://firebase.google.com/docs/cloud-messaging/android/receive-messages) | E02, REPORT §3 | Receipt/enqueue/start/apply từ candidate | SOURCE_SUPPORTED |
| A3 | Normal priority có thể bị trì hoãn trong Doze | `FirebaseAndroidPriority` và `AndroidDozeStandby`, [priority](https://firebase.google.com/docs/cloud-messaging/android-message-priority), [Doze](https://developer.android.com/training/monitoring-device-state/doze-standby) | E03, REPORT §3 và §6 | Trạng thái OS và mốc event trước/trong/sau idle | SOURCE_SUPPORTED |
| D1 | HYBRID thêm cơ hội sync qua periodic khi ca E06 chủ động bỏ gửi push | [SCOPE](SCOPE.md), [PROTOCOL E06](../experiments/PROTOCOL.md), [SEM-40](evidence/SEM-40/FAULT_INJECTION.md) | E06, REPORT §3 và §6 | Skip đúng update/target, source PERIODIC và applied/timeout trong cửa sổ | HYPOTHESIS |
| D2 | Version guard được thiết kế để giữ version tăng đơn điệu khi response về khác thứ tự | [SHARED_SYNC](mechanisms/SHARED_SYNC.md), [CORE_CASES](evidence/SEM-39/CORE_CASES.md) | E05, REPORT §3 | Test logic và race trên candidate được ghi trong evidence | DESIGN |
| D3 | Kết quả cần tách accepted, received, enqueued, started và applied | [EVENT_SCHEMA](EVENT_SCHEMA.md), [MECHANISMS](MECHANISMS.md) | E02/E04, REPORT §4 | Run/device/signal/request/work/network IDs và clock có căn cứ | DESIGN |
| R1 | Tỷ lệ cập nhật và duration của demo sẽ được báo theo từng nhóm run hợp lệ | [EXPERIMENT_PROTOCOL](EXPERIMENT_PROTOCOL.md) | E01–E06, REPORT §5 | `experiments/results.csv`, CHECKS SEM-45 và SUMMARY SEM-43 đang chờ | PENDING_RUN |
| R2 | Đối chiếu OPPO với emulator phụ thuộc cấu hình và evidence của từng thiết bị | [DEVICES](environment/DEVICES.md), [PROTOCOL](../experiments/PROTOCOL.md) | E01/E02, REPORT §5 và §6 | Run OPPO hoặc NOT_RUN/lý do do SEM-42 bàn giao | PENDING_RUN |

## 3. Cách tiếp nhận các luận điểm từ SEM-22

SEM-22 đã có ma trận nghiên cứu/API và CHECKS trên main. Khi tổng hợp, SEM-50 dùng diễn đạt đã đối chiếu sau đây để giữ phạm vi claim phù hợp với evidence hiện có. [API_CROSSCHECK](../research/notes/API_CROSSCHECK.md), [CHECKS SEM-22](evidence/SEM-22/CHECKS.md)

| Vị trí nguồn cần lưu ý | Cách dùng trong báo cáo SEM-50 |
|---|---|
| §3.1 và P1-C2 trình bày mức pin từ paper | Gắn kết luận với phương pháp/giả định ở PAPER_1 §5. Báo cáo tập trung vào giả thuyết lượng công việc và độ mới dữ liệu theo scope |
| §3.2/P1-C3 gắn REPLACE + version guard với bảo đảm process death/race | Dùng yêu cầu giữ tín hiệu và E05-C. Source shared enqueuer ở base gọi enqueue one-time. Khả năng bảo toàn tín hiệu được kiểm bằng test/candidate riêng |
| §4.2/P2-C2 mô tả alarm bị cấm rộng trên Android mới | Dẫn quyết định chọn WorkManager/FCM trong SCOPE và sự khác nhau về cơ chế/phương pháp giữa paper và demo |
| §4.3/P2-C3 suy hành vi MIUI sang OPPO | Trình bày biến thiên thiết bị trong paper và yêu cầu thu evidence OPPO riêng tại R2 |
| P2-C4 đánh giá đạo đức từ việc lược ngoại lệ trên hình | Ghi rõ tác giả đã nêu 77 ngoại lệ khi hiển thị, bảo toàn timeout/late trong dữ liệu nhóm và công bố quy tắc loại run |
| §6 gọi HYBRID bảo đảm tức thời và bù mọi push thất lạc | Giữ D1 là giả thuyết có case E06 và điều kiện scheduler/network/background được ghi cụ thể |
| Phụ lục EAP đưa ra điều kiện tài khoản/OEM | Chốt baseline message.android v1 theo scope và phân biệt với AndroidConfigV2 xuất hiện trong documentation hiện tại |

## 4. Truy vết bibliography và bước cập nhật

Paper 2 dùng key chuẩn **GonzalezPerez2022AndroidScheduling** từ metadata của SEM-21. Tên `GonzalezPerez2022ReliableScheduling` xuất hiện trong tài liệu SEM-22 được ánh xạ về cùng DOI khi tổng hợp. Bibliography giữ một record cho mỗi paper. Bản preprint 2016 của Paper 1 là phiên bản của cùng nghiên cứu. [Metadata paper 1](../research/metadata/paper-1.bib), [metadata paper 2](../research/metadata/paper-2.bib)

Khi nhận SEM-43/45, cập nhật mỗi dòng R1/R2 và các giả thuyết bằng run ID, nhóm, source commit, cửa sổ, vị trí CSV/SUMMARY và trạng thái kết luận. Các claim của paper/documentation tiếp tục giữ bối cảnh và citation của nguồn. [CHECKS SEM-50](evidence/SEM-50/CHECKS.md)
