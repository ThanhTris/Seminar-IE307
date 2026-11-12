# SEM-50 — Hoàn thiện báo cáo, bibliography và CLAIMS

- Trạng thái: **In Progress** (Project).
- Trạng thái đầu vào: **Đang thực hiện**.
- Đối chiếu Project: 2026-11-12 13:54:39 UTC.
- Người thực hiện duy nhất: **Tuấn** (`mtuan2491`).
- Hạn: **09/11/2026 22:00 (UTC+7)**.
- Công sức: 2/100 — Nghiên cứu/lập luận.
- Tách từ nhóm cũ: [SEM-09](SEM-09.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** [SEM-19](SEM-19.md), [SEM-20](SEM-20.md), [SEM-21](SEM-21.md), [SEM-22](SEM-22.md), [SEM-43](SEM-43.md), [SEM-45](SEM-45.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Kịch bản 15 phút](../../docs/PRESENTATION_PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Hoàn tất | [SEM-19 — Tổng hợp mô hình cơ chế và câu hỏi phản biện](SEM-19.md) | Tuấn | `docs/MECHANISMS.md`<br>`docs/QUESTIONS.md` | `docs/evidence/SEM-19/CHECKS.md` | Done |
| Hoàn tất | [SEM-20 — Đọc bài nghiên cứu thứ nhất và ghi chú nguồn](SEM-20.md) | Tuấn | `research/notes/PAPER_1.md`<br>`research/metadata/paper-1.bib` | `docs/evidence/SEM-20/CHECKS.md` | Done |
| Hoàn tất | [SEM-21 — Đọc bài nghiên cứu thứ hai và ghi chú nguồn](SEM-21.md) | Tâm | `research/notes/PAPER_2.md`<br>`research/metadata/paper-2.bib` | `docs/evidence/SEM-21/CHECKS.md` | Done |
| Hoàn tất | [SEM-22 — Đối chiếu hai bài nghiên cứu với API push hiện hành](SEM-22.md) | Trang | `research/notes/API_CROSSCHECK.md` | `docs/evidence/SEM-22/CHECKS.md` | Done |
| Hoàn tất | [SEM-43 — Chốt SUMMARY và bộ evidence thực nghiệm](SEM-43.md) | Vinh | `experiments/SUMMARY.md` | `docs/evidence/SEM-43/CHECKS.md` | Todo |
| Hoàn tất | [SEM-45 — Viết parser log và sinh results.csv](SEM-45.md) | Tuấn | `experiments/scripts/analyze.*`<br>`experiments/results.csv` | `docs/evidence/SEM-45/CHECKS.md` | In Progress |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-11-12 13:54:39 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Tuấn cần làm

1. Viết báo cáo bằng template LaTeX của môn theo bố cục giảng viên yêu cầu trong docs/SUBMISSION_REQUIREMENTS.md: 1. Giới thiệu đề tài; 2. Hiện thực đề tài; 3. Kết luận và khuyến nghị; phụ lục Bảng phân công công việc lấy từ TEAM_ASSIGNMENTS.
2. Chương 2 có đủ: môi trường thực hiện, công cụ/công nghệ, các bước cài đặt, cấu hình, các bước triển khai/thực thi, kết quả đầu ra, minh họa chức năng/thành phần chính, vấn đề gặp phải và cách xử lý, mục Video demo (SEM-55 chèn link Drive khi đóng gói).
3. Chuyển nội dung bản nháp REPORT.md vào LaTeX; ghép metadata hai bài vào references.bib; tạo CLAIMS có nguồn/vị trí/case/evidence/trạng thái.
4. Đối chiếu các kết luận với SUMMARY, không trình bày giả thuyết như số đo; biên dịch PDF từ mã LaTeX đã commit.

## Đầu ra bắt buộc

- `report/latex/ (mã nguồn LaTeX theo template môn, gồm main.tex)`
- `report/seminar-ie307.pdf`
- `research/references.bib`
- `docs/CLAIMS.md`
- `docs/evidence/SEM-50/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Bố cục đúng 3 chương và phụ lục Bảng phân công theo yêu cầu giảng viên; chương Hiện thực đủ 9 mục con.
- [ ] PDF biên dịch được từ mã LaTeX trong repo; hai nghiên cứu có vai trò trong lập luận, DOI/metadata khớp và citations truy được.
- [ ] Số liệu/giới hạn khớp logs/CSV/SUMMARY; phần chưa chạy nêu rõ.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-51](SEM-51.md) cần đầu ra này để **hoàn tất**.
- [SEM-52](SEM-52.md) cần đầu ra này để **hoàn tất**.
- [SEM-55](SEM-55.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Tuấn thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
