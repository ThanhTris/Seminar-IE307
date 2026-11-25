# Ma trận luận điểm và evidence SEM-50

Tuấn (`mtuan2491`), 25/11/2026. Ma trận truy vết báo cáo LaTeX trên nền `db8dc5f`. SUMMARY của SEM-43 mô tả snapshot `007a1aa`. Ba pilot E01 ngày 20/11 được dẫn trực tiếp từ CSV SEM-45 và evidence SEM-42. [Bản LaTeX](../report/latex/main.tex) · [Yêu cầu SEM-50](../tasks/backlog/SEM-50.md)

## 1. Cách đọc trạng thái

| Trạng thái | Phạm vi dùng trong báo cáo |
|---|---|
| SOURCE_SUPPORTED | Có nguồn nghiên cứu hoặc documentation cho phát biểu đúng bối cảnh nguồn |
| DESIGN | Quyết định hoặc yêu cầu thiết kế của project đã có artifact |
| HYPOTHESIS | Ý tưởng nhóm cần đối chiếu với case và dữ liệu thực |
| OBSERVED_PILOT | Quan sát từ run pilot, kèm build, route và giới hạn evidence |
| NOT_RUN | Chưa quan sát ở phạm vi nêu trong claim |

Cột vị trí dùng chương và mục của bản LaTeX. Citation key theo references.bib đã tổng hợp. [Bibliography](../research/references.bib)

## 2. Ma trận claim, nguồn và evidence

| ID | Phát biểu được dùng | Nguồn và vị trí | Case / vị trí LaTeX | Evidence hoặc đầu vào tiếp theo | Trạng thái |
|---|---|---|---|---|---|
| P1-C1 | Server log Mendeley trong paper có 96.792/100.000 cycle rỗng | `Simon2017DiffsyncEnergy`, §7.2, tr. 8, [PAPER_1](../research/notes/PAPER_1.md) | E01, §1.3, Chương 3 | GET/applied/unchanged của workload demo để đối chiếu riêng | SOURCE_SUPPORTED |
| P1-C2 | Paper đề xuất kích hoạt sync theo thay đổi để giảm chu kỳ rỗng trong bối cảnh nghiên cứu | `Simon2017DiffsyncEnergy`, §6–7, [PAPER_1](../research/notes/PAPER_1.md) | E01/E02, §1.3, Chương 3 | Số request và điều kiện update được kiểm soát của nhóm | SOURCE_SUPPORTED |
| P1-C3 | `loopOnceMore` trong Mendeley gợi ý cần giữ tín hiệu tới lúc cycle đang bận | `Simon2017DiffsyncEnergy`, §7.1, tr. 7, [PAPER_1](../research/notes/PAPER_1.md) | E05-C, §1.3, Chương 3 | Overlap, signal/request IDs và cache tới target mới trong run của nhóm | HYPOTHESIS |
| P1-C4 | Demo dùng push để yêu cầu worker lấy snapshot hiện hành | Paper §4/§6, [SHARED_SYNC](mechanisms/SHARED_SYNC.md) và [API](API.md) | E02/E04, §2.7 | Payload và GET/correlation trong candidate, log thật từ SEM-45 | DESIGN |
| P2-C1 | Thí nghiệm alarm mỗi phút của paper ghi nhận thiếu lượt trên bốn thiết bị Android 7–9 | `GonzalezPerez2022AndroidScheduling`, §4.1, bảng 1–2, tr. 13, [PAPER_2](../research/notes/PAPER_2.md) | E01, §1.3 | Chu kỳ thực và cấu hình của demo để đối chiếu scheduler theo từng nền tảng | SOURCE_SUPPORTED |
| P2-C2 | Demo chọn WorkManager/FCM theo scope, paper sử dụng AlarmManager/wake lock/NTD | Paper §2–3 và [SCOPE](SCOPE.md) | E01/E03, §1.3, §2.2 | Pin công cụ và candidate theo phạm vi đã chọn | DESIGN |
| P2-C3 | Kết quả paper thay đổi theo thiết bị, ứng dụng và điều kiện đo | `GonzalezPerez2022AndroidScheduling`, §4.2–4.3, tr. 13–17, [PAPER_2](../research/notes/PAPER_2.md) | E01/E02 thiết bị, §2.8 | Evidence OPPO/emulator từ SEM-42/45 | SOURCE_SUPPORTED |
| P2-C4 | Hình 4 của paper lược 77 ngoại lệ để hiển thị, cần đọc cùng mô tả đầy đủ | `GonzalezPerez2022AndroidScheduling`, §4.2, tr. 14, [PAPER_2](../research/notes/PAPER_2.md) | E01–E06, §2.5–2.6 | CSV giữ timeout/late và bảng loại run có lý do | SOURCE_SUPPORTED |
| A1 | Periodic có repeat interval tối thiểu 15 phút, thời điểm chạy phụ thuộc constraints và hệ thống | `AndroidDefineWork`, mục Schedule periodic work và Effect of Constraints, [tài liệu Android](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work) | E01, §2.7 | Cấu hình thực và lần chạy tự nhiên trong log | SOURCE_SUPPORTED |
| A2 | Data-only v1 được route tới callback khi được delivery, công việc kéo dài cần cơ chế xử lý phù hợp lifecycle | `FirebaseReceiveMessages`, bảng message types và onMessageReceived, [tài liệu Firebase](https://firebase.google.com/docs/cloud-messaging/android/receive-messages) | E02, §2.7 | Receipt/enqueue/start/apply từ candidate | SOURCE_SUPPORTED |
| A3 | Normal priority có thể bị trì hoãn trong Doze | `FirebaseAndroidPriority` và `AndroidDozeStandby`, [priority](https://firebase.google.com/docs/cloud-messaging/android-message-priority), [Doze](https://developer.android.com/training/monitoring-device-state/doze-standby) | E03, §2.7–2.8 | Trạng thái OS và mốc event trước/trong/sau idle | SOURCE_SUPPORTED |
| D1 | HYBRID thêm cơ hội sync qua periodic khi ca E06 chủ động bỏ gửi push | [SCOPE](SCOPE.md), [PROTOCOL E06](../experiments/PROTOCOL.md), [SEM-40](evidence/SEM-40/FAULT_INJECTION.md) | E06, §2.7–2.8 | Skip đúng update/target, source PERIODIC và applied/timeout trong cửa sổ | HYPOTHESIS |
| D2 | Version guard được thiết kế để giữ version tăng đơn điệu khi response về khác thứ tự | [SHARED_SYNC](mechanisms/SHARED_SYNC.md), [CORE_CASES](evidence/SEM-39/CORE_CASES.md) | E05, §2.7 | Test logic và race trên candidate được ghi trong evidence | DESIGN |
| D3 | Kết quả cần tách accepted, received, enqueued, started và applied | [EVENT_SCHEMA](EVENT_SCHEMA.md), [MECHANISMS](MECHANISMS.md) | E02/E04, §2.5 | Run/device/signal/request/work/network IDs và clock có căn cứ | DESIGN |
| R1 | Inventory 23 pilot, 10 VALID/COMPLETED và 13 INVALID, thuộc 10 nhóm; 0 lượt main đủ điều kiện và latency main N/A | [CSV SEM-45](../experiments/results.csv), [CHECKS SEM-45](evidence/SEM-45/CHECKS.md), [SUMMARY SEM-43](../experiments/SUMMARY.md) §2–3 | E01–E06, §2.6 | `db8dc5f`, CSV v0.7.0; 20 run #29 + 3 run #35, gate false | OBSERVED_PILOT / MAIN NOT_RUN |
| R2 | OPPO run-03 có 5 chu kỳ và apply v5 tại 930021 ms từ đầu cửa sổ elapsed, ADB reverse, cấp nguồn USB | [Manifest](../experiments/pilots/run-sem42-oppo-e01-03/manifest.json), [events](../experiments/pilots/run-sem42-oppo-e01-03/events.jsonl), [CHECKS SEM-42](evidence/SEM-42/CHECKS.md) | E01, §2.6–2.8 | APK `814347F…`, thiếu boot ID và clock liên máy | OBSERVED_PILOT |
| R3 | OPPO run-02 bị hủy, app lên tiền cảnh và thiếu mốc mở; emulator 8d5816 có 2 chu kỳ, dùng host gateway | [Run-02](../experiments/pilots/run-sem42-oppo-e01-02/manifest.json), [emulator](../experiments/pilots/run-sem41-pilot-e01-1-20261120-8d5816/manifest.json), [provenance](../release/BUILD_MANIFEST.json) | E01, §2.6–2.8 | Run-02 INVALID, số chu kỳ trong cửa sổ null; gateway thuộc nhóm khác host HTTP | OBSERVED_PILOT |
| R4 | Audit SEM-41 ghi E03 periodic áp dụng sau thoát force-idle và E04 periodic áp dụng sau reconnect | [SUMMARY](../experiments/SUMMARY.md) §3–4, [E03 audit](../experiments/pilots/run-sem41-pilot-e03-1-20261115-dc9cc9/audit.json), [E04 kiểm reconnect](evidence/SEM-41/PR_REVIEW_FIXES.json) | E03/E04, §2.6 | Hai E03 và ba E04 trong loạt chạy lại của producer; clock/cấu hình giới hạn phạm vi | OBSERVED_PILOT |
| R5 | Hai E06 HYBRID của loạt chạy lại ghi deliberate skip và apply qua periodic | [SUMMARY](../experiments/SUMMARY.md) §3–4, [run aa16ca](../experiments/pilots/run-sem41-pilot-e06-1-20261116-aa16ca/events.jsonl), [run 8f734c](../experiments/pilots/run-sem41-pilot-e06-2-20261116-8f734c/events.jsonl) | E06, §2.6, Chương 3 | Pilot INJECTED, APK chưa cấu hình Firebase | OBSERVED_PILOT |
| R6 | Chưa có kết quả FCM E02 đầu cuối, E05 race trên thiết bị hoặc so sánh pin và latency giữa máy | [SUMMARY](../experiments/SUMMARY.md) §2, [CHECKS SEM-42](evidence/SEM-42/CHECKS.md), [CHECKS SEM-45](evidence/SEM-45/CHECKS.md) | E02/E05, §2.6, Chương 3 | Main/candidate và phép đo clock/năng lượng còn thiếu | NOT_RUN |

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

Khi có kết quả main, ghim revision, case, thiết bị, APK, cửa sổ và bằng chứng clock trước khi cập nhật các claim kết quả. SEM-43/48 có thể làm mới SUMMARY/biểu đồ theo inventory mới. Báo cáo hiện dẫn run-03 trực tiếp. [CHECKS SEM-50](evidence/SEM-50/CHECKS.md)
