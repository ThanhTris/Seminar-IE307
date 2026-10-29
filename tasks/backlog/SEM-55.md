# SEM-55 — Chốt manifest và gói bàn giao seminar

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-29 16:22:16 UTC.
- Người thực hiện duy nhất: **Trí** (`ThanhTris`).
- Hạn: **2026-11-12** (UTC+7).
- Công sức: 1/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-10](SEM-10.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-43](SEM-43.md), [SEM-50](SEM-50.md), [SEM-51](SEM-51.md), [SEM-52](SEM-52.md), [SEM-53](SEM-53.md), [SEM-54](SEM-54.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Kịch bản 15 phút](../../docs/PRESENTATION_PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-43 — Chốt SUMMARY và bộ evidence thực nghiệm](SEM-43.md) | Vinh | `experiments/SUMMARY.md` | `docs/evidence/SEM-43/CHECKS.md` | Todo |
| Bắt đầu | [SEM-50 — Hoàn thiện báo cáo, bibliography và CLAIMS](SEM-50.md) | Tuấn | `report/REPORT.md`<br>`research/references.bib`<br>`docs/CLAIMS.md` | `docs/evidence/SEM-50/CHECKS.md` | Todo |
| Bắt đầu | [SEM-51 — Ghép deck 15 phút, PDF và speaker notes](SEM-51.md) | Tuấn | `slides/seminar-ie307.pptx`<br>`slides/seminar-ie307.pdf`<br>`slides/SPEAKER_NOTES.md` | `docs/evidence/SEM-51/CHECKS.md` | Todo |
| Bắt đầu | [SEM-52 — Build APK bàn giao và viết DEMO_RUNBOOK](SEM-52.md) | Trí | `release/BUILD_MANIFEST.json`<br>`docs/DEMO_RUNBOOK.md`<br>`release/ (APK hoặc liên kết tải)` | `docs/evidence/SEM-52/CHECKS.md` | Todo |
| Bắt đầu | [SEM-53 — Tái lập runbook và quay video dự phòng](SEM-53.md) | Vinh | `release/VIDEO_MANIFEST.json`<br>`docs/evidence/SEM-53/REPRODUCTION.md`<br>`Video demo/fallback có liên kết tải` | `docs/evidence/SEM-53/CHECKS.md` | Todo |
| Bắt đầu | [SEM-54 — Điều phối hai lần diễn tập và ghi thời lượng](SEM-54.md) | Tuấn | `docs/REHEARSAL.md` | `docs/evidence/SEM-54/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-29 16:22:16 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trí cần làm

1. Ghép chỉ mục APK/server/source/slide/report/video/checks thành manifest cuối.
2. Rà link tải/checksum/version và danh mục phần còn thiếu, dành 13/11 sửa lỗi cuối.
3. Ghi quan hệ commit code đã đo và commit tài liệu cuối; không yêu cầu hai commit phải trùng.

## Đầu ra bắt buộc

- `release/MANIFEST.json`
- `release/README.md`
- `docs/evidence/SEM-55/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Mọi artifact truy được source/build/evidence và tải/đọc được.
- [ ] Video/rehearsal/report/slide có thật trước khi Done, phần chưa thực hiện liệt kê rõ.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- Không có task sau trực tiếp.

## Ranh giới thực hiện

Một task chỉ có Trí thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
