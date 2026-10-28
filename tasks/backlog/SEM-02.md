# SEM-02 — Xây mô hình cơ chế và câu hỏi phản biện

- Status: backlog
- Lịch mục tiêu: 28–30/10/2026
- Công sức: 15/100 — Thực hành/hiểu cơ chế
- Owner/reviewer: chưa phân công
- Điều kiện bắt đầu: có thể chuẩn bị từ kế hoạch đã chốt
- Điều kiện hoàn tất bổ sung: SEM-01 đã bàn giao

## Đầu vào

Phạm vi đã xác nhận trong docs/PLAN.md và nguồn chính thức trong research/README.md. Bổ sung version thiết bị khi SEM-01 bàn giao.

## Việc cần làm

1. Giải thích từ trigger đến cache: periodic scheduler/WorkManager và push FCM/callback/worker.
2. Phân biệt data-only, notification và mixed payload trong baseline API; phân biệt trigger nhận được và sync hoàn tất.
3. Lập bảng foreground/background/process death/recent-swipe/force-stop/Doze; đánh dấu điều cần đo trên OPPO.
4. Chuẩn bị câu hỏi phản biện và dự đoán cho E01–E06; mỗi giả thuyết gắn nguồn, chưa gọi là kết quả.

## Đầu ra bắt buộc

- docs/MECHANISMS.md — bảng thuật ngữ, 2 sơ đồ luồng, lifecycle/OS constraints, version áp dụng và nguồn.
- docs/QUESTIONS.md — ít nhất 10 câu hỏi cơ chế kèm đáp án ngắn và liên kết nguồn.
- docs/evidence/SEM-02/CHECKS.md — commit, môi trường, bước kiểm tra, expected/actual, link bằng chứng, hạn chế và phần bàn giao.

## Tiêu chí nghiệm thu

- [ ] Có thể giải thích hai luồng không đọc code, chỉ ra điểm Android quyết định chạy.
- [ ] Không đồng nhất màn hình tắt với Doze hoặc data-only với thông báo tắt tiếng.
- [ ] Không cần tạo app riêng cho task này; bằng chứng runtime được bổ sung từ SEM-05/06/08.
- [ ] Có đủ đầu ra và CHECKS.md; người làm giải thích được kết quả, reviewer hoặc người thực hiện tự review được ghi rõ.

## Trạng thái bàn giao

Chưa thực hiện. Tên file ở trên là đầu ra phải tạo khi làm task, không phải bằng chứng đã tồn tại. Cập nhật task và task board cùng lúc khi đổi trạng thái.
