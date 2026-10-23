# SEM-07 — Tích hợp hybrid và phục hồi

- Status: backlog
- Owner: chưa phân công
- Reviewer: chưa phân công
- Dependencies: SEM-05, SEM-06
- Đầu vào: PLAN.md và đầu ra được nghiệm thu của các dependency.
- Đầu ra dự kiến: android/; server/; docs/SYNC.md

## Tiêu chí nghiệm thu

- [ ] Ba chế độ chọn riêng; cùng sync engine; chống xử lý trùng, version cũ, retry mất mạng; periodic làm cơ chế bổ sung; có test logic idempotency.
- [ ] Có docs/evidence/SEM-07/CHECKS.md: môi trường, bước thực hiện, expected/actual, log và hạn chế.
- [ ] Có docs/evidence/SEM-07/HANDOFF.md: commit, đầu ra, cách sử dụng và việc còn lại.
- [ ] Người thực hiện giải thích được cơ chế liên quan; reviewer xác nhận trước khi chuyển done.

## Kiểm tra và bàn giao

Kiểm tra đúng phạm vi task. Với tài liệu: xác minh nguồn và liên kết; với code: chạy hành vi thật và kiểm thử logic quan trọng; với thí nghiệm: lưu dữ liệu thô và lệnh tái lập. Không đánh dấu hoàn thành nếu chỉ có scaffold.

