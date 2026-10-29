# SEM-36 — Tích hợp ba mode và pilot hybrid

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Trí** (`ThanhTris`).
- Hạn: **2026-11-05** (UTC+7).
- Công sức: 3/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-07](SEM-07.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-29](SEM-29.md), [SEM-30](SEM-30.md), [SEM-32](SEM-32.md), [SEM-34](SEM-34.md), [SEM-35](SEM-35.md)
- **Hoàn tất còn cần:** [SEM-38](SEM-38.md), [SEM-39](SEM-39.md), [SEM-40](SEM-40.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Trí cần làm

1. Tích hợp PERIODIC/PUSH/HYBRID; hủy lịch không cần và chờ worker kết thúc hoặc đánh dấu run bị nhiễu.
2. Ghép output robustness của core/messaging và skip-push CLI vào bản tích hợp.
3. Chạy E05/E06 pilot và ghi SYNC về version/concurrency/retry/mode transition.

## Đầu ra bắt buộc

- `android/ (mode controller và tích hợp)`
- `docs/SYNC.md`
- `docs/evidence/SEM-36/HYBRID_PILOT.md`
- `docs/evidence/SEM-36/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] E05 không rollback/ghi trùng/mất cập nhật ở race; E06 phục hồi từ PERIODIC khi bỏ gửi có chủ ý.
- [ ] Không coi hybrid là vượt Doze/force-stop; các nhánh code vẫn dùng cùng sync engine.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-37](SEM-37.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trí thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
