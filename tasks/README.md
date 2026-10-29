# Task board — mỗi task một người

Phân công 29/10/2026: **45 task SEM-11…SEM-55**, mỗi task đúng một người thực hiện. Tiến độ được đối chiếu Project trong snapshot bên dưới. Hạn cuối 13/11/2026, 15 phút gồm demo, giữ 80 đơn vị thực hành/cơ chế và 20 nghiên cứu/lập luận.

[Project hiện hành](https://github.com/users/ThanhTris/projects/3/views/1) · [Project nhóm theo người](https://github.com/users/ThanhTris/projects/3/views/2) · [Phân công trong repo](../docs/TEAM_ASSIGNMENTS.md) · [Dữ liệu task](catalog.json).

SEM-01…SEM-10 chỉ còn là nhóm lịch sử với link tới task thay thế; thẻ cũ được archive, không tính Done. Mỗi task mới có việc làm, file đầu ra, CHECKS, acceptance, gate bắt đầu/gate hoàn tất và các task nhận bàn giao. Không có cột Phối hợp/Reviewer trong phân công thực hiện.

- **Bắt đầu sau:** cần đầu ra của task đó trước khi bắt đầu phần triển khai.
- **Hoàn tất còn cần:** có thể soạn khung/chuẩn bị ngay nếu không có gate bắt đầu, nhưng chưa được bàn giao cuối khi thiếu đầu vào.
- Task nhận đầu ra kiểm artifact/version/CHECKS trước dùng; lỗi trả về đúng owner ở Needs Update. Status Review là bước kiểm nhận, không thêm người thực hiện.
- Một nhánh `codex/SEM-XX-ten-ngan` cho mỗi task; mỗi CHECKS ghi đầu ra bàn giao cho task nào, không lấy trạng thái thay cho artifact thật.

<!-- deadline-policy:start -->
## Deadline từng task

[Lịch đầy đủ theo từng người](DEADLINES.md). Mỗi task có ngày và giờ bàn giao theo UTC+7; cột `Deadline (UTC+7)` trên Project hiển thị đầy đủ. Các gate trong cùng ngày được xếp giờ bàn giao trước task nhận đầu vào. Gói cuối SEM-55 hạn 12/11/2026 22:00, ngày 13/11 dành dự phòng đến 22:00.
<!-- deadline-policy:end -->

<!-- input-snapshot:start -->
## Trạng thái đối chiếu Project

Snapshot **2026-10-29 16:31:03 UTC**. Status là tiến độ thực hiện; Input status là khả năng bắt đầu theo dependency: **Sẵn sàng 7**, **Chuẩn bị trước 8**, **Chờ đầu vào 30**.

- Sẵn sàng: không có task dependency chưa Done; vẫn cần kiểm artifact/CHECKS khi nhận bàn giao.
- Chuẩn bị trước: được làm phần độc lập nhưng còn gate hoàn tất chưa bàn giao.
- Chờ đầu vào: còn gate bắt đầu chưa bàn giao.

Project là nguồn Status hiện hành. Sau khi đổi Status nguồn, chạy `python scripts/update_task_snapshot.py --apply` để đồng bộ Input status và tài liệu; `--check` chỉ kiểm độ khớp. Script giữ nguyên Status/Assignees/Owner/Deadline và không tạo thẻ.
<!-- input-snapshot:end -->

| Task | Người thực hiện duy nhất | Status | Input status | Hạn (UTC+7) | Công sức | Bắt đầu sau | Hoàn tất còn cần |
|---|---|---|---|---|---:|---|---|
| [SEM-11](backlog/SEM-11.md) — Chốt phạm vi và môi trường build Android | Trí | Todo | Sẵn sàng | 30/10/2026 12:00 (UTC+7) | 3 | Không có. | Không có. |
| [SEM-12](backlog/SEM-12.md) — Lập hồ sơ OPPO và emulator | Vinh | Todo | Sẵn sàng | 30/10/2026 12:00 (UTC+7) | 1 | Không có. | Không có. |
| [SEM-13](backlog/SEM-13.md) — Kiểm môi trường Node và quyền Firebase | Tâm | Todo | Sẵn sàng | 30/10/2026 12:00 (UTC+7) | 1 | Không có. | Không có. |
| [SEM-14](backlog/SEM-14.md) — Vẽ luồng dữ liệu và hợp đồng sync chung | Trí | Todo | Chờ đầu vào | 30/10/2026 14:00 (UTC+7) | 1 | [SEM-11](backlog/SEM-11.md) | Không có. |
| [SEM-15](backlog/SEM-15.md) — Giải thích cơ chế silent push và giới hạn FCM | Trang | Todo | Sẵn sàng | 30/10/2026 18:00 (UTC+7) | 3 | Không có. | Không có. |
| [SEM-16](backlog/SEM-16.md) — Lập ma trận lifecycle và protocol E01–E06 | Vinh | Todo | Sẵn sàng | 30/10/2026 18:00 (UTC+7) | 2 | Không có. | Không có. |
| [SEM-17](backlog/SEM-17.md) — Giải thích periodic WorkManager và constraints | Trung | Todo | Sẵn sàng | 30/10/2026 18:00 (UTC+7) | 3 | Không có. | Không có. |
| [SEM-18](backlog/SEM-18.md) — Giải thích server, FCM accepted và correlation | Tâm | Todo | Sẵn sàng | 30/10/2026 18:00 (UTC+7) | 2 | Không có. | Không có. |
| [SEM-19](backlog/SEM-19.md) — Tổng hợp mô hình cơ chế và câu hỏi phản biện | Tuấn | Todo | Chuẩn bị trước | 30/10/2026 22:00 (UTC+7) | 4 | Không có. | [SEM-11](backlog/SEM-11.md), [SEM-12](backlog/SEM-12.md), [SEM-13](backlog/SEM-13.md), [SEM-14](backlog/SEM-14.md), [SEM-15](backlog/SEM-15.md), [SEM-16](backlog/SEM-16.md), [SEM-17](backlog/SEM-17.md), [SEM-18](backlog/SEM-18.md) |
| [SEM-20](backlog/SEM-20.md) — Đọc bài nghiên cứu thứ nhất và ghi chú nguồn | Tuấn | Todo | Chuẩn bị trước | 01/11/2026 16:00 (UTC+7) | 5 | Không có. | [SEM-11](backlog/SEM-11.md), [SEM-12](backlog/SEM-12.md) |
| [SEM-21](backlog/SEM-21.md) — Đọc bài nghiên cứu thứ hai và ghi chú nguồn | Tâm | Todo | Chuẩn bị trước | 01/11/2026 16:00 (UTC+7) | 3 | Không có. | [SEM-11](backlog/SEM-11.md), [SEM-12](backlog/SEM-12.md) |
| [SEM-22](backlog/SEM-22.md) — Đối chiếu hai bài nghiên cứu với API push hiện hành | Trang | Todo | Chuẩn bị trước | 01/11/2026 22:00 (UTC+7) | 2 | Không có. | [SEM-15](backlog/SEM-15.md), [SEM-20](backlog/SEM-20.md), [SEM-21](backlog/SEM-21.md) |
| [SEM-23](backlog/SEM-23.md) — Tạo scaffold Android và UI cache/timeline | Trí | Todo | Chờ đầu vào | 31/10/2026 12:00 (UTC+7) | 4 | [SEM-11](backlog/SEM-11.md) | Không có. |
| [SEM-24](backlog/SEM-24.md) — Chuẩn bị bộ xuất log và run manifest | Vinh | Todo | Chờ đầu vào | 31/10/2026 15:00 (UTC+7) | 1 | [SEM-12](backlog/SEM-12.md) | [SEM-26](backlog/SEM-26.md) |
| [SEM-25](backlog/SEM-25.md) — Xây Room, SyncRepository và SyncWorker dùng chung | Trung | Todo | Chờ đầu vào | 31/10/2026 17:00 (UTC+7) | 4 | [SEM-23](backlog/SEM-23.md), [SEM-26](backlog/SEM-26.md) | Không có. |
| [SEM-26](backlog/SEM-26.md) — Chốt hợp đồng API và event schema | Tâm | Todo | Chờ đầu vào | 30/10/2026 17:00 (UTC+7) | 2 | [SEM-11](backlog/SEM-11.md), [SEM-13](backlog/SEM-13.md), [SEM-14](backlog/SEM-14.md) | Không có. |
| [SEM-27](backlog/SEM-27.md) — Triển khai server snapshot và CLI cập nhật | Tâm | Todo | Chờ đầu vào | 31/10/2026 17:00 (UTC+7) | 4 | [SEM-13](backlog/SEM-13.md), [SEM-26](backlog/SEM-26.md) | Không có. |
| [SEM-28](backlog/SEM-28.md) — Ghép manual sync đầu cuối và chốt hướng dẫn setup | Trí | Todo | Chờ đầu vào | 31/10/2026 22:00 (UTC+7) | 1 | [SEM-23](backlog/SEM-23.md), [SEM-24](backlog/SEM-24.md), [SEM-25](backlog/SEM-25.md), [SEM-27](backlog/SEM-27.md) | Không có. |
| [SEM-29](backlog/SEM-29.md) — Chạy pilot periodic E01 trên hai thiết bị | Vinh | Todo | Chờ đầu vào | 02/11/2026 22:00 (UTC+7) | 2 | [SEM-16](backlog/SEM-16.md), [SEM-24](backlog/SEM-24.md), [SEM-30](backlog/SEM-30.md) | [SEM-31](backlog/SEM-31.md) |
| [SEM-30](backlog/SEM-30.md) — Triển khai unique periodic work | Trung | Todo | Chờ đầu vào | 01/11/2026 18:00 (UTC+7) | 4 | [SEM-17](backlog/SEM-17.md), [SEM-25](backlog/SEM-25.md), [SEM-28](backlog/SEM-28.md) | Không có. |
| [SEM-31](backlog/SEM-31.md) — Bàn giao chẩn đoán và tài liệu periodic | Trung | Todo | Chờ đầu vào | 02/11/2026 12:00 (UTC+7) | 3 | [SEM-30](backlog/SEM-30.md) | Không có. |
| [SEM-32](backlog/SEM-32.md) — Triển khai callback FCM và enqueue sync | Trang | Todo | Chờ đầu vào | 02/11/2026 18:00 (UTC+7) | 4 | [SEM-15](backlog/SEM-15.md), [SEM-25](backlog/SEM-25.md), [SEM-28](backlog/SEM-28.md) | Không có. |
| [SEM-33](backlog/SEM-33.md) — Xử lý token refresh và bàn giao PUSH.md | Trang | Todo | Chờ đầu vào | 03/11/2026 14:00 (UTC+7) | 3 | [SEM-13](backlog/SEM-13.md), [SEM-32](backlog/SEM-32.md) | Không có. |
| [SEM-34](backlog/SEM-34.md) — Chạy pilot push E02 và xác nhận cache nền | Vinh | Todo | Chờ đầu vào | 03/11/2026 22:00 (UTC+7) | 1 | [SEM-16](backlog/SEM-16.md), [SEM-24](backlog/SEM-24.md), [SEM-32](backlog/SEM-32.md), [SEM-35](backlog/SEM-35.md) | [SEM-33](backlog/SEM-33.md) |
| [SEM-35](backlog/SEM-35.md) — Làm CLI gửi FCM data-only normal priority | Tâm | Todo | Chờ đầu vào | 01/11/2026 15:00 (UTC+7) | 2 | [SEM-13](backlog/SEM-13.md), [SEM-18](backlog/SEM-18.md), [SEM-27](backlog/SEM-27.md) | Không có. |
| [SEM-36](backlog/SEM-36.md) — Tích hợp ba mode và pilot hybrid | Trí | Todo | Chờ đầu vào | 05/11/2026 18:00 (UTC+7) | 3 | [SEM-29](backlog/SEM-29.md), [SEM-30](backlog/SEM-30.md), [SEM-32](backlog/SEM-32.md), [SEM-34](backlog/SEM-34.md), [SEM-35](backlog/SEM-35.md) | [SEM-38](backlog/SEM-38.md), [SEM-39](backlog/SEM-39.md), [SEM-40](backlog/SEM-40.md) |
| [SEM-37](backlog/SEM-37.md) — Chốt bản ứng viên và manifest phục vụ tập chính | Trí | Todo | Chờ đầu vào | 05/11/2026 22:00 (UTC+7) | 2 | [SEM-31](backlog/SEM-31.md), [SEM-33](backlog/SEM-33.md), [SEM-36](backlog/SEM-36.md), [SEM-38](backlog/SEM-38.md), [SEM-39](backlog/SEM-39.md), [SEM-40](backlog/SEM-40.md) | Không có. |
| [SEM-38](backlog/SEM-38.md) — Xử lý duplicate và version hint của push | Trang | Todo | Chờ đầu vào | 05/11/2026 12:00 (UTC+7) | 2 | [SEM-32](backlog/SEM-32.md), [SEM-33](backlog/SEM-33.md) | Không có. |
| [SEM-39](backlog/SEM-39.md) — Củng cố version guard, retry và race trong core | Trung | Todo | Chờ đầu vào | 05/11/2026 12:00 (UTC+7) | 2 | [SEM-25](backlog/SEM-25.md), [SEM-30](backlog/SEM-30.md) | Không có. |
| [SEM-40](backlog/SEM-40.md) — Thêm fault injection cố ý bỏ gửi push | Tâm | Todo | Chờ đầu vào | 04/11/2026 18:00 (UTC+7) | 1 | [SEM-27](backlog/SEM-27.md), [SEM-35](backlog/SEM-35.md) | Không có. |
| [SEM-41](backlog/SEM-41.md) — Chạy tập chính E01–E06 trên emulator | Vinh | Todo | Chờ đầu vào | 07/11/2026 13:00 (UTC+7) | 3 | [SEM-16](backlog/SEM-16.md), [SEM-24](backlog/SEM-24.md), [SEM-37](backlog/SEM-37.md) | Không có. |
| [SEM-42](backlog/SEM-42.md) — Chạy đối chiếu OPPO E01/E02 và ghi giới hạn OEM | Vinh | Todo | Chờ đầu vào | 07/11/2026 15:00 (UTC+7) | 3 | [SEM-12](backlog/SEM-12.md), [SEM-16](backlog/SEM-16.md), [SEM-24](backlog/SEM-24.md), [SEM-37](backlog/SEM-37.md) | Không có. |
| [SEM-43](backlog/SEM-43.md) — Chốt SUMMARY và bộ evidence thực nghiệm | Vinh | Todo | Chờ đầu vào | 07/11/2026 22:00 (UTC+7) | 1 | [SEM-41](backlog/SEM-41.md), [SEM-42](backlog/SEM-42.md), [SEM-44](backlog/SEM-44.md), [SEM-45](backlog/SEM-45.md) | Không có. |
| [SEM-44](backlog/SEM-44.md) — Kiểm độc lập trigger và phép tính dữ liệu main | Trung | Todo | Chờ đầu vào | 07/11/2026 19:00 (UTC+7) | 1 | [SEM-41](backlog/SEM-41.md), [SEM-42](backlog/SEM-42.md), [SEM-45](backlog/SEM-45.md) | Không có. |
| [SEM-45](backlog/SEM-45.md) — Viết parser log và sinh results.csv | Tuấn | Todo | Chờ đầu vào | 07/11/2026 17:00 (UTC+7) | 2 | [SEM-24](backlog/SEM-24.md), [SEM-26](backlog/SEM-26.md) | [SEM-41](backlog/SEM-41.md), [SEM-42](backlog/SEM-42.md) |
| [SEM-46](backlog/SEM-46.md) — Viết phần mở bài và bàn giao lời dẫn thao tác demo | Trí | Todo | Chuẩn bị trước | 08/11/2026 16:00 (UTC+7) | 1 | Không có. | [SEM-14](backlog/SEM-14.md), [SEM-37](backlog/SEM-37.md) |
| [SEM-47](backlog/SEM-47.md) — Viết phần silent push và lời dẫn demo 4 phút | Trang | Todo | Chờ đầu vào | 08/11/2026 16:00 (UTC+7) | 2 | [SEM-15](backlog/SEM-15.md) | [SEM-33](backlog/SEM-33.md), [SEM-34](backlog/SEM-34.md), [SEM-38](backlog/SEM-38.md) |
| [SEM-48](backlog/SEM-48.md) — Viết nội dung và biểu đồ kết quả cho bài nói | Vinh | Todo | Chuẩn bị trước | 08/11/2026 18:00 (UTC+7) | 1 | Không có. | [SEM-43](backlog/SEM-43.md), [SEM-44](backlog/SEM-44.md), [SEM-45](backlog/SEM-45.md) |
| [SEM-49](backlog/SEM-49.md) — Viết phần kiến trúc và lập luận nghiên cứu thứ hai | Tâm | Todo | Chờ đầu vào | 08/11/2026 16:00 (UTC+7) | 1 | [SEM-18](backlog/SEM-18.md) | [SEM-21](backlog/SEM-21.md), [SEM-27](backlog/SEM-27.md), [SEM-35](backlog/SEM-35.md), [SEM-40](backlog/SEM-40.md) |
| [SEM-50](backlog/SEM-50.md) — Hoàn thiện báo cáo, bibliography và CLAIMS | Tuấn | Todo | Chuẩn bị trước | 09/11/2026 22:00 (UTC+7) | 2 | Không có. | [SEM-19](backlog/SEM-19.md), [SEM-20](backlog/SEM-20.md), [SEM-21](backlog/SEM-21.md), [SEM-22](backlog/SEM-22.md), [SEM-43](backlog/SEM-43.md), [SEM-45](backlog/SEM-45.md) |
| [SEM-51](backlog/SEM-51.md) — Ghép deck 15 phút, PDF và speaker notes | Tuấn | Todo | Chuẩn bị trước | 10/11/2026 22:00 (UTC+7) | 3 | Không có. | [SEM-46](backlog/SEM-46.md), [SEM-47](backlog/SEM-47.md), [SEM-48](backlog/SEM-48.md), [SEM-49](backlog/SEM-49.md), [SEM-50](backlog/SEM-50.md) |
| [SEM-52](backlog/SEM-52.md) — Build APK bàn giao và viết DEMO_RUNBOOK | Trí | Todo | Chờ đầu vào | 11/11/2026 22:00 (UTC+7) | 1 | [SEM-37](backlog/SEM-37.md) | [SEM-43](backlog/SEM-43.md), [SEM-50](backlog/SEM-50.md), [SEM-51](backlog/SEM-51.md) |
| [SEM-53](backlog/SEM-53.md) — Tái lập runbook và quay video dự phòng | Vinh | Todo | Chờ đầu vào | 12/11/2026 15:00 (UTC+7) | 2 | [SEM-52](backlog/SEM-52.md) | Không có. |
| [SEM-54](backlog/SEM-54.md) — Điều phối hai lần diễn tập và ghi thời lượng | Tuấn | Todo | Chờ đầu vào | 12/11/2026 19:00 (UTC+7) | 1 | [SEM-51](backlog/SEM-51.md), [SEM-52](backlog/SEM-52.md) | [SEM-53](backlog/SEM-53.md) |
| [SEM-55](backlog/SEM-55.md) — Chốt manifest và gói bàn giao seminar | Trí | Todo | Chờ đầu vào | 12/11/2026 22:00 (UTC+7) | 1 | [SEM-43](backlog/SEM-43.md), [SEM-50](backlog/SEM-50.md), [SEM-51](backlog/SEM-51.md), [SEM-52](backlog/SEM-52.md), [SEM-53](backlog/SEM-53.md), [SEM-54](backlog/SEM-54.md) | Không có. |
