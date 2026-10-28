# Kế hoạch hiện hành — Chủ đề 12

Cập nhật 28/10/2026, thay lịch cũ tại commit 4341206. Hạn cuối vẫn là **13/11/2026 (UTC+7)**. Đã mất 5 ngày lịch kể từ mốc khởi đầu; repo chưa có bằng chứng triển khai. Kế hoạch dưới đây là lịch mục tiêu, cần báo sớm nếu cổng kiểm tra bị trễ.

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
| Nhân sự | Chưa gán owner; task có thể thực hiện tuần tự, không giả định có nhiều thành viên |

Phiên bản Android/ColorOS, API level máy ảo, JDK/Gradle/SDK và thư viện phải ghi trong SEM-01. Không suy ra thông số thiết bị từ tên model. Không chuyển stack nếu chưa có lý do và cập nhật quyết định trong repo.

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

Trước code, SEM-04 chốt docs/API.md và docs/EVENT_SCHEMA.md. Event tối thiểu: run_id, event_id, source, mode, device_alias, data_version, UTC timestamp, monotonic time phía Android, request_id/work_id/message_id nếu có, outcome/reason. Server accepted, push_received, work_started và snapshot_applied là các event riêng.

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

## 6. Lịch điều chỉnh

| Task | Lịch mục tiêu | Cổng bàn giao |
|---|---|---|
| SEM-01 | 28–29/10 | Cấu hình build, thiết bị và quyền truy cập Firebase rõ ràng |
| SEM-02 | 28–30/10 | Mô hình cơ chế, bảng thuật ngữ, các câu hỏi phản biện |
| SEM-03 | 29/10–01/11 | 2 bài có ghi chú, bibliography và bảng lập luận ban đầu |
| SEM-04 | 29–31/10 | App/server sync thủ công + cache + logging chạy đầu cuối |
| SEM-05 | 01–02/11 | Periodic có bằng chứng chạy tự nhiên |
| SEM-06 | 01–03/11 | Push data-only có bằng chứng nhận và sync khi background |
| SEM-07 | 04–05/11 | Hybrid, version guard, duplicate/race/retry tests |
| SEM-08 | 02–07/11 | Thử từng luồng ngay khi sẵn sàng; hoàn tất tập ca cốt lõi |
| SEM-09 | Dàn ý 28/10; bản cuối 08–10/11 | Bài trình bày 15 phút và báo cáo đối chiếu evidence |
| SEM-10 | 11–12/11 | APK, video, runbook, diễn tập có bấm giờ |
| Dự phòng | 13/11 | Sửa lỗi cuối và gói bàn giao, không thêm tính năng |

SEM-02 có thể bắt đầu từ phạm vi đã chốt mà không chờ build; thí nghiệm thật thuộc SEM-05/06/08. SEM-08 chuẩn bị theo protocol ngay, chạy từng ca sau task cung cấp luồng tương ứng; không chờ hybrid để kiểm tra periodic/push. SEM-09 soạn lời dẫn sớm nhưng chỉ chốt kết quả sau SEM-08.

Nếu 31/10 chưa có M1 (sync thủ công và log), báo blocker ngay và ưu tiên thông luồng. Nếu 03/11 chưa có đủ hai trigger, cắt UI, high-priority contrast và ca mở rộng; không bỏ hai cơ chế chính. Nếu thiếu dữ liệu đến 07/11, công bố phần chưa chạy, giảm số ca mở rộng; không dùng log giả. Video chỉ thay thao tác live khi cần, không thay bằng chứng thực nghiệm.

## 7. Phân bổ công sức

| Task | Đơn vị / 100 | Nhóm |
|---|---:|---|
| SEM-01 | 5 | Thực hành |
| SEM-02 | 15 | Thực hành/hiểu cơ chế |
| SEM-03 | 10 | Nghiên cứu |
| SEM-04 | 15 | Thực hành |
| SEM-05 | 10 | Thực hành |
| SEM-06 | 10 | Thực hành |
| SEM-07 | 10 | Thực hành |
| SEM-08 | 10 | Thực hành |
| SEM-09 | 10 | Nghiên cứu/lập luận/trình bày |
| SEM-10 | 5 | Thực hành/diễn tập |

Tổng thực hành 80, nghiên cứu 20. Đây là trọng số tương đối, chưa phải dự toán giờ vì chưa có quỹ thời gian/người thực hiện.

## 8. Nghiệm thu chung

- M1: clone/setup, app/server hoạt động, version và log đối chiếu được.
- M2: hai trigger hoạt động độc lập; không có sync ngầm khi mở app làm sai chứng cứ.
- M3: protocol cốt lõi có run thực tế, kể cả timeout/negative results, metadata và giới hạn.
- M4: demo 4 phút, toàn bài 15 phút, có câu trả lời vì sao các ca trễ/không chạy.
- M5: APK, hướng dẫn, server, dữ liệu đã loại thông tin nhạy cảm, báo cáo và slide gắn với một commit.

Theo [task board](../tasks/README.md). Không đánh dấu task done chỉ vì đã tạo tài liệu yêu cầu. Một CHECKS.md cho mỗi task có thể chứa cả kiểm chứng và bàn giao; không bắt buộc thêm HANDOFF.md trùng nội dung.

## 9. Thông tin còn phải đo hoặc cung cấp

Đã xác nhận framework tự do, 15 phút gồm demo, OPPO Find X9 và máy ảo. Còn thiếu phiên bản thiết bị, Firebase project/quyền gửi test, môi trường build và rubric nếu giảng viên có riêng. SEM-01 kiểm tra các điểm này trước khi chốt môi trường; hạn 13/11 giữ nguyên.
