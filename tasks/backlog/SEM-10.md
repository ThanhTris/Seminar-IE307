# SEM-10 — Đóng gói demo và diễn tập

- Status: backlog
- Lịch mục tiêu: 11–12/11/2026; dự phòng 13/11
- Công sức: 5/100 — Thực hành
- Owner: Trí
- Reviewer: Tâm
- Phối hợp: Vinh, Tuấn
- Điều kiện bắt đầu: SEM-07 đã có đầu ra cần dùng
- Điều kiện hoàn tất bổ sung: SEM-08, SEM-09 đã bàn giao

## Đầu vào

App/server đã tích hợp; kịch bản PRESENTATION_PLAN; kết quả SEM-08 và slide SEM-09 trước khi hoàn tất.

## Việc cần làm

Phân việc: Trí build/đóng gói, ghi manifest/checksum và DEMO_RUNBOOK; Vinh quay video, thử chạy theo runbook và ghi lỗi; Tuấn điều phối hai lượt diễn tập, ghi REHEARSAL và sửa lời dẫn. Cả sáu tham gia diễn tập, sửa nội dung/module mình phụ trách.

Theo [phân công 6 người](../../docs/TEAM_ASSIGNMENTS.md); owner tổng hợp đầu ra và CHECKS, reviewer kiểm trước khi chuyển done.

1. Build APK cho OPPO và emulator, chạy setup từ môi trường sạch hoặc ghi rõ phần chưa tái lập.
2. Quay video dự phòng từ run thật của bản build tương ứng; metadata và nhãn phát lại rõ ràng.
3. Soạn runbook: kết nối, mode/reset, dữ liệu, thao tác live, ngưỡng chuyển video 30 giây và khôi phục thiết bị.
4. Diễn tập 2 lần có bấm giờ; sửa lời dẫn và kiểm tra không lộ token/credential trong log/video.
5. Đóng gói artifact với commit, checksum và danh mục; rà soát tài liệu và link tải.

## Đầu ra bắt buộc

- release/ — APK hoặc liên kết GitHub Release tới APK, manifest phiên bản/commit/checksum và danh mục artifact.
- docs/DEMO_RUNBOOK.md — hướng dẫn chuẩn bị, thao tác, fallback và cleanup.
- Video demo thật và clip dự phòng, đường dẫn trong release manifest; tránh commit file quá lớn.
- docs/REHEARSAL.md — thời gian từng phần của 2 lần diễn tập, lỗi và cách sửa.
- docs/evidence/SEM-10/CHECKS.md — commit, môi trường, bước kiểm tra, expected/actual, link bằng chứng, hạn chế và phần bàn giao.

## Tiêu chí nghiệm thu

- [ ] Người khác làm theo runbook tái lập được hoặc ghi rõ bước cần hỗ trợ/cấu hình.
- [ ] Hai lần diễn tập nằm trong 15 phút gồm demo; payload/log/video không lộ bí mật.
- [ ] APK, server, báo cáo và slide trỏ đúng commit; mọi phần chưa hoàn thành được liệt kê trước bàn giao.
- [ ] Có đủ đầu ra và CHECKS.md; người làm giải thích được kết quả, reviewer được phân công kiểm tra và ghi kết luận.

## Trạng thái bàn giao

Chưa thực hiện. Tên file ở trên là đầu ra phải tạo khi làm task, không phải bằng chứng đã tồn tại. Cập nhật task và task board cùng lúc khi đổi trạng thái.
