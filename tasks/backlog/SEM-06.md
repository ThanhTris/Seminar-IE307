# SEM-06 — Triển khai và quan sát push im lặng

- Status: backlog
- Lịch mục tiêu: 01–03/11/2026
- Công sức: 10/100 — Thực hành
- Owner: Trang
- Reviewer: Trí
- Phối hợp: Vinh, Tâm
- Điều kiện bắt đầu: SEM-02, SEM-04 đã có đầu ra cần dùng
- Điều kiện hoàn tất bổ sung: không ngoài điều kiện bắt đầu

## Đầu vào

App/server baseline, schema event, Firebase project đã cấu hình, cơ chế API v1 trong MECHANISMS.

## Việc cần làm

Phân việc: Trang làm client FCM, token refresh, enqueue worker, PUSH.md và pilot; Tâm làm lệnh gửi server, TTL và correlation ID; Vinh xác nhận log/pilot trên hai thiết bị. Trang chịu trách nhiệm luồng push đầu cuối.

Theo [phân công 6 người](../../docs/TEAM_ASSIGNMENTS.md); owner tổng hợp đầu ra và CHECKS, reviewer kiểm trước khi chuyển done.

1. Server gửi AndroidConfig v1 data-only normal priority với run/version, TTL khai báo rõ; không gắn notification payload.
2. Client ghi received rồi enqueue regular work để fetch snapshot; không để async network rời lifecycle callback.
3. Lưu/cập nhật token theo onNewToken và làm mới cấu hình gửi; không commit giá trị token.
4. Hủy periodic khi thử PUSH; phân biệt FCM accepted, callback, worker và cache applied.
5. Chạy pilot foreground/background trên emulator và OPPO; payload/callback luôn khớp phiên bản đã chọn.

## Đầu ra bắt buộc

- android/ — FirebaseMessagingService và phần enqueue sync, xử lý token refresh.
- server/ — lệnh gửi data-only, kết quả accepted/rejected và message correlation.
- docs/PUSH.md — payload mẫu đã loại token, đường đi callback, TTL, cách đăng ký/cập nhật token và giới hạn.
- experiments/runs/<run_id>/ — pilot push ghi nhận từng event.
- docs/evidence/SEM-06/CHECKS.md — commit, môi trường, bước kiểm tra, expected/actual, link bằng chứng, hạn chế và phần bàn giao.

## Tiêu chí nghiệm thu

- [ ] Background nhận tín hiệu và cập nhật cache trước khi mở app trong ít nhất một pilot hợp lệ.
- [ ] Không có thông báo do demo tự tạo; ghi màn hình và log để xác nhận data-only.
- [ ] Không báo FCM accepted là delivered; không dùng high-priority silent traffic để che tình huống chậm.
- [ ] Khóa SDK ổn định; AndroidConfigV2 EAP chỉ là ghi chú trong nguồn, không trộn code vào baseline.
- [ ] Có đủ đầu ra và CHECKS.md; người làm giải thích được kết quả, reviewer được phân công kiểm tra và ghi kết luận.

## Trạng thái bàn giao

Chưa thực hiện. Tên file ở trên là đầu ra phải tạo khi làm task, không phải bằng chứng đã tồn tại. Cập nhật task và task board cùng lúc khi đổi trạng thái.
