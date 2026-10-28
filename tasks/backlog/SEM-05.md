# SEM-05 — Triển khai và quan sát periodic fetch

- Status: backlog
- Lịch mục tiêu: 01–02/11/2026
- Công sức: 10/100 — Thực hành
- Owner/reviewer: chưa phân công
- Điều kiện bắt đầu: SEM-02, SEM-04 đã có đầu ra cần dùng
- Điều kiện hoàn tất bổ sung: không ngoài điều kiện bắt đầu

## Đầu vào

SyncRepository, docs/API.md, docs/EVENT_SCHEMA.md và mô hình cơ chế đã review.

## Việc cần làm

1. Thêm unique periodic work và network constraint, cập nhật UI trạng thái lịch.
2. Tắt push khi thử mode PERIODIC; đăng ký nhiều lần không sinh thêm lịch.
3. Ghi work start/end, trigger, version và failure; retry có phân biệt lỗi tạm thời/vĩnh viễn.
4. Chạy E01 pilot và bắt đầu ghi phiên periodic tự nhiên dài, không ép chạy để tạo bằng chứng.

## Đầu ra bắt buộc

- android/ — periodic scheduler và SyncWorker dùng repository chung.
- docs/PERIODIC.md — luồng xử lý, cấu hình được dùng, cách kiểm tra lịch và đọc log.
- experiments/runs/<run_id>/ — manifest và event log của pilot được gắn nhãn.
- docs/evidence/SEM-05/CHECKS.md — commit, môi trường, bước kiểm tra, expected/actual, link bằng chứng, hạn chế và phần bàn giao.

## Tiêu chí nghiệm thu

- [ ] Một lịch active sau nhiều lần đăng ký; worker có trigger PERIODIC.
- [ ] Có ít nhất 2 lần chạy tự nhiên trong pilot và ghi cả phiên quan sát; nếu thiếu, nêu blocker.
- [ ] Không yêu cầu hệ thống phải lệch giờ để chứng minh hiểu giới hạn; đối chiếu điều quan sát với tài liệu.
- [ ] Có đủ đầu ra và CHECKS.md; người làm giải thích được kết quả, reviewer hoặc người thực hiện tự review được ghi rõ.

## Trạng thái bàn giao

Chưa thực hiện. Tên file ở trên là đầu ra phải tạo khi làm task, không phải bằng chứng đã tồn tại. Cập nhật task và task board cùng lúc khi đổi trạng thái.
