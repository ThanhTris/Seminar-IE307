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

Nhóm thực hành SEM-01/02/04/05/06/07/08/10 = 80; nghiên cứu và lập luận SEM-03/09 = 20. Đây là tỷ trọng công sức, không phải số slide.

## Lịch 3 tuần đã chốt

Bắt đầu 23/10/2026; hoàn thành chậm nhất 13/11/2026, theo giờ Việt Nam (UTC+7). Task được quản lý bằng file trong repo, tập trung việc cần làm và đầu ra; chưa phân công người khi chưa biết thành viên.

| Thời gian | Task | Đầu ra bắt buộc |
|---|---|---|
| 23–24/10 | SEM-01 | Phạm vi, stack, thiết bị và môi trường chạy được xác nhận |
| 24–27/10 | SEM-02, SEM-03 | Tài liệu cơ chế, thí nghiệm nhỏ; ghi chú 2–4 bài nghiên cứu và bảng claim–evidence ban đầu |
| 25–28/10 | SEM-04 | App/server chạy đầu cuối, cache và timeline có ID |
| 28–30/10 | SEM-05, SEM-06 | Hai luồng periodic và push chạy riêng, có log thật |
| 31/10–02/11 | SEM-07 | Ba chế độ đồng bộ, chống trùng, retry và phục hồi mạng |
| 03–06/11 | SEM-08 | Ma trận kiểm thử, dữ liệu thô và tổng hợp kết quả |
| 07–10/11 | SEM-09 | Báo cáo, slide và kết luận đối chiếu nguồn với thực nghiệm |
| 11–12/11 | SEM-10 | APK, runbook, video dự phòng và diễn tập |
| 13/11 | Dự phòng và bàn giao | Sửa lỗi cuối, kiểm tra gói nộp và chốt phiên bản |

Tuần 1 (23–29/10): hiểu cơ chế, nền tảng demo và nguồn nghiên cứu. Tuần 2 (30/10–05/11): hoàn thiện demo và thu thập dữ liệu. Tuần 3 (06–12/11): chốt kết quả, trình bày và diễn tập; 13/11 là hạn bàn giao.

SEM-03 có thể làm cùng SEM-02/04 khi đầu vào SEM-01 sẵn sàng. SEM-05/06 chỉ tích hợp sau khi SEM-02/04 đạt nghiệm thu. Nếu trễ tiến độ, bỏ phần mở rộng đo pin/đa thiết bị và trang trí UI trước; giữ ba chế độ, ca thử trọng tâm, dữ liệu thô và giải thích giới hạn.

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

Đã chốt: deadline 13/11/2026; GitHub ThanhTris, public; task dạng yêu cầu công việc và đầu ra trong repo. Còn cần xác nhận trước SEM-01 hoàn tất: thời lượng trình bày, số thành viên, rubric, công nghệ bắt buộc và thiết bị Android. Không chặn việc lập kế hoạch vì các mục này.
