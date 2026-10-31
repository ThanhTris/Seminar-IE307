# SEM-47 — Viết phần silent push và lời dẫn demo 4 phút

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-31 16:46:06 UTC.
- Người thực hiện duy nhất: **Trang** (`rosy179`).
- Hạn: **08/11/2026 16:00 (UTC+7)**.
- Công sức: 2/100 — Nghiên cứu/lập luận.
- Tách từ nhóm cũ: [SEM-09](SEM-09.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-15](SEM-15.md)
- **Hoàn tất còn cần:** [SEM-33](SEM-33.md), [SEM-34](SEM-34.md), [SEM-38](SEM-38.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Kịch bản 15 phút](../../docs/PRESENTATION_PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-15 — Giải thích cơ chế silent push và giới hạn FCM](SEM-15.md) | Trang | `docs/mechanisms/SILENT_PUSH.md` | `docs/evidence/SEM-15/CHECKS.md` | Todo |
| Hoàn tất | [SEM-33 — Xử lý token refresh và bàn giao PUSH.md](SEM-33.md) | Trang | `android/ (token lifecycle)`<br>`docs/PUSH.md` | `docs/evidence/SEM-33/CHECKS.md` | Todo |
| Hoàn tất | [SEM-34 — Chạy pilot push E02 và xác nhận cache nền](SEM-34.md) | Vinh | `experiments/runs/<push-pilot-run>/manifest.json`<br>`experiments/runs/<push-pilot-run>/events.jsonl` | `docs/evidence/SEM-34/CHECKS.md` | Todo |
| Hoàn tất | [SEM-38 — Xử lý duplicate và version hint của push](SEM-38.md) | Trang | `android/ (messaging input policy)`<br>`docs/evidence/SEM-38/PUSH_INPUT_CASES.md` | `docs/evidence/SEM-38/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-31 16:46:06 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trang cần làm

1. Soạn nội dung cơ chế push, payload/TTL/token và giới hạn bằng evidence được bàn giao.
2. Viết một mạch lời dẫn demo cho cả push/periodic/Doze; đánh dấu phần live/playback.
3. Ghi ngưỡng 30 giây đổi video và câu trả lời accepted khác delivered.

## Đầu ra bắt buộc

- `slides/inputs/TRANG.md`
- `slides/DEMO_SCRIPT.md`
- `docs/evidence/SEM-47/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Nội dung demo nằm trong 4 phút và không coi 30 giây là bảo đảm FCM.
- [ ] Mỗi claim có nguồn/evidence hoặc ghi giả thuyết; chỉ giao file input riêng.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-51](SEM-51.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Trang thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
