# SEM-06 — Triển khai FCM data-only

- Status: backlog
- Owner: chưa phân công
- Reviewer: chưa phân công
- Dependencies: SEM-02, SEM-04
- Đầu vào: PLAN.md và đầu ra được nghiệm thu của các dependency.
- Đầu ra dự kiến: android/; server/; docs/PUSH.md

## Tiêu chí nghiệm thu

- [ ] Gửi qua Admin SDK, nhận data-only, bàn giao việc dài sang worker; xử lý token refresh; ghi server accepted khác device received; thử foreground/background.
- [ ] Có docs/evidence/SEM-06/CHECKS.md: môi trường, bước thực hiện, expected/actual, log và hạn chế.
- [ ] Có docs/evidence/SEM-06/HANDOFF.md: commit, đầu ra, cách sử dụng và việc còn lại.
- [ ] Người thực hiện giải thích được cơ chế liên quan; reviewer xác nhận trước khi chuyển done.

## Kiểm tra và bàn giao

Kiểm tra đúng phạm vi task. Với tài liệu: xác minh nguồn và liên kết; với code: chạy hành vi thật và kiểm thử logic quan trọng; với thí nghiệm: lưu dữ liệu thô và lệnh tái lập. Không đánh dấu hoàn thành nếu chỉ có scaffold.

