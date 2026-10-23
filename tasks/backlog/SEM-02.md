# SEM-02 — Giải thích cơ chế Android

- Status: backlog
- Owner: chưa phân công
- Reviewer: chưa phân công
- Dependencies: SEM-01
- Đầu vào: PLAN.md và đầu ra được nghiệm thu của các dependency.
- Đầu ra dự kiến: docs/MECHANISMS.md

## Tiêu chí nghiệm thu

- [ ] Vẽ luồng WorkManager/JobScheduler và FCM; giải thích Doze, constraints, retry, process death và force-stop; chạy thí nghiệm nhỏ có log.
- [ ] Có docs/evidence/SEM-02/CHECKS.md: môi trường, bước thực hiện, expected/actual, log và hạn chế.
- [ ] Có docs/evidence/SEM-02/HANDOFF.md: commit, đầu ra, cách sử dụng và việc còn lại.
- [ ] Người thực hiện giải thích được cơ chế liên quan; reviewer xác nhận trước khi chuyển done.

## Kiểm tra và bàn giao

Kiểm tra đúng phạm vi task. Với tài liệu: xác minh nguồn và liên kết; với code: chạy hành vi thật và kiểm thử logic quan trọng; với thí nghiệm: lưu dữ liệu thô và lệnh tái lập. Không đánh dấu hoàn thành nếu chỉ có scaffold.

