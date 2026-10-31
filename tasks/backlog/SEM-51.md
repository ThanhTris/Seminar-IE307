# SEM-51 — Ghép deck 15 phút, PDF và speaker notes

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chuẩn bị trước**.
- Đối chiếu Project: 2026-10-31 16:46:06 UTC.
- Người thực hiện duy nhất: **Tuấn** (`mtuan2491`).
- Hạn: **10/11/2026 22:00 (UTC+7)**.
- Công sức: 3/100 — Nghiên cứu/lập luận.
- Tách từ nhóm cũ: [SEM-09](SEM-09.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** [SEM-46](SEM-46.md), [SEM-47](SEM-47.md), [SEM-48](SEM-48.md), [SEM-49](SEM-49.md), [SEM-50](SEM-50.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Kịch bản 15 phút](../../docs/PRESENTATION_PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Hoàn tất | [SEM-46 — Viết phần mở bài và bàn giao lời dẫn thao tác demo](SEM-46.md) | Trí | `slides/inputs/TRI.md` | `docs/evidence/SEM-46/CHECKS.md` | Todo |
| Hoàn tất | [SEM-47 — Viết phần silent push và lời dẫn demo 4 phút](SEM-47.md) | Trang | `slides/inputs/TRANG.md`<br>`slides/DEMO_SCRIPT.md` | `docs/evidence/SEM-47/CHECKS.md` | Todo |
| Hoàn tất | [SEM-48 — Viết nội dung và biểu đồ kết quả cho bài nói](SEM-48.md) | Vinh | `slides/inputs/VINH.md`<br>`slides/inputs/results/` | `docs/evidence/SEM-48/CHECKS.md` | Todo |
| Hoàn tất | [SEM-49 — Viết phần kiến trúc và lập luận nghiên cứu thứ hai](SEM-49.md) | Tâm | `slides/inputs/TAM.md` | `docs/evidence/SEM-49/CHECKS.md` | Todo |
| Hoàn tất | [SEM-50 — Hoàn thiện báo cáo, bibliography và CLAIMS](SEM-50.md) | Tuấn | `report/REPORT.md`<br>`research/references.bib`<br>`docs/CLAIMS.md` | `docs/evidence/SEM-50/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-31 16:46:06 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Tuấn cần làm

1. Chuẩn bị dàn ý rồi ghép input của từng owner vào một deck chính.
2. Xuất PPTX/PDF và notes theo PRESENTATION_PLAN: 7 lượt nói, 30 giây chuyển tiếp trong 15 phút.
3. Kiểm source/evidence/link, các nhãn live/playback và thời lượng demo 4 phút.

## Đầu ra bắt buộc

- `slides/seminar-ie307.pptx`
- `slides/seminar-ie307.pdf`
- `slides/SPEAKER_NOTES.md`
- `docs/evidence/SEM-51/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Bộ slide chỉnh sửa được và PDF đọc được; không tăng tổng thời lượng vì chuyển người.
- [ ] Bản cuối chỉ dùng input/evidence đã bàn giao; không ghi đã có kết quả khi chưa có.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-52](SEM-52.md) cần đầu ra này để **hoàn tất**.
- [SEM-54](SEM-54.md) cần đầu ra này để **bắt đầu**.
- [SEM-55](SEM-55.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Tuấn thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
