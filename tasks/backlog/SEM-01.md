# SEM-01 — Chốt phạm vi và kiểm tra môi trường

- Status: backlog
- Lịch mục tiêu: 28–29/10/2026
- Công sức: 5/100 — Thực hành
- Owner: Trí
- Reviewer: Trung
- Phối hợp: Vinh, Tâm
- Điều kiện bắt đầu: có thể chuẩn bị từ kế hoạch đã chốt
- Điều kiện hoàn tất bổ sung: không ngoài điều kiện bắt đầu

## Đầu vào

Quyết định đã xác nhận trong docs/PLAN.md: 15 phút, Kotlin native, OPPO Find X9 + emulator, hạn 13/11.

## Việc cần làm

Phân việc: Trí chốt SCOPE và công cụ Android; Tâm kiểm tra Node/Firebase/kết nối server; Vinh lập hồ sơ OPPO và emulator. Trí tổng hợp ENVIRONMENT và CHECKS.

Theo [phân công 6 người](../../docs/TEAM_ASSIGNMENTS.md); owner tổng hợp đầu ra và CHECKS, reviewer kiểm trước khi chuyển done.

1. Ghi phạm vi, 3 mode và các tính năng ngoài phạm vi; không đổi đề tài thành ứng dụng lớn.
2. Kiểm tra JDK, Android SDK, Gradle, Node và ADB; chọn emulator có Google Play services; ghi Android/API/ColorOS thực tế.
3. Chốt phiên bản stable của thư viện/build tools và phương án Firebase project; kiểm tra quyền truy cập, package/application ID và đường dẫn cấu hình local.
4. Xác định cách app trên từng thiết bị truy cập server và Internet cho FCM; không dùng localhost của máy tính làm địa chỉ trên điện thoại.

## Đầu ra bắt buộc

- docs/SCOPE.md — mục tiêu, quyết định công nghệ, thiết bị, giới hạn và các câu hỏi còn mở.
- docs/ENVIRONMENT.md — version matrix, kết quả kiểm tra từng công cụ, thiết bị, kết nối và cách cấp cấu hình Firebase không chứa key.
- docs/evidence/SEM-01/CHECKS.md — commit, môi trường, bước kiểm tra, expected/actual, link bằng chứng, hạn chế và phần bàn giao.

## Tiêu chí nghiệm thu

- [ ] ADB nhận đúng thiết bị/emulator; ghi kết quả thật hoặc blocker, không tự suy phiên bản OPPO.
- [ ] Các công cụ trả version và cấu hình Firebase cần thiết được xác định; có phiên bản stable cụ thể để SEM-04 pin.
- [ ] Người làm giải thích được lý do chọn native, baseline FCM v1 và phạm vi 15 phút.
- [ ] Có đủ đầu ra và CHECKS.md; người làm giải thích được kết quả, reviewer được phân công kiểm tra và ghi kết luận.

## Trạng thái bàn giao

Chưa thực hiện. Tên file ở trên là đầu ra phải tạo khi làm task, không phải bằng chứng đã tồn tại. Cập nhật task và task board cùng lúc khi đổi trạng thái.
