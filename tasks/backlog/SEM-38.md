# SEM-38 — Xử lý duplicate và version hint của push

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-30 01:48:21 UTC.
- Người thực hiện duy nhất: **Trang** (`rosy179`).
- Hạn: **05/11/2026 12:00 (UTC+7)**.
- Công sức: 2/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-07](SEM-07.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-32](SEM-32.md), [SEM-33](SEM-33.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-32 — Triển khai callback FCM và enqueue sync](SEM-32.md) | Trang | `android/ (messaging callback và enqueue adapter)` | `docs/evidence/SEM-32/CHECKS.md` | Todo |
| Bắt đầu | [SEM-33 — Xử lý token refresh và bàn giao PUSH.md](SEM-33.md) | Trang | `android/ (token lifecycle)`<br>`docs/PUSH.md` | `docs/evidence/SEM-33/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-30 01:48:21 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trang cần làm

1. Xử lý payload trùng/cũ và tín hiệu mới tới lúc worker đang chạy thông qua enqueue API chung.
2. Giữ input phía messaging và correlation rõ; không viết lại transaction/version guard của core.
3. Kiểm ba tình huống duplicate/stale/new-during-sync và bàn giao diff messaging.

## Đầu ra bắt buộc

- `android/ (messaging input policy)`
- `docs/evidence/SEM-38/PUSH_INPUT_CASES.md`
- `docs/evidence/SEM-38/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Tín hiệu trùng không gây notification hoặc sync engine riêng; bản mới không bị bỏ qua.
- [ ] Mỗi ca có input/expected/actual trên đúng revision; lỗi core chuyển đúng task SEM-39.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-36](SEM-36.md) cần đầu ra này để **hoàn tất**.
- [SEM-37](SEM-37.md) cần đầu ra này để **bắt đầu**.
- [SEM-47](SEM-47.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Trang thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
