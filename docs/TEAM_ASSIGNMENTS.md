# Phân công 6 thành viên — Seminar IE307

Chủ đề 12: **Xử lý việc tìm nạp nền và thông báo đẩy im lặng**. Cập nhật 28/10/2026. Hạn bàn giao 13/11/2026; bài nói 15 phút gồm demo. Danh sách người dùng xác nhận: Trí, Trang, Vinh, Trung, Tâm, Tuấn.

Phân công theo đầu việc, chưa dựa trên thông tin về thế mạnh cá nhân. Owner chịu trách nhiệm tập hợp và bàn giao task; người phối hợp làm phần đã ghi, không phải owner làm toàn bộ. Việc gán người không đổi trạng thái backlog thành đang làm/đã xong.

## 1. Vai trò và đầu ra của từng người

| Thành viên | Trách nhiệm chính | Đầu ra trực tiếp | Mốc chính |
|---|---|---|---|
| **Trí** | Môi trường, nền app, tích hợp hybrid, đóng gói | SCOPE/ENVIRONMENT; scaffold/UI/timeline; mode integration và SYNC; APK, release manifest và DEMO_RUNBOOK | 29/10; 31/10; 05/11; 12/11 |
| **Trang** | Cơ chế và client silent push | Phần lý thuyết FCM; FirebaseMessagingService/token/enqueue; PUSH; pilot push và nội dung slide push | 30/10; 03/11; 10/11 |
| **Vinh** | Thiết bị, kiểm thử và kiểm chứng dữ liệu | Hồ sơ OPPO/emulator; scripts chạy/reset; manifest và logs E01–E06; SUMMARY; video dự phòng | 29/10; 07/11; 12/11 |
| **Trung** | Sync core và periodic fetch | Room/SyncRepository/SyncWorker và giao diện enqueue chung; periodic scheduler; PERIODIC; version/retry/race tests | Core 31/10; periodic 02/11; tích hợp 05/11 |
| **Tâm** | Backend, API và gửi FCM | Server snapshot/version; API/EVENT_SCHEMA; CLI gửi/bỏ gửi push; ghi chú bài nghiên cứu thứ hai | 31/10; 01/11; 03–05/11 |
| **Tuấn** | Tổng hợp cơ chế, nghiên cứu và bài trình bày | MECHANISMS/QUESTIONS; bài nghiên cứu thứ nhất/bibliography; script phân tích/CSV; CLAIMS, slide/PDF/report/notes | 30/10; 01/11; 07/11; 10/11 |

Các tên ngắn ở bảng tương ứng với đường dẫn đầy đủ trong từng task. Mọi tài liệu/code/log trên là đầu ra phải làm, chưa tồn tại chỉ vì có tên trong bảng.

## 2. Ai chịu trách nhiệm từng task

| Task | Owner | Phối hợp thực hiện | Reviewer |
|---|---|---|---|
| [SEM-01](../tasks/backlog/SEM-01.md) | Trí | Vinh, Tâm | Trung |
| [SEM-02](../tasks/backlog/SEM-02.md) | Tuấn | Trí, Trang, Vinh, Trung, Tâm | Trí |
| [SEM-03](../tasks/backlog/SEM-03.md) | Tuấn | Trang, Tâm | Vinh |
| [SEM-04](../tasks/backlog/SEM-04.md) | Tâm | Trí, Vinh, Trung | Trang |
| [SEM-05](../tasks/backlog/SEM-05.md) | Trung | Trí, Vinh | Trang |
| [SEM-06](../tasks/backlog/SEM-06.md) | Trang | Vinh, Tâm | Trí |
| [SEM-07](../tasks/backlog/SEM-07.md) | Trí | Trang, Trung, Tâm | Vinh |
| [SEM-08](../tasks/backlog/SEM-08.md) | Vinh | Trung, Tuấn | Trang |
| [SEM-09](../tasks/backlog/SEM-09.md) | Tuấn | Trí, Trang, Vinh, Tâm | Trung |
| [SEM-10](../tasks/backlog/SEM-10.md) | Trí | Vinh, Tuấn | Tâm |

Reviewer kiểm lại đầu ra và CHECKS trước khi chuyển done, không chỉ đọc checklist. SEM-02 có phần đóng góp của cả nhóm: Tuấn đọc chéo phần Trí viết, Trí kiểm bản tổng hợp. Reviewer không tự xác nhận phần do mình viết.

## 3. Phần việc và bàn giao cụ thể

### Trí — môi trường và tích hợp

- 28–29/10: chốt phạm vi và môi trường với Tâm/Vinh; ghi phiên bản thực tế và blocker Firebase nếu có.
- 29–31/10: tạo scaffold Android, UI cache/timeline và nối phần sync của Trung với server của Tâm; tổng hợp SETUP.
- 04–05/11: tích hợp periodic + push vào ba mode; bảo đảm đổi mode không để worker cũ làm nhiễu ca thử; chốt SYNC.md, commit app/server và checksum bản ứng viên cuối 05/11 cho Vinh đo tập chính.
- 11–12/11: build APK, ghi commit/checksum, viết runbook và chốt gói bàn giao. Vinh hỗ trợ video/tái lập; Tuấn hỗ trợ diễn tập.
- Bàn giao môi trường cho Trung/Trang/Tâm; bản tích hợp cho Vinh; bản demo ổn định cho Tuấn.

### Trang — silent push

- 28–30/10: viết đường đi server → FCM → callback → worker và các giới hạn vào phần SEM-02 giao Tuấn tổng hợp.
- Đến 01/11: đối chiếu lập luận push trong hai bài nghiên cứu với tài liệu API đang dùng.
- 01–03/11: triển khai nhận FCM, refresh token, gọi enqueue/SyncWorker đã có từ SEM-04 và viết PUSH.md; phối hợp Tâm kiểm luồng foreground tối thiểu ngay 01/11, hoàn tất pilot background đến 03/11.
- 04–05/11: tích hợp duplicate/enqueue vào hybrid với Trí/Trung.
- Đến 08/11: giao nội dung slide push và lời dẫn demo cho Tuấn; ngày 09–10/11 phối hợp review/sửa. Trang dẫn toàn demo 4 phút, Trí thao tác thiết bị.
- Đầu ra quan trọng: push nhận được và cache được áp dụng trước khi mở lại UI, có log từng giai đoạn.

### Vinh — thiết bị và thực nghiệm

- 28–29/10: ghi cấu hình emulator/OPPO, chuẩn bị cách xuất log; phối hợp người đang giữ OPPO để đặt lịch sử dụng, không mặc định Vinh sở hữu thiết bị.
- 29–31/10: góp ý EVENT_SCHEMA để log đủ phân tích; chuẩn bị run manifest và script chạy/reset.
- 02–05/11: chạy pilot từng luồng để tìm lỗi. Ngày 06–07/11 chạy tập chính E01–E06 trên bản ứng viên, lưu commit/checksum, timeout và run bị nhiễu; chạy lại ca có code/config thay đổi thay vì trộn build.
- Cùng Tuấn tái tính số liệu từ logs; Vinh kiểm dữ liệu đầu vào, ký nhận SUMMARY ngày 07/11 và giao kết quả/giới hạn cho bài nói chậm nhất 08/11.
- 11–12/11: quay video bản build thật, tái lập runbook và lưu lỗi diễn tập.
- Không chỉ chụp màn hình: mỗi kết luận phải truy được về run_id, manifest và log.

### Trung — sync core và periodic

- 28–30/10: viết phần WorkManager/constraints/lifecycle và cách đọc timeline.
- 29–31/10: làm Room, SyncRepository, SyncWorker và giao diện enqueue chung, version snapshot và manual sync; bàn giao core cho Trang trước SEM-06. UI chỉ đọc cache khi mở lại.
- 01–02/11: làm unique periodic work và network constraint gọi worker chung, PERIODIC.md và pilot E01.
- 04–05/11: xử lý version guard, retry và race trong core; test trigger trùng/cũ/đến trong khi worker đang kết thúc.
- Hỗ trợ Vinh kiểm/reset scheduler và xác nhận trigger của dữ liệu đo.
- Bàn giao cùng API sync cho Trang sử dụng; không tạo sync engine riêng cho từng mode.

### Tâm — backend và hợp đồng dữ liệu

- 28–29/10: kiểm Node/Firebase và phương án kết nối; soạn API/schema nháp ngay sau khi phạm vi ổn định.
- 29–31/10: server health/snapshot/update, version bền qua restart, API.md và EVENT_SCHEMA.md. Chốt schema với Trí/Trung/Trang/Vinh trước khi nối code.
- Đến 01/11: đọc bài nghiên cứu thứ hai, ghi phương pháp/giới hạn và ca thử liên quan cho Tuấn.
- 01–03/11: làm CLI gửi data-only, log accepted/rejected và ID; phối hợp Trang kiểm payload/token.
- 04–05/11: thêm chế độ cố ý bỏ gửi push để thử hybrid.
- Đến 08/11: giao phần kiến trúc và đối chiếu nghiên cứu cho Tuấn; 09–10/11 hỗ trợ sửa, 11–12/11 review gói release.

### Tuấn — cơ chế, phân tích và bài nói

- 28–30/10: tổng hợp phần cơ chế của cả nhóm thành hai sơ đồ và ít nhất 10 câu hỏi phản biện; không chỉ ghép văn bản.
- 29/10–01/11: đọc bài nghiên cứu thứ nhất, tổng hợp hai bài với Tâm/Trang, quản lý references.bib và CLAIMS.
- 02–07/11: làm script tổng hợp log thành results.csv và bảng/biểu đồ; phối hợp Vinh kiểm số mẫu và timeout.
- Chuẩn bị dàn ý sớm; nhận nội dung/evidence các phần ngày 08/11, ghép deck/report ngày 09/11 để Trung review, chốt deck/PDF/notes/CLAIMS ngày 10/11. Mỗi người viết phần mình, Tuấn tổng hợp.
- 11–12/11: điều phối hai lần diễn tập có bấm giờ, ghi REHEARSAL, sửa lời dẫn; mỗi người vẫn phải hiểu cả hai cơ chế.
- Tuấn là đầu mối chỉnh file deck chính; các thành viên gửi nội dung và evidence, tránh sáu bản slide lệch nhau.

## 4. Khối lượng dự kiến

Phân rã đúng 100 đơn vị của PLAN, không cộng thêm 100 đơn vị mới. Mỗi ô là phần công sức thực hiện trong task, không phải điểm thành tích hay giờ làm. Review/hỗ trợ được điều chỉnh theo khối lượng thực tế.

| Task | Trí | Trang | Vinh | Trung | Tâm | Tuấn | Tổng |
|---|---:|---:|---:|---:|---:|---:|---:|
| SEM-01 | 3 | 0 | 1 | 0 | 1 | 0 | 5 |
| SEM-02 | 1 | 3 | 2 | 3 | 2 | 4 | 15 |
| SEM-03 | 0 | 2 | 0 | 0 | 3 | 5 | 10 |
| SEM-04 | 4 | 0 | 1 | 4 | 6 | 0 | 15 |
| SEM-05 | 1 | 0 | 2 | 7 | 0 | 0 | 10 |
| SEM-06 | 0 | 7 | 1 | 0 | 2 | 0 | 10 |
| SEM-07 | 5 | 2 | 0 | 2 | 1 | 0 | 10 |
| SEM-08 | 0 | 0 | 7 | 1 | 0 | 2 | 10 |
| SEM-09 | 1 | 2 | 1 | 0 | 1 | 5 | 10 |
| SEM-10 | 2 | 0 | 2 | 0 | 0 | 1 | 5 |
| **Tổng** | **17** | **16** | **17** | **17** | **16** | **17** | **100** |

SEM-03 + SEM-09 giữ 20 đơn vị nghiên cứu/lập luận; các task còn lại giữ 80 đơn vị cơ chế/thực hành. Khối lượng giữa người được cân bằng bằng phần đóng góp, không chỉ số task đứng tên owner.

## 5. Thứ tự phối hợp và tránh sửa trùng

- **29/10:** Trí chốt cấu hình nền; Tâm chốt API/EVENT_SCHEMA bản đầu với cả nhóm. Sau đầu vào SEM-01, Trí/Trung làm Android và Tâm làm server song song. Tài liệu SEM-02/03 có thể chuẩn bị trước.
- **31/10:** ghép manual sync đầu cuối và log; SyncWorker/enqueue chung phải có trong đầu ra SEM-04. Có thể chuẩn bị tài liệu/test trước, nhưng SEM-05/06 chỉ tích hợp khi đầu vào SEM-02/04 đạt.
- **01–03/11:** Trung làm periodic và Trang làm push trên cùng nền tảng; Tâm cung cấp sender; Vinh nhận từng phần để test.
- **04–05/11:** Trí tập hợp bản hybrid; các thay đổi sync core qua Trung, messaging qua Trang, server qua Tâm. Cuối 05/11 chốt bản ứng viên app/server có commit/checksum cho tập chính.
- **02–07/11:** Vinh điều phối lịch mỗi thiết bị: 02–05 pilot, 06–07 tập chính trên bản ứng viên; không chạy hai ca cùng app làm nhiễu nhau. Tuấn phân tích dữ liệu đã xuất trong lúc phiên khác đang chạy.
- **08–10/11:** tất cả giao nội dung/evidence ngày 08, Tuấn ghép ngày 09, Trung review và chốt ngày 10; từng người xác nhận phần mình.
- **11–12/11:** cả sáu diễn tập, gói nộp chốt bởi Trí; 13/11 dành sửa lỗi cuối.

Đầu mối file dùng chung: Trí quản build/manifest/UI và tích hợp mode; Trung quản Room/SyncRepository/SyncWorker; Trang quản messaging; Tâm quản server/API/EVENT_SCHEMA; Vinh quản script chạy/reset, manifest/log và SUMMARY; Tuấn quản script phân tích, CSV sinh ra, CLAIMS, report và slide.

Đây là đầu mối phối hợp, không phải độc quyền chỉnh file. Khi hai task cần đổi cùng file, thống nhất thay đổi với đầu mối và giữ diff nhỏ. Mỗi người làm branch riêng có ID task; không làm sáu bản app tách biệt.

## 6. Cách báo cáo hoàn thành

Owner cập nhật task với: đã làm, link commit/đầu ra, CHECKS, phần còn thiếu và người cần hỗ trợ. Reviewer xác nhận hành vi/nguồn thật trước done. Giữ toàn bộ tiêu chí của task; việc phân người không bỏ đầu ra.

Mỗi thành viên phải giải thích được periodic, silent push, Doze và cách đọc timeline; biết chạy ít nhất một ca thử hoặc tái lập phân tích từ log. Tất cả tham gia diễn tập và trả lời phản biện phần mình.

## 7. Kết quả kiểm tra lần hai

Đã sửa thiếu đầu vào SyncWorker của luồng push, thêm gate bản ứng viên và quy tắc không trộn dữ liệu khác build, đặt hạn nội dung trước ngày chốt slide. Phân vai nói được gộp thành 7 lượt liên tục với một người dẫn demo; 30 giây chuyển tiếp nằm trong tổng 15 phút.

Owner/reviewer, 10 đầu việc, effort 80/20 và các mốc đến 13/11 được giữ. Phân bổ 16–17 đơn vị/người là ước lượng ban đầu; Trí kiểm lại tải và blocker ngày 31/10 và 05/11, điều chuyển phần hỗ trợ khi cần và cập nhật task tương ứng.
