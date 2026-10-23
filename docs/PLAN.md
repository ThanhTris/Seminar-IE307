# Kế hoạch Seminar IE307

## Mục tiêu và phạm vi

Giải thích được ai kích hoạt công việc nền, hệ điều hành quyết định khi nào chạy, dữ liệu đi qua những thành phần nào và vì sao công việc có thể trễ hoặc không thực hiện. Mỗi kết luận cần nguồn hoặc bằng chứng thực nghiệm.

Trong seminar này, Background Fetch được hiểu là lấy dữ liệu nền định kỳ bằng WorkManager; Silent Push là FCM data-only kích hoạt xử lý nền. Đây là cách ánh xạ thuật ngữ cho Android, cần trình bày rõ để tránh nhầm API cùng tên trên nền tảng khác.

Demo đề xuất: bảng tin môn học có version trên server, dữ liệu cache trên Android và màn hình lịch sử đồng bộ. So sánh ba chế độ: periodic fetch, push-triggered sync, hybrid. Cả ba dùng cùng dữ liệu và hàm đồng bộ để so sánh công bằng.

Stack đề xuất, chưa chốt: Kotlin + Jetpack Compose + Room + WorkManager + Firebase Messaging; backend Node.js/TypeScript và Firebase Admin SDK. Chốt sau khi biết yêu cầu môn học. Credential chỉ ở môi trường local/server.

## Phân bổ 100 đơn vị công sức

| Task | Nội dung | Đơn vị |
|---|---|---:|
| SEM-01 | Phạm vi, thiết bị và nền tảng | 5 |
| SEM-02 | Cơ chế và thí nghiệm nhỏ | 15 |
| SEM-03 | Tài liệu và bài báo | 10 |
| SEM-04 | App, server và logging | 15 |
| SEM-05 | Periodic fetch | 10 |
| SEM-06 | Silent push | 10 |
| SEM-07 | Hybrid và phục hồi lỗi | 10 |
| SEM-08 | Thực nghiệm và đo lường | 10 |
| SEM-09 | Phân tích, báo cáo và slide | 10 |
| SEM-10 | Đóng gói và diễn tập | 5 |

Nhóm thực hành SEM-01/02/04/05/06/07/08/10 = 80; nghiên cứu và lập luận SEM-03/09 = 20. Đây là tỷ trọng công sức, không phải số slide. Chưa gán ngày do chưa có deadline và nhân sự.

## Cổng nghiệm thu

M1: chốt phạm vi, thiết bị, giải thích cơ chế bằng lời và sơ đồ, chọn nguồn có liên quan.
M2: app/server chạy được; timeline liên kết request_id, message_id, work_id và data_version.
M3: từng chế độ chạy độc lập; không dùng nút chạy ngay để chứng minh periodic work chạy đúng lịch.
M4: có dữ liệu thô, cấu hình thiết bị, lệnh tái lập, kết quả và giới hạn cho từng ca.
M5: APK, server, hướng dẫn, báo cáo, slide và video dự phòng cùng phiên bản Git.

## Thiết kế thí nghiệm

Các trạng thái: foreground, background, màn hình tắt/Doze, mất mạng rồi nối lại, Battery Saver, process bị kill, vuốt khỏi recent, force-stop và mở lại, reboot. Phân biệt rõ các trạng thái kết thúc app; ghi Android/API level, hãng máy, app version, cấu hình pin và Google Play services.

Đo: thời điểm server đổi dữ liệu, nhận push, enqueue/start/end work, version áp dụng; tỷ lệ cập nhật trong cửa sổ quan sát, độ trễ, số request, retry và dữ liệu trùng. Ghi đồng hồ và sai lệch thời gian giữa server/thiết bị. Ca không nhận được phải ghi timeout/censored, không loại khỏi thống kê.

Pilot 3 lần mỗi ca để sửa quy trình; sau đó tối thiểu 10 lần mỗi ca trọng tâm nếu thời gian cho phép. Periodic phải quan sát đủ chu kỳ thực; rút gọn demo bằng log/video đã ghi và ghi rõ đó là phát lại. Báo cáo median, khoảng dao động và số mẫu; không suy rộng cho mọi thiết bị. Đo pin chỉ là phần mở rộng khi có phương pháp kiểm soát phù hợp.

Theo tài liệu Android, periodic có khoảng lặp tối thiểu 15 phút và có thể trễ do tối ưu pin. FCM normal priority là baseline cho đồng bộ nền; high priority chỉ thử có giải thích chính sách, không xem là cách bảo đảm silent sync tức thì. Không biến dự đoán thành kết quả đo.

## Quy trình làm task

Áp dụng mẫu đồ án IE307: ID ổn định, owner/reviewer, dependency, đầu vào/đầu ra, acceptance criteria và evidence. Owner chờ phân công, không tự lấy danh sách thành viên đồ án sang seminar.

Trạng thái: backlog → in-progress → review → done. Nhánh `task/SEM-XX-ten-ngan`. Chỉ bắt đầu khi đầu vào phụ thuộc đã sẵn sàng; mỗi task bàn giao `docs/evidence/SEM-XX/CHECKS.md` và `HANDOFF.md` gồm commit, cách chạy, kết quả thật và hạn chế. Không tạo evidence giả chỉ để đánh dấu hoàn thành.

## Các điểm cần xác nhận

Deadline, thời lượng trình bày, số thành viên, rubric; công nghệ bắt buộc; thiết bị Android; GitHub account/visibility; có cần chat Codex riêng hoặc GitHub Issues/Project hay không.
