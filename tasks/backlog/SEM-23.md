# SEM-23 — Tạo scaffold Android và UI cache/timeline

- Trạng thái: Todo — chưa thực hiện.
- Người thực hiện duy nhất: **Trí** (`ThanhTris`).
- Hạn: **2026-10-31** (UTC+7).
- Công sức: 4/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-04](SEM-04.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-11](SEM-11.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

## Việc Trí cần làm

1. Tạo project Kotlin/Compose, manifest, Gradle wrapper và dependency đã pin.
2. Làm UI bản tin/version/mode/lần sync/timeline lọc run_id và adapter đọc cache từ core.
3. Giữ code trong build/ui/config; không viết thêm sync engine hay tự gọi GET lúc mở UI.

## Đầu ra bắt buộc

- `android/ (build, manifest, ui, config)`
- `docs/setup/ANDROID.md`
- `docs/evidence/SEM-23/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Build được debug APK; UI trạng thái rỗng và timeline hiển thị rõ trigger.
- [ ] Không auto-fetch khi mở app; nút manual phải dùng giao diện enqueue của task core khi được bàn giao.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-25](SEM-25.md) cần đầu ra này để **bắt đầu**.
- [SEM-28](SEM-28.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trí thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
