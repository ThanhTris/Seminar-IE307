# SEM-17 — Giải thích periodic WorkManager và constraints

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Sẵn sàng**.
- Đối chiếu Project: 2026-11-02 02:54:44 UTC.
- Người thực hiện duy nhất: **Trung** (`TrungNQ2645`).
- Hạn: **30/10/2026 18:00 (UTC+7)**.
- Công sức: 3/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-02](SEM-02.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Nguồn kỹ thuật và nghiên cứu](../../research/README.md).

Không cần nhận đầu ra từ task khác để bắt đầu. Owner thực hiện từ tài liệu nền và tự ghi các blocker môi trường/quyền truy cập trong CHECKS của task này.

Status nguồn được đối chiếu Project lúc **2026-11-02 02:54:44 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trung cần làm

1. Viết cơ chế scheduler/constraints/worker, chu kỳ tối thiểu và tính không chính xác thời điểm chạy.
2. Phân biệt work đăng ký, work được chạy, retry và snapshot được áp dụng.
3. Giải thích Doze/network constraint và cách đọc timeline theo nguồn chính thức có version.

## Đầu ra bắt buộc

- `docs/mechanisms/PERIODIC_FETCH.md`
- `docs/evidence/SEM-17/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Không coi chu kỳ cấu hình là cam kết chạy đúng từng mốc.
- [ ] Phân biệt periodic tự nhiên với force-run/test driver chỉ dùng debug.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-19](SEM-19.md) cần đầu ra này để **hoàn tất**.
- [SEM-30](SEM-30.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trung thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
