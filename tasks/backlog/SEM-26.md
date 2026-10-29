# SEM-26 — Chốt hợp đồng API và event schema

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Tâm** (`HoaiTam`).
- Hạn: **2026-10-30** (UTC+7).
- Công sức: 2/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-04](SEM-04.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-11](SEM-11.md), [SEM-13](SEM-13.md), [SEM-14](SEM-14.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Tâm cần làm

1. Viết health/GET snapshot/update, payload/error và version semantics đủ để client code theo contract.
2. Chốt event fields và nullable correlation, UTC/monotonic, outcome/reason.
3. Đưa ví dụ đã loại token và phiên bản contract; thay đổi sau bàn giao phải ghi delta.

## Đầu ra bắt buộc

- `docs/API.md`
- `docs/EVENT_SCHEMA.md`
- `docs/evidence/SEM-26/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Snapshot/version/error rõ ràng, event accepted/received/started/applied riêng biệt.
- [ ] Core và server có thể triển khai theo contract mà không cần chờ code của nhau.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-24](SEM-24.md) cần đầu ra này để **hoàn tất**.
- [SEM-25](SEM-25.md) cần đầu ra này để **bắt đầu**.
- [SEM-27](SEM-27.md) cần đầu ra này để **bắt đầu**.
- [SEM-45](SEM-45.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Tâm thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
