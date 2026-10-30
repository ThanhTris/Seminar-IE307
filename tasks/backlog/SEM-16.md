# SEM-16 — Lập ma trận lifecycle và protocol E01–E06

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Sẵn sàng**.
- Đối chiếu Project: 2026-10-30 20:34:26 UTC.
- Người thực hiện duy nhất: **Vinh** (`Vinh5905`).
- Hạn: **30/10/2026 18:00 (UTC+7)**.
- Công sức: 2/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-02](SEM-02.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Protocol cốt lõi](../../docs/EXPERIMENT_PROTOCOL.md).

Không cần nhận đầu ra từ task khác để bắt đầu. Owner thực hiện từ tài liệu nền và tự ghi các blocker môi trường/quyền truy cập trong CHECKS của task này.

Status nguồn được đối chiếu Project lúc **2026-10-30 20:34:26 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Vinh cần làm

1. Lập bảng foreground/background/process death/recent-swipe/force-stop/Doze và giả thuyết cần đo.
2. Chuyển EXPERIMENT_PROTOCOL thành checklist có số lượt, cửa sổ, reset/cleanup và tiêu chí run hợp lệ.
3. Lập lịch độc quyền cho từng app/thiết bị, tách pilot 02–05/11 với main 06–07/11.

## Đầu ra bắt buộc

- `experiments/PROTOCOL.md`
- `experiments/RUN_SCHEDULE.md`
- `docs/evidence/SEM-16/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Giữ nguyên số lượt và cửa sổ cốt lõi E01–E06; dự trù ít nhất 10–12 giờ quan sát.
- [ ] Màn hình tắt không tự được gọi Doze; force-stop có mốc người dùng mở lại và cleanup.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-19](SEM-19.md) cần đầu ra này để **hoàn tất**.
- [SEM-29](SEM-29.md) cần đầu ra này để **bắt đầu**.
- [SEM-34](SEM-34.md) cần đầu ra này để **bắt đầu**.
- [SEM-41](SEM-41.md) cần đầu ra này để **bắt đầu**.
- [SEM-42](SEM-42.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Vinh thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
