# SEM-04 — Dựng demo tối thiểu và logging

- Status: backlog
- Lịch mục tiêu: 29–31/10/2026
- Công sức: 15/100 — Thực hành
- Owner: Tâm
- Reviewer: Trang
- Phối hợp: Trí, Vinh, Trung
- Điều kiện bắt đầu: SEM-01 đã có đầu ra cần dùng
- Điều kiện hoàn tất bổ sung: không ngoài điều kiện bắt đầu

## Đầu vào

docs/SCOPE.md và docs/ENVIRONMENT.md đã đủ để build; kiến trúc tối thiểu trong PLAN.

## Việc cần làm

Phân việc: Tâm làm server, API.md và phần event phía server; Trung làm Room/SyncRepository/SyncWorker và giao diện enqueue dùng chung; Trí làm scaffold Android, UI timeline và tích hợp, tổng hợp SETUP; Vinh chốt trường dữ liệu đo và kiểm log. Tâm quản lý API.md/EVENT_SCHEMA.md và nghiệm thu đầu cuối.

Theo [phân công 6 người](../../docs/TEAM_ASSIGNMENTS.md); owner tổng hợp đầu ra và CHECKS, reviewer kiểm trước khi chuyển done.

1. Tạo project Android Kotlin/Compose/Room và server TypeScript; pin dependency, Gradle wrapper và package lock.
2. Xây API đọc/cập nhật snapshot có version tăng đơn điệu; persist version và snapshot qua restart server.
3. Xây SyncRepository, SyncWorker và giao diện enqueue dùng chung cho periodic/push; quy định input trigger/run/version và event đầu ra trong EVENT_SCHEMA. Manual sync đi qua worker, có nhãn riêng; UI mở lại chỉ đọc cache trong thí nghiệm.
4. Tạo timeline JSONL và run_id; instrument server/client theo event schema, chuẩn bị kết nối cả hai thiết bị.
5. Thiết lập cấu hình mẫu, credential local; UI tối thiểu gồm bản tin, mode và timeline, không làm admin dashboard.

## Đầu ra bắt buộc

- android/ — source app, manifest, Gradle wrapper, dependency versions; SyncRepository/SyncWorker và giao diện enqueue dùng chung đã chạy được.
- server/ — source, package.json, lockfile, cấu hình mẫu, API snapshot và CLI cập nhật.
- docs/API.md — endpoint/payload/error/version semantics và ví dụ không chứa token.
- docs/EVENT_SCHEMA.md — event fields, correlation IDs, UTC/monotonic time và ví dụ.
- docs/SETUP.md — từ clone đến app/server chạy, có bước cấu hình riêng của người dùng.
- docs/evidence/SEM-04/CHECKS.md — commit, môi trường, bước kiểm tra, expected/actual, link bằng chứng, hạn chế và phần bàn giao.

## Tiêu chí nghiệm thu

- [ ] Build APK debug; server khởi động, app GET và lưu snapshot; đọc cache sau khi offline/mở lại.
- [ ] Manual sync enqueue được SyncWorker và ghi trigger MANUAL; mở UI không âm thầm GET dữ liệu. Trang xác nhận có thể dùng giao diện enqueue này cho SEM-06 mà không chờ code SEM-05.
- [ ] Server restart không làm version giảm; log từ hai phía liên kết được cùng một run.
- [ ] Có đủ đầu ra và CHECKS.md; người làm giải thích được kết quả, reviewer được phân công kiểm tra và ghi kết luận.

## Trạng thái bàn giao

Chưa thực hiện. Tên file ở trên là đầu ra phải tạo khi làm task, không phải bằng chứng đã tồn tại. Cập nhật task và task board cùng lúc khi đổi trạng thái.
