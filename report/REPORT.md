# WIP — SEM-50 chưa hoàn thành, chưa đủ điều kiện merge

# Tìm nạp nền và thông báo đẩy im lặng trên Android

Seminar IE307, chủ đề 12. Tuấn (`mtuan2491`) tổng hợp ngày 09/11/2026 trên nhánh `codex/SEM-50-report-claims`, base main `54d48c2ed48588b59b16cc652a8d1b77912c15b7`.

**Bản thảo đang chờ kết quả từ SEM-43 và SEM-45.** Các phần bối cảnh, nghiên cứu liên quan, cơ chế và phương pháp đã được soạn từ đầu vào có sẵn. Phần kết quả, đối chiếu thực nghiệm và kết luận cuối được chốt sau khi nhận CSV, SUMMARY và CHECKS. Trưởng nhóm review phần chuẩn bị và chờ cập nhật hoàn tất trước khi merge task. [CHECKS SEM-50](../docs/evidence/SEM-50/CHECKS.md)

## 1. Bài toán và câu hỏi nghiên cứu

Demo là bảng tin Android nhận snapshot có version từ server, lưu vào Room và hiển thị cache. Ba mode PERIODIC, PUSH và HYBRID sử dụng chung sync core. Mục tiêu của seminar là quan sát cơ chế kích hoạt, thời điểm worker chạy và thời điểm dữ liệu thật sự commit trong điều kiện thiết bị cụ thể. Phạm vi tập trung vào tính đúng và hành vi cập nhật, cùng các giới hạn của công việc nền. [SCOPE](../docs/SCOPE.md)

Ba câu hỏi định hướng các phần cơ chế và thực nghiệm

1. Một thay đổi trên server được nối tới received/enqueued/started/applied như thế nào trong từng mode?
2. Idle, mất mạng và trạng thái lifecycle liên quan đến các mốc đó ra sao trên cấu hình đã đo?
3. Trong ca HYBRID chủ động bỏ gửi push, periodic có áp dụng được target trong cửa sổ quan sát hay kết thúc với outcome nào?

Các câu hỏi được gắn với E01–E06 và ma trận claim để giữ rõ phần cần evidence. [CLAIMS](../docs/CLAIMS.md), [PROTOCOL](../experiments/PROTOCOL.md)

## 2. Hai nghiên cứu liên quan

### 2.1. Kích hoạt đồng bộ theo thay đổi

Simon và cộng sự nghiên cứu differential synchronisation trong Mendeley trên iOS. Tỷ lệ cycle rỗng ở server log thúc đẩy cách kích hoạt theo thay đổi. Với bảng tin, nhóm dùng ý tưởng đó để đặt giả thuyết về lượng công việc và giữ tín hiệu khi sync đang bận. Năng lượng và workload trong paper giữ bối cảnh thiết bị/phương pháp gốc. [@Simon2017DiffsyncEnergy] [PAPER_1, §3–7](../research/notes/PAPER_1.md)

### 2.2. Lịch dự kiến và lần thực hiện quan sát được

González-Pérez và cộng sự khảo sát AlarmManager/NTD trên Android 7–11. Completeness và các chỉ số thời gian của paper thúc đẩy nhóm ghi đủ lần thực hiện, ngoại lệ và điều kiện thiết bị. Bảng tin dùng WorkManager/FCM và chỉ số trigger-to-cache riêng. Sự khác nhau về công cụ, workload và đồng hồ được giữ trong phần đối chiếu. [@GonzalezPerez2022AndroidScheduling] [PAPER_2, phương pháp và kết quả](../research/notes/PAPER_2.md)

### 2.3. Vai trò trong lập luận của seminar

| Nghiên cứu | Quyết định / câu hỏi của nhóm | Case để đối chiếu |
|---|---|---|
| Paper 1 | Theo dõi phần sync tạo dữ liệu mới và yêu cầu giữ tín hiệu tới khi worker bận | E01/E02 và E05-C |
| Paper 2 | Ghi lịch, work start, cửa sổ, điều kiện OS và mọi outcome hợp lệ | E01/E03/E04 và đối chiếu thiết bị |

Các liên hệ là giả thuyết và lựa chọn phương pháp của nhóm. CLAIMS §3 ghi cách tiếp nhận từng luận điểm SEM-22 khi ghép báo cáo, gồm phạm vi race/version guard, biến thiên OEM, mô hình HYBRID và cách xử lý ngoại lệ trên hình của paper. [CLAIMS](../docs/CLAIMS.md), [API_CROSSCHECK](../research/notes/API_CROSSCHECK.md)

## 3. Mô hình cơ chế và kiến trúc

### 3.1. Hai luồng tới cache

Luồng PERIODIC bắt đầu từ đăng ký lịch, tiếp đến cơ hội thực thi do WorkManager/hệ thống quyết định, worker lấy snapshot và repository kiểm version trong transaction Room. Lịch đã đăng ký và thời điểm bắt đầu được quan sát riêng. Documentation quy định repeat interval tối thiểu 15 phút và mô tả ảnh hưởng của constraints/hệ thống. [@AndroidDefineWork] [Define work requests](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work)

Luồng PUSH trong baseline của project dùng FCM HTTP v1 data-only normal priority. Sau delivery, callback kiểm input và chuyển công việc qua worker. Bảng routing v1 và lifecycle của callback được đối chiếu với documentation Firebase. [@FirebaseReceiveMessages] [Receive messages](https://firebase.google.com/docs/cloud-messaging/android/receive-messages)

Normal priority có thể bị trì hoãn trong Doze. Nhóm ghi trạng thái OS, thời điểm nhận và worker start riêng khi đọc ca idle. [@FirebaseAndroidPriority; @AndroidDozeStandby] [Message priority](https://firebase.google.com/docs/cloud-messaging/android-message-priority), [Doze](https://developer.android.com/training/monitoring-device-state/doze-standby)

Hai sơ đồ và glossary chi tiết đã có trong MECHANISMS. Endpoint snapshot theo contract là GET `/api/bulletin`, API/event schema 2.0.0. Repository lấy dữ liệu ngoài transaction, đọc lại cached version trong transaction rồi ghi outcome phù hợp. UI quan sát cache, source MANUAL được gắn nhãn khi chuẩn bị hoặc chẩn đoán. [MECHANISMS](../docs/MECHANISMS.md), [SHARED_SYNC](../docs/mechanisms/SHARED_SYNC.md), [API](../docs/API.md)

### 3.2. Mốc quan sát và ý nghĩa

| Mốc | Điều event xác nhận | Dữ liệu nối chuỗi |
|---|---|---|
| `server_updated` | Snapshot mới đã persist | Run/device/update/version |
| `push_send_accepted` | Kết quả chấp nhận send quan sát được | Signal/send attempt/FCM message ID khi có |
| `push_received` | Callback Android ghi nhận tín hiệu | Signal, run/device và hint |
| `work_enqueued` | One-time work được chấp nhận xếp lịch | Request/work IDs |
| `work_started` | Lượt worker đã bắt đầu | Request/work/attempt |
| Fetch start/completed | GET được bắt đầu và kết thúc theo instrumentation | Network call ID, HTTP status/outcome |
| `snapshot_applied` | Snapshot và metadata version đã commit vào Room | Request/work/attempt, data/cache version |

Schema phân biệt origin và source. Request ID nối logical sync qua retry, work ID có thể dùng qua nhiều periodic cycle, signal IDs nối sender/callback. Từng giá trị timestamp được giữ theo nguồn để phân tích clock. [EVENT_SCHEMA](../docs/EVENT_SCHEMA.md)

### 3.3. HYBRID và version guard

HYBRID là thiết kế có hai trigger đi qua cùng core. Giả thuyết E06 là periodic có thêm cơ hội lấy target khi việc gửi push cho update đó được chủ động bỏ qua. Cách dựng ca dùng event skip của SEM-40 và log phía app trong cửa sổ được protocol quy định. [CLAIMS D1](../docs/CLAIMS.md), [FAULT_INJECTION](../docs/evidence/SEM-40/FAULT_INJECTION.md)

Version guard được thiết kế để kiểm version mới/bằng/cũ tại transaction. Phần kiểm bảo toàn tín hiệu và race dùng test logic cùng case overlap E05-C trên candidate. Bằng chứng cần nối request/version và điều kiện overlap của lần chạy cụ thể. [CORE_CASES](../docs/evidence/SEM-39/CORE_CASES.md), [PROTOCOL E05](../experiments/PROTOCOL.md)

## 4. Phương pháp thực nghiệm

### 4.1. Nhận dạng và cô lập run

Mỗi run giữ case/subscenario/repetition, phase, mode, device alias, build/commit/APK/config và window. Các lượt được reset/drain, giữ version server tăng đơn điệu và ghi baseline cache. Setup MANUAL được phân loại ngoài cửa sổ nền. Cleanup, run bị nhiễu và lý do loại được ghi cùng manifest. [PROTOCOL](../experiments/PROTOCOL.md), [hướng dẫn exporter](../experiments/README.md)

### 4.2. Thiết kế ca theo protocol

| Case | Thiết kế dự kiến | Window / số lượt theo protocol | Evidence chính cần nhận |
|---|---|---|---|
| E01 | Periodic tự nhiên trên emulator và OPPO | 1 phiên 90 phút/máy, mục tiêu ít nhất 3 cycle | Đăng ký lịch, cycle/request IDs, target/cache |
| E02 | Push trên emulator và OPPO | 5 lượt/máy, 120 giây/lượt | Send/receipt/start/apply và UI reopen |
| E03 | Doze, từng trigger trên emulator | 2 lượt/trigger, 5 phút baseline + 20 phút idle + 10 phút sau thoát | Xác nhận OS idle và phase event |
| E04 | Offline, từng trigger trên emulator | 3 lượt/trigger, offline 2 phút + 30 phút periodic hoặc 5 phút push sau reconnect | Transport, reconnect, event và outcome |
| E05 | Duplicate, hint cũ và overlap trên emulator | 3 lượt/kịch bản, 15 phút/lượt, test logic đi kèm | Signal/request/version, overlap và hook INJECTED |
| E06 | HYBRID chủ động bỏ gửi push trên emulator | 2 lượt, 45 phút/lượt | Skip đúng target/update, source PERIODIC và cache |

Bảng là thiết kế dự kiến nhận từ SEM-16. Số lượt thực nhận, run hợp lệ và kết quả được điền ở mục 5 sau bàn giao. [PROTOCOL E01–E06](../experiments/PROTOCOL.md)

### 4.3. Chỉ số và cách báo cáo

- Tỷ lệ cập nhật trong window dùng số run có applied đúng target trên tổng run hợp lệ cùng case/subscenario/device/mode/build/config/phase. E01 được giữ là một session với số cycle riêng.
- Timeout, failure, unknown và late completion được báo riêng. Run bị loại khỏi thống kê có lý do, các dữ liệu nguồn được giữ để kiểm.
- Duration nội bộ Android dùng elapsed realtime trên cùng device/boot khác null. Latency liên máy cần clock calibration và uncertainty có căn cứ. Giá trị thiếu được để trống trong CSV và giải thích trong report phân tích.
- Median/min/max đi kèm n_complete/n_total và n_measured của từng metric. Các mốc nhận push, chờ worker và sync được tách theo correlation.
- GET/retry/applied được đếm theo instrumentation thực. Phạm vi demo dùng các chỉ số lượng công việc và độ mới dữ liệu đã khai.

Định nghĩa và phép tính cuối được đối chiếu với phiên bản parser/CHECKS SEM-45 lúc nhận CSV. Bản công cụ làm trước hiện nằm trên nhánh SEM-45 riêng. [EXPERIMENT_PROTOCOL](../docs/EXPERIMENT_PROTOCOL.md), [Task SEM-45](../tasks/backlog/SEM-45.md)

## 5. Kết quả đang chờ bàn giao

**PENDING_INPUT — mục này chưa có kết quả tập chính để nghiệm thu SEM-50.**

| Đầu vào | Task cung cấp | Trạng thái tại base báo cáo | Việc cần làm khi nhận |
|---|---|---|---|
| `experiments/results.csv` và CHECKS | SEM-45 | CHỜ BÀN GIAO | Kiểm run/group/build/window/clock/flags và lệnh tái lập |
| `experiments/SUMMARY.md` và CHECKS | SEM-43 | CHỜ BÀN GIAO | Đối chiếu nhận định với CSV và evidence nguồn |
| Run/candidate/device provenance | Đi cùng bộ bàn giao SEM-43/45 | CHỜ BÀN GIAO | Pin commit, APK hash, cấu hình và nhãn phase |

| Nhóm kết quả | n_valid / n_complete | Outcome / latency / counts | Evidence |
|---|---|---|---|
| E01 theo device/build/config | CHỜ | CHỜ | Run IDs và CSV cần nhận |
| E02 theo device/build/config | CHỜ | CHỜ | Run IDs và CSV cần nhận |
| E03 theo trigger và phase idle | CHỜ | CHỜ | OS milestones và clock mapping cần nhận |
| E04 theo trigger và reconnect | CHỜ | CHỜ | Transport/mốc reconnect cần nhận |
| E05 theo subscenario/injection | CHỜ | CHỜ | Overlap, test logic và target cần nhận |
| E06 HYBRID skip theo build/config | CHỜ | CHỜ | Skip và periodic apply/timeout cần nhận |

Repo nền có hai lượt pilot periodic SEM-29 được bàn giao theo format Android legacy-room-v1. Chúng là dữ liệu pilot đã ghi trong CHECKS SEM-29. Việc đưa vào phân tích chính cần quyết định có provenance và khả năng đọc dữ liệu theo protocol/parser. Các hàng kết quả trên chờ bộ bàn giao SEM-43/45. [CHECKS SEM-29](../docs/evidence/SEM-29/CHECKS.md)

## 6. Thảo luận và giới hạn cần đối chiếu

| Vấn đề | Nội dung đã soạn từ nguồn | Phần cần dữ liệu chính |
|---|---|---|
| Công việc không tạo dữ liệu mới | Paper 1 gợi ý xem workload, thay đổi và chu kỳ rỗng | GET/applied/unchanged cùng điều kiện update và window |
| Lịch và thời điểm chạy | Paper 2 và documentation thúc đẩy ghi cả schedule/start | Cycle tự nhiên, jitter, idle/network và số mẫu |
| Tín hiệu đến lúc worker bận | Thiết kế yêu cầu giữ cập nhật tới khi core đang xử lý | Overlap có chứng cứ, signal IDs và version cuối ở E05-C |
| HYBRID | Hai trigger dùng chung core, E06 là ca bỏ gửi có kiểm soát | Skip đúng target và outcome trong cửa sổ |
| Thiết bị / OS | Phương pháp paper và cấu hình demo khác nhau | OPPO hoặc NOT_RUN có lý do, metadata của từng thiết bị |
| Độ tin cậy timing | Chỉ số cần phép đo clock và provenance tương ứng | Samples, boot, uncertainty, phase mapping và metric thiếu |

Các kết luận so sánh phụ thuộc số mẫu và thiết kế run. E01/E02 có vị trí update so với lịch khác nhau, nên phần thảo luận phải giữ điều kiện đó khi diễn giải latency. Bảng claim ghi rõ SOURCE_SUPPORTED, DESIGN, HYPOTHESIS và PENDING_RUN để cập nhật cùng evidence. [CLAIMS](../docs/CLAIMS.md), [EXPERIMENT_PROTOCOL](../docs/EXPERIMENT_PROTOCOL.md)

## 7. Kết luận dự thảo và điều kiện chốt

Phần tổng hợp hiện mô tả hai trigger đi tới cùng cache, các mốc cần quan sát và cách dùng hai nghiên cứu để thiết kế câu hỏi/case. Kết luận về mức cập nhật, latency, race, HYBRID và đối chiếu thiết bị sẽ được viết theo bộ CSV/SUMMARY được kiểm nhận ở bước 3 của SEM-50.

Để chốt, người tổng hợp nhận SEM-43/45 và CHECKS, điền mục 5, nối từng nhận định ở mục 6 tới run/group/evidence, cập nhật CLAIMS rồi rà citation cùng bibliography. Bản hoàn tất được bàn giao cho SEM-51/52/55 theo dependency của task. **Trạng thái hiện tại là WIP, chờ đầu vào và chưa đủ điều kiện merge.** [Task SEM-50](../tasks/backlog/SEM-50.md)

## 8. Tài liệu tham khảo

Bibliography dùng định dạng BibTeX và citation theo cú pháp Pandoc để ghép công cụ xuất bản sau này. Hai bài nghiên cứu giữ DOI và key từ artifact riêng của SEM-20/21. [references.bib](../research/references.bib)

| Citation key | Tài liệu |
|---|---|
| `Simon2017DiffsyncEnergy` | Simon, Schmidt và Pammer-Schindler, 2017, DOI 10.4108/eai.30-6-2017.152756 |
| `GonzalezPerez2022AndroidScheduling` | González-Pérez, Matey-Sanz, Granell và Casteleyn, 2022, DOI 10.1016/j.pmcj.2022.101550 |
| `AndroidDefineWork` | Android Developers, Define work requests, truy cập 09/11/2026 |
| `FirebaseReceiveMessages` | Firebase, Receive messages in Android apps, truy cập 09/11/2026 |
| `FirebaseAndroidPriority` | Firebase, Set and manage Android message priority, truy cập 09/11/2026 |
| `AndroidDozeStandby` | Android Developers, Optimize for Doze and App Standby, truy cập 09/11/2026 |
