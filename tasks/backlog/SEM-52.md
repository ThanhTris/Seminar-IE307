# SEM-52 — Build APK bàn giao và viết DEMO_RUNBOOK

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-31 12:44:19 UTC.
- Người thực hiện duy nhất: **Trí** (`ThanhTris`).
- Hạn: **11/11/2026 22:00 (UTC+7)**.
- Công sức: 1/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-10](SEM-10.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-37](SEM-37.md)
- **Hoàn tất còn cần:** [SEM-43](SEM-43.md), [SEM-50](SEM-50.md), [SEM-51](SEM-51.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Kịch bản 15 phút](../../docs/PRESENTATION_PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-37 — Chốt bản ứng viên và manifest phục vụ tập chính](SEM-37.md) | Trí | `release/CANDIDATE_MANIFEST.json`<br>`docs/evidence/SEM-37/CANDIDATE_GATE.md` | `docs/evidence/SEM-37/CHECKS.md` | Todo |
| Hoàn tất | [SEM-43 — Chốt SUMMARY và bộ evidence thực nghiệm](SEM-43.md) | Vinh | `experiments/SUMMARY.md` | `docs/evidence/SEM-43/CHECKS.md` | Todo |
| Hoàn tất | [SEM-50 — Hoàn thiện báo cáo, bibliography và CLAIMS](SEM-50.md) | Tuấn | `report/REPORT.md`<br>`research/references.bib`<br>`docs/CLAIMS.md` | `docs/evidence/SEM-50/CHECKS.md` | Todo |
| Hoàn tất | [SEM-51 — Ghép deck 15 phút, PDF và speaker notes](SEM-51.md) | Tuấn | `slides/seminar-ie307.pptx`<br>`slides/seminar-ie307.pdf`<br>`slides/SPEAKER_NOTES.md` | `docs/evidence/SEM-51/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-31 12:44:19 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trí cần làm

1. Build từ source đã đo, ghi commit/config/SHA256 và link APK chạy trên OPPO/emulator.
2. Viết runbook clone/setup/kết nối/reset/mode/live/fallback/cleanup để người khác tái lập.
3. Bàn giao artifact nền cho task video và diễn tập; thay code phải ghi ca đo cần chạy lại.

## Đầu ra bắt buộc

- `release/BUILD_MANIFEST.json`
- `docs/DEMO_RUNBOOK.md`
- `release/ (APK hoặc liên kết tải)`
- `docs/evidence/SEM-52/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Commit/config/checksum nối được với candidate/dữ liệu đo; không tự lấy evidence bản cũ cho code mới.
- [ ] Runbook nêu ngưỡng đổi video 30 giây và cách khôi phục thiết bị.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-53](SEM-53.md) cần đầu ra này để **bắt đầu**.
- [SEM-54](SEM-54.md) cần đầu ra này để **bắt đầu**.
- [SEM-55](SEM-55.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trí thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
