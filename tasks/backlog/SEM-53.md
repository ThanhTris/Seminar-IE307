# SEM-53 — Tái lập runbook và quay video dự phòng

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Sẵn sàng**.
- Còn chờ: Nên nhận: [SEM-52](SEM-52.md).
- Đối chiếu Project: 2026-11-13 16:49:37 UTC.
- Người thực hiện duy nhất: **Trí** (`ThanhTris`).
- Hạn: **12/11/2026 15:00 (UTC+7)**.
- Công sức: 2/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-10](SEM-10.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** [SEM-52](SEM-52.md)

Không có gate bắt đầu nghĩa là làm được ngay. Mục Hoàn tất còn cần là đầu vào nên dùng nếu đã có, không chặn chuyển Done: owner chuyển Done khi đầu ra và CHECKS của chính task có thật; đầu vào chưa có thì ghi Not run/giới hạn trong CHECKS. Bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Kịch bản 15 phút](../../docs/PRESENTATION_PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Hoàn tất | [SEM-52 — Build APK bàn giao và viết DEMO_RUNBOOK](SEM-52.md) | Trung | `release/BUILD_MANIFEST.json`<br>`docs/DEMO_RUNBOOK.md`<br>`release/ (APK hoặc liên kết tải)` | `docs/evidence/SEM-52/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-11-13 16:49:37 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trí cần làm

1. Làm theo runbook trên thiết bị, ghi bước tái lập được và blocker/sai lệch để task SEM-52 sửa.
2. Quay video demo thật của đúng build, minh họa đủ chức năng chính (PUSH live, PERIODIC, HYBRID khi bỏ gửi push); video này là mục Video demo phải nộp và cũng là bản dự phòng khi trình bày; gắn nhãn playback và run/commit/checksum.
3. Upload video lên Drive, chia sẻ quyền truy cập cho email giảng viên nêu trong thông báo seminar và kiểm link bằng tài khoản khác; ghi link vào VIDEO_MANIFEST để SEM-55 chèn vào báo cáo; không commit media lớn hoặc lộ token/serial.

## Đầu ra bắt buộc

- `release/VIDEO_MANIFEST.json`
- `docs/evidence/SEM-53/REPRODUCTION.md`
- `Video demo trên Drive, đã chia sẻ cho giảng viên, có liên kết tải`
- `docs/evidence/SEM-53/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Video có metadata thật, minh họa đủ chức năng chính và không thay evidence thực nghiệm bằng mô phỏng.
- [ ] Link Drive mở được bằng tài khoản được chia sẻ; link có trong VIDEO_MANIFEST.
- [ ] Runbook tái lập được hoặc chỉ rõ phần cần hỗ trợ; dữ liệu nhạy cảm đã được loại.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-54](SEM-54.md) cần đầu ra này để **hoàn tất**.
- [SEM-55](SEM-55.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Trí thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
