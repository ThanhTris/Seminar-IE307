# SEM-33 — Xử lý token refresh và bàn giao PUSH.md

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-30 20:34:26 UTC.
- Người thực hiện duy nhất: **Trang** (`rosy179`).
- Hạn: **03/11/2026 14:00 (UTC+7)**.
- Công sức: 3/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-06](SEM-06.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-13](SEM-13.md), [SEM-32](SEM-32.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-13 — Kiểm môi trường Node và quyền Firebase](SEM-13.md) | Tâm | `docs/environment/SERVER_FIREBASE.md` | `docs/evidence/SEM-13/CHECKS.md` | Todo |
| Bắt đầu | [SEM-32 — Triển khai callback FCM và enqueue sync](SEM-32.md) | Trang | `android/ (messaging callback và enqueue adapter)` | `docs/evidence/SEM-32/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-30 20:34:26 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trang cần làm

1. Xử lý đăng ký/cập nhật token và cấu hình local tối thiểu, bao gồm onNewToken.
2. Viết payload đã loại token, TTL, callback/enqueue, thao tác setup và giới hạn nhận nền.
3. Kiểm token thay đổi/cấu hình thiếu và giữ credential ngoài repo/log public.

## Đầu ra bắt buộc

- `android/ (token lifecycle)`
- `docs/PUSH.md`
- `docs/evidence/SEM-33/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Có bằng chứng token refresh hoặc blocker được ghi thật, không chỉ token hardcode.
- [ ] PUSH.md đủ để chạy sender và phân biệt accepted/received/applied.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-34](SEM-34.md) cần đầu ra này để **hoàn tất**.
- [SEM-37](SEM-37.md) cần đầu ra này để **bắt đầu**.
- [SEM-38](SEM-38.md) cần đầu ra này để **bắt đầu**.
- [SEM-47](SEM-47.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Trang thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
