# Task board — Seminar IE307

Kế hoạch cập nhật 28/10/2026, hạn 13/11/2026. Toàn bộ task vẫn **backlog**, chưa có code/evidence. Các đầu ra là yêu cầu bàn giao, không phải file đã hoàn thành.

Mỗi task có việc cần làm, đầu ra bắt buộc, ca nghiệm thu và điều kiện bắt đầu/hoàn tất. Giữ ID SEM-01…SEM-10; không tạo chat hoặc GitHub Issue mới.

Đã phân công cho Trí, Trang, Vinh, Trung, Tâm và Tuấn. Xem [bảng phân công theo người](../docs/TEAM_ASSIGNMENTS.md) để biết phần đóng góp, đầu ra, mốc bàn giao và reviewer; owner/reviewer cũng được ghi trực tiếp trong từng task.

| Task | Owner | Reviewer | Lịch mục tiêu | Công sức | Điều kiện bắt đầu | Điều kiện hoàn tất bổ sung |
|---|---|---|---|---:|---|---|
| [SEM-01 — Chốt phạm vi và kiểm tra môi trường](backlog/SEM-01.md) | Trí | Trung | 28–29/10/2026 | 5 | Chuẩn bị ngay | — |
| [SEM-02 — Xây mô hình cơ chế và câu hỏi phản biện](backlog/SEM-02.md) | Tuấn | Trí | 28–30/10/2026 | 15 | Chuẩn bị ngay | SEM-01 |
| [SEM-03 — Đọc hai nghiên cứu và lập bảng lập luận](backlog/SEM-03.md) | Tuấn | Vinh | 29/10–01/11/2026 | 10 | Chuẩn bị ngay | SEM-01 |
| [SEM-04 — Dựng demo tối thiểu và logging](backlog/SEM-04.md) | Tâm | Trang | 29–31/10/2026 | 15 | SEM-01 | — |
| [SEM-05 — Triển khai và quan sát periodic fetch](backlog/SEM-05.md) | Trung | Trang | 01–02/11/2026 | 10 | SEM-02, SEM-04 | — |
| [SEM-06 — Triển khai và quan sát push im lặng](backlog/SEM-06.md) | Trang | Trí | 01–03/11/2026 | 10 | SEM-02, SEM-04 | — |
| [SEM-07 — Tích hợp hybrid và tính đúng của đồng bộ](backlog/SEM-07.md) | Trí | Vinh | 04–05/11/2026 | 10 | SEM-05, SEM-06 | — |
| [SEM-08 — Chạy tập ca cốt lõi và phân tích số đo](backlog/SEM-08.md) | Vinh | Trang | Chuẩn bị từ 28/10; chạy 02–07/11/2026 | 10 | Chuẩn bị ngay | SEM-05, SEM-06, SEM-07 |
| [SEM-09 — Hoàn thiện bài trình bày 15 phút và lập luận](backlog/SEM-09.md) | Tuấn | Trung | Dàn ý từ 28/10; bản cuối 08–10/11/2026 | 10 | Chuẩn bị ngay | SEM-02, SEM-03, SEM-08 |
| [SEM-10 — Đóng gói demo và diễn tập](backlog/SEM-10.md) | Trí | Tâm | 11–12/11/2026; dự phòng 13/11 | 5 | SEM-07 | SEM-08, SEM-09 |

## Cách sử dụng

1. Bắt đầu SEM-01 kiểm tra môi trường và SEM-02 xây mô hình cơ chế; SEM-03 có thể đọc nguồn theo phạm vi đã xác nhận.
2. SEM-04 chỉ code trên môi trường đã chốt. SEM-05 và SEM-06 dùng cùng nền tảng; nếu một người làm, thực hiện từng luồng, không cần hai project riêng.
3. SEM-08 chuẩn bị protocol ngay, chạy ca theo từng đầu vào: E01 sau SEM-05; E02 sau SEM-06; E03/E04 theo trigger đã sẵn sàng; E05/E06 sau SEM-07. Chỉ hoàn tất sau đủ tập cốt lõi.
4. SEM-09 soạn dàn ý ngay; phần kết quả chờ SEM-08. SEM-10 có thể chuẩn bị đóng gói sau SEM-07, nhưng nghiệm thu cuối phải có SEM-08/09.
5. Trạng thái backlog → in-progress → review → done; nhánh task/SEM-XX-ten-ngan. Mỗi task có một CHECKS.md bao gồm bàn giao; HANDOFF.md là tùy chọn.
6. Task done cần đầu ra thật, kiểm chứng và kết luận review; không coi việc viết kế hoạch là hoàn thành task.
7. Đến 31/10, SEM-04 phải giao cả SyncWorker/enqueue chung cho hai trigger. Ngày 02–05/11 chạy pilot; bản ứng viên chốt cuối 05/11, dữ liệu chính thức chạy 06–07/11 và phân nhóm theo build. Nội dung slide/evidence bàn giao ngày 08/11 để ghép/review trước ngày 10/11.

Trọng số: thực hành/cơ chế/diễn tập 80, nghiên cứu/lập luận 20. Khi trễ cổng, báo blocker và điều chỉnh phần mở rộng theo [PLAN](../docs/PLAN.md), không tự kéo dài deadline.
