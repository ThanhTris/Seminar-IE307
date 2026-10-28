# SEM-04 — Dựng demo tối thiểu và logging

- Status: backlog
- Lịch mục tiêu: 29–31/10/2026
- Công sức: 15/100 — Thực hành
- Owner/reviewer: chưa phân công
- Điều kiện bắt đầu: SEM-01 đã có đầu ra cần dùng
- Điều kiện hoàn tất bổ sung: không ngoài điều kiện bắt đầu

## Đầu vào

docs/SCOPE.md và docs/ENVIRONMENT.md đã đủ để build; kiến trúc tối thiểu trong PLAN.

## Việc cần làm

1. Tạo project Android Kotlin/Compose/Room và server TypeScript; pin dependency, Gradle wrapper và package lock.
2. Xây API đọc/cập nhật snapshot có version tăng đơn điệu; persist version và snapshot qua restart server.
3. Xây một SyncRepository dùng chung, manual sync có nhãn; UI mở lại chỉ đọc cache trong thí nghiệm.
4. Tạo timeline JSONL và run_id; instrument server/client theo event schema, chuẩn bị kết nối cả hai thiết bị.
5. Thiết lập cấu hình mẫu, credential local; UI tối thiểu gồm bản tin, mode và timeline, không làm admin dashboard.

## Đầu ra bắt buộc

- android/ — source app, manifest, Gradle wrapper và dependency versions có thể build.
- server/ — source, package.json, lockfile, cấu hình mẫu, API snapshot và CLI cập nhật.
- docs/API.md — endpoint/payload/error/version semantics và ví dụ không chứa token.
- docs/EVENT_SCHEMA.md — event fields, correlation IDs, UTC/monotonic time và ví dụ.
- docs/SETUP.md — từ clone đến app/server chạy, có bước cấu hình riêng của người dùng.
- docs/evidence/SEM-04/CHECKS.md — commit, môi trường, bước kiểm tra, expected/actual, link bằng chứng, hạn chế và phần bàn giao.

## Tiêu chí nghiệm thu

- [ ] Build APK debug; server khởi động, app GET và lưu snapshot; đọc cache sau khi offline/mở lại.
- [ ] Manual sync ghi trigger MANUAL; mở UI không âm thầm GET dữ liệu.
- [ ] Server restart không làm version giảm; log từ hai phía liên kết được cùng một run.
- [ ] Có đủ đầu ra và CHECKS.md; người làm giải thích được kết quả, reviewer hoặc người thực hiện tự review được ghi rõ.

## Trạng thái bàn giao

Chưa thực hiện. Tên file ở trên là đầu ra phải tạo khi làm task, không phải bằng chứng đã tồn tại. Cập nhật task và task board cùng lúc khi đổi trạng thái.
