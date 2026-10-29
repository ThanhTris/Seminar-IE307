# SEM-28 — Ghép manual sync đầu cuối và chốt hướng dẫn setup

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Trí** (`ThanhTris`).
- Hạn: **2026-10-31** (UTC+7).
- Công sức: 1/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-05](SEM-05.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-23](SEM-23.md), [SEM-24](SEM-24.md), [SEM-25](SEM-25.md), [SEM-27](SEM-27.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Trí cần làm

1. Nhận app/server/core/exporter đã bàn giao và nối nút manual với enqueue.
2. Chạy một luồng update → manual worker → Room → UI/timeline, mở lại offline.
3. Tổng hợp SETUP từ tài liệu Android/server, ghi M1 và revision đã ghép.

## Đầu ra bắt buộc

- `docs/SETUP.md`
- `docs/evidence/SEM-28/M1.md`
- `docs/evidence/SEM-28/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Build debug/server chạy; MANUAL có nhãn và UI mở lại không phát sinh GET.
- [ ] M1 chỉ Pass khi có run thật; thiếu credential/mạng ghi blocker, không tự nghiệm thu từ tài liệu.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-30](SEM-30.md) cần đầu ra này để **bắt đầu**.
- [SEM-32](SEM-32.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trí thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
