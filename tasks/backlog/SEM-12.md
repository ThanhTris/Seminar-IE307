# SEM-12 — Lập hồ sơ OPPO và emulator

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Sẵn sàng**.
- Đối chiếu Project: 2026-10-30 01:48:21 UTC.
- Người thực hiện duy nhất: **Vinh** (`Vinh5905`).
- Hạn: **30/10/2026 12:00 (UTC+7)**.
- Công sức: 1/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-01](SEM-01.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Protocol cốt lõi](../../docs/EXPERIMENT_PROTOCOL.md).

Không cần nhận đầu ra từ task khác để bắt đầu. Owner thực hiện từ tài liệu nền và tự ghi các blocker môi trường/quyền truy cập trong CHECKS của task này.

Status nguồn được đối chiếu Project lúc **2026-10-30 01:48:21 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Vinh cần làm

1. Đọc Android/API/ColorOS thực tế qua thiết bị; ghi alias thay cho serial.
2. Chọn emulator có Google Play services, kiểm ADB và cách lấy log.
3. Ghi lịch sử dụng OPPO với người đang giữ máy và cách kết nối thiết bị với server.

## Đầu ra bắt buộc

- `docs/environment/DEVICES.md`
- `docs/evidence/SEM-12/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] ADB nhận emulator và OPPO hoặc ghi blocker cụ thể; không tự mặc định phiên bản OS.
- [ ] Hồ sơ phân biệt mạng tới server với Internet/FCM, không dùng localhost PC làm địa chỉ OPPO.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-19](SEM-19.md) cần đầu ra này để **hoàn tất**.
- [SEM-20](SEM-20.md) cần đầu ra này để **hoàn tất**.
- [SEM-21](SEM-21.md) cần đầu ra này để **hoàn tất**.
- [SEM-24](SEM-24.md) cần đầu ra này để **bắt đầu**.
- [SEM-42](SEM-42.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Vinh thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
