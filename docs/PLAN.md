# Kế hoạch hiện hành — Chủ đề 12

Cập nhật 29/10/2026: chia 45 task một người; lịch và phạm vi kỹ thuật giữ theo bản 28/10. Hạn cuối vẫn là **13/11/2026 (UTC+7)**. Đã mất 5 ngày lịch kể từ mốc khởi đầu; repo chưa có bằng chứng triển khai. Kế hoạch dưới đây là lịch mục tiêu, cần báo sớm nếu cổng kiểm tra bị trễ.

## 1. Kết quả cần đạt

Trong 15 phút gồm demo, người nghe hiểu:
1. Tìm nạp nền là gì, ai quyết định khi nào công việc được chạy.
2. Push im lặng đưa tín hiệu cập nhật đến app như thế nào.
3. Vì sao tín hiệu đến, worker chạy và dữ liệu cập nhật là ba sự kiện khác nhau.
4. Cách xử lý trì hoãn, mất mạng, trùng sự kiện và dữ liệu cũ.
5. Những gì demo đã đo được và những giới hạn chưa kiểm chứng.

Tỷ lệ 80/20 là công sức, không áp đặt tỷ lệ số slide. Phần demo phải cho thấy cơ chế và giới hạn, có lịch sử sự kiện kiểm tra được.

## 2. Quyết định phạm vi

| Hạng mục | Quyết định |
|---|---|
| Nền tảng | Android; Kotlin + Compose, Room, WorkManager, Firebase Messaging |
| Backend | Node.js + TypeScript, Firebase Admin SDK; API nhỏ và lệnh CLI, không làm dashboard web |
| Bài toán | Một bảng tin môn học, mỗi bản cập nhật có version tăng đơn điệu |
| Dữ liệu | Một snapshot nhỏ, lưu cache; lấy bản hiện hành từ server |
| Thiết bị | Máy ảo có Google Play services cho ca kiểm soát; OPPO Find X9 cho đối chiếu |
| Trình bày | 15 phút gồm 4 phút demo; phân bổ chi tiết tại PRESENTATION_PLAN.md |
| Ngoài phạm vi cốt lõi | iOS, đa người dùng, đăng nhập sản phẩm, thiết kế UI cầu kỳ, benchmark pin, phát hành store |
| Bài báo | 2 nghiên cứu phù hợp được đọc kỹ; bài thứ 3–4 là mở rộng |
| Nhân sự | 6 người: Trí, Trang, Vinh, Trung, Tâm, Tuấn; mỗi task một người thực hiện theo [bảng phân công](TEAM_ASSIGNMENTS.md) |

Phiên bản Android/ColorOS, API level máy ảo, JDK/Gradle/SDK và thư viện phải ghi trong SEM-11/12/13. Không suy ra thông số thiết bị từ tên model. Không chuyển stack nếu chưa có lý do và cập nhật quyết định trong repo.

## 3. Phân biệt khái niệm và API

Background Fetch trong đề tài là khái niệm lấy dữ liệu nền; demo ánh xạ sang periodic WorkManager. Silent Push trong demo là tín hiệu FCM data-only, không tạo thông báo hiển thị. Đây không phải một API chung cho mọi nền tảng. Nguồn được quản lý tại [research/README.md](../research/README.md).

Chọn baseline triển khai **AndroidConfig v1 + data-only + normal priority**, SDK ổn định và phiên bản được khóa sau kiểm tra build. Không dùng high priority để làm silent demo có vẻ tức thì. Tài liệu Firebase hiện đã có AndroidConfigV2/BackgroundSync ở hướng EAP; ghi rõ demo dùng v1, đưa thay đổi này vào phụ lục, không trộn callback/payload giữa hai API. Tham chiếu [hướng dẫn chuyển đổi](https://firebase.google.com/docs/cloud-messaging/send/v2-api).

Người trình bày cần phân biệt notification, data và notification+data; app background, process chết, vuốt recent và force-stop; màn hình tắt và Doze. Chỉ mô tả hành vi quan sát trên cấu hình đã ghi.

## 4. Demo tối thiểu

Luồng chung: server đổi snapshot → một trigger yêu cầu đồng bộ → SyncWorker → GET snapshot → transaction cập nhật Room nếu version mới → timeline.

- **Periodic:** đăng ký một periodic work; không gửi push. Ghi thời điểm đăng ký và các lần chạy thật.
- **Push:** tắt periodic, server gửi data-only qua FCM; callback ghi sự kiện rồi enqueue công việc.
- **Hybrid:** cả hai trigger dùng cùng hàm sync, khóa/transaction và quy tắc version; dùng để minh họa phục hồi khi cố ý không gửi một push.

Chuyển chế độ phải hủy lịch không cần, đợi worker đang chạy kết thúc hoặc đánh dấu ca bị nhiễu, rồi mới bắt đầu run mới. Màn hình mở lại chỉ đọc cache; auto-refresh khi mở app tắt trong chế độ thí nghiệm. Nút sync thủ công có nhãn riêng và không tính là background result.

UI chỉ cần: snapshot/version cache, mode hiện tại, lần sync cuối và timeline có lọc run_id. Backend có health, đọc snapshot, cập nhật snapshot, gửi hoặc bỏ qua push có chủ ý; token được lưu qua cấu hình local hoặc cơ chế đăng ký tối thiểu có xử lý refresh.

Trước code, SEM-26 (Tâm) chốt docs/API.md và docs/EVENT_SCHEMA.md. SEM-25 (Trung) bàn giao core/enqueue sau scaffold SEM-23; SEM-28 (Trí) chốt manual end-to-end. SEM-30 (Trung) và SEM-32 (Trang) triển khai hai trigger sau đầu vào riêng; không chờ toàn bộ nhóm cơ chế tổng hợp. Event tối thiểu: run_id, event_id, source, mode, device_alias, data_version, UTC timestamp, monotonic time phía Android, request_id/work_id/message_id nếu có, outcome/reason. Server accepted, push_received, work_started và snapshot_applied là các event riêng.

## 5. Tối ưu cần chứng minh

| Thay đổi | Bằng chứng cần có |
|---|---|
| Unique periodic work | Đăng ký lặp không tạo thêm lịch |
| Đồng bộ idempotent | Trigger trùng không tạo bản dữ liệu trùng, version không giảm |
| Chỉ ghi khi version mới | Đọc snapshot không đổi không ghi lại bản tin |
| Network constraint và retry hữu hạn | Ca mất mạng phục hồi; lỗi vĩnh viễn không tạo vòng retry vô hạn |
| Coalesce tín hiệu phù hợp | Không mất cập nhật mới đến lúc worker đang kết thúc; có ca race |
| Push + periodic phục hồi | Bỏ gửi push có chủ ý, dữ liệu vẫn được cập nhật bởi periodic khi đủ điều kiện |

Giảm số request/ghi DB là chỉ số công việc; chưa đủ để kết luận tiết kiệm pin. Không cần tự viết scheduler, foreground service hoặc alarm để né hạn chế nền.

## 6. Lịch và gate hiện hành

Các task thực hiện là SEM-11…SEM-55, tra dependency đầy đủ tại [task board](../tasks/README.md). SEM-01…10 chỉ giữ mapping lịch sử, không giao nhiều người trên cùng một task.

| Mốc | Task đầu ra | Hạn |
|---|---|---|
| Môi trường độc lập | SEM-11 Trí; SEM-12 Vinh; SEM-13 Tâm | 29/10 |
| Cơ chế từng phần và bản tổng hợp | SEM-14…19, từng task một người | 30/10 |
| Contract và runtime tối thiểu | SEM-26 contract; SEM-23 scaffold; SEM-25 core; SEM-27 server; SEM-24 exporter; SEM-28 M1 | 30–31/10 |
| Nghiên cứu | SEM-20 Tuấn; SEM-21 Tâm; SEM-22 Trang | 01/11 |
| Periodic | SEM-30/31 Trung; pilot SEM-29 Vinh | 01–02/11 |
| Silent push | SEM-35 Tâm; SEM-32/33 Trang; pilot SEM-34 Vinh | 01–03/11 |
| Robustness và hybrid | SEM-38 Trang; SEM-39 Trung; SEM-40 Tâm; SEM-36 Trí | 04–05/11 |
| Chốt candidate | SEM-37 Trí | Cuối 05/11 |
| Tập main | SEM-41/42 Vinh, từng ca/build/thiết bị riêng | 06–07/11 |
| CSV/audit/SUMMARY | SEM-45 Tuấn → SEM-44 Trung → SEM-43 Vinh | 07/11 |
| Nội dung bài nói | SEM-46 Trí; SEM-47 Trang; SEM-48 Vinh; SEM-49 Tâm | 08/11 |
| Report và deck | SEM-50/51 Tuấn | 09–10/11 |
| APK/runbook → video → diễn tập → manifest cuối | SEM-52 Trí → SEM-53 Vinh → SEM-54 Tuấn → SEM-55 Trí | 11–12/11 |
| Dự phòng | Sửa lỗi cuối, không thêm tính năng | 13/11 |

Chỉ phần được ghi rõ chuẩn bị ngay mới được làm trước gate hoàn tất; task nhận đầu ra ghi artifact/version đã nhận. Mỗi người tự thực hiện và ghi CHECKS của task mình, không có cột Phối hợp/Reviewer. Task kiểm độc lập SEM-44 và tái lập SEM-53 có owner riêng.

Nếu 31/10 chưa có M1, báo blocker và ưu tiên thông luồng. Nếu 03/11 thiếu trigger, cắt UI/ca mở rộng; không bỏ hai cơ chế chính. Code/config ảnh hưởng đổi sau candidate phải chạy lại ca liên quan, không gộp log khác build. Thiếu số liệu ghi NOT_RUN, không dùng log giả; video chỉ thay thao tác live.

## 7. Phân bổ công sức

Giữ nguyên 100 đơn vị, cơ chế/thực hành 80 và nghiên cứu/lập luận 20. Chi tiết từng task tại tasks/catalog.json; tổng theo người: Trí 17, Trang 16, Vinh 17, Trung 17, Tâm 16, Tuấn 17. Không chia đều số thẻ vì mỗi thẻ có quy mô khác nhau (1–5 đơn vị). Đây là ước lượng công sức, không phải giờ hoặc điểm đánh giá.

## 8. Nghiệm thu chung

- M1: clone/setup, app/server hoạt động, version và log đối chiếu được.
- M2: hai trigger hoạt động độc lập; không có sync ngầm khi mở app làm sai chứng cứ.
- M3: protocol cốt lõi có run thực tế, kể cả timeout/negative results, metadata và giới hạn.
- M4: demo 4 phút, toàn bài 15 phút, có câu trả lời vì sao các ca trễ/không chạy.
- M5: manifest nối được APK/server đã kiểm chứng (commit và checksum) với dữ liệu đo, hướng dẫn, báo cáo và slide. Commit tài liệu có thể mới hơn code đã đo; mọi thay đổi code phải được kiểm tra ảnh hưởng trước bàn giao.

Theo [task board](../tasks/README.md). Không đánh dấu task done chỉ vì đã tạo tài liệu yêu cầu. Một CHECKS.md cho mỗi task một người chứa cả kiểm chứng và bàn giao; không bắt buộc thêm HANDOFF.md trùng nội dung.

## 9. Thông tin còn phải đo hoặc cung cấp

Đã xác nhận framework tự do, 15 phút gồm demo, OPPO Find X9 và máy ảo. Còn thiếu phiên bản thiết bị, Firebase project/quyền gửi test, môi trường build và rubric nếu giảng viên có riêng. SEM-11/12/13 kiểm tra từng phần này trước khi chốt môi trường; hạn 13/11 giữ nguyên.
