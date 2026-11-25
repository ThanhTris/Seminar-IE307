# SEM-50 — Kiểm chứng và bàn giao báo cáo LaTeX

Tuấn (`mtuan2491`), 25/11/2026. Nhánh `codex/SEM-50-latex-report` bắt đầu từ `main` tại `db8dc5f` (merge SEM-45). Nguồn biên dịch tại `7434eb5922c9c4bf6f409f5212a554a13be95e5f`. Trạng thái bàn giao là bản review.

[Yêu cầu SEM-50](../../../tasks/backlog/SEM-50.md) · [Yêu cầu giảng viên](../../SUBMISSION_REQUIREMENTS.md) · [Nguồn LaTeX và hướng dẫn build](../../../report/latex/README.md) · [PDF](../../../report/seminar-ie307.pdf) · [Bibliography](../../../research/references.bib) · [CLAIMS](../../CLAIMS.md)

## Kiểm chứng

| Kiểm tra | Mong đợi | Thực tế | Kết quả |
|---|---|---|---|
| Bố cục và hiển thị | Ba chương, chín mục trong chương Hiện thực, phụ lục và mục lục | PDF A4 10 trang. Đã render và xem cả 10 trang, kiểm tiếng Việt, bảng, hình, số trang và mục lục | Pass cho bố cục bản review |
| Phụ lục phân công | Mỗi task xuất hiện đúng một lần với owner đúng | 45/45 task khớp [catalog](../../../tasks/catalog.json) và bảng [TEAM_ASSIGNMENTS](../../TEAM_ASSIGNMENTS.md). `scripts/update_task_snapshot.py --check` xác minh 45 thẻ Project, mỗi thẻ có một assignee khớp owner | Pass |
| Trích dẫn và truy vết | Hai paper có DOI, nội dung nằm trong phạm vi nguồn. Citation và link evidence dùng được | Cả hai DOI có trong bibliography và là link trong PDF. Đã kiểm 29 đích PDF ghim theo commit và 50 link Markdown nội bộ. CLAIMS ghi case, vị trí, evidence và trạng thái, đối chiếu với ghi chú SEM-20–22 | Pass |
| Biên dịch lại | Nguồn đã commit có thể tạo PDF và mục lục, citation đầy đủ | Tectonic `0.17.0+20260731`, Windows, Times New Roman, BibTeX và `SOURCE_DATE_EPOCH=1795564800`. Hai lượt build riêng cho PDF khớp từng byte trên cấu hình này. SHA-256 `9244786097a77d07f2d05d5b8e23eadbe90b0c5394e0e19eaa6030809fa734d2` | Pass |
| Tái lập dữ liệu | CSV và summary khớp bộ đã merge | Analyzer v0.7.0 chạy `--dataset pilot --source-index docs/evidence/SEM-45/INPUTS.json` với output riêng. `results.csv` và `summary.json` khớp từng byte | Pass |
| Phạm vi mẫu | Giữ riêng pilot, nhóm route/build và mẫu số main | 23 pilot, 10 nhóm, 10 VALID/COMPLETED, 13 INVALID; outcome nguồn 15 SUCCESS / 5 TIMEOUT / 2 FAILURE / 1 UNKNOWN. Tất cả `eligible=false`. Kế hoạch main có 33 slot, số lượt main hợp lệ bằng 0, latency main N/A | Pass |
| E01 ngày 20/11 | Số chu kỳ theo elapsed, target và route khớp với log/manifest | OPPO run-03 có 5 request PERIODIC riêng, attempt 0, trong cửa sổ. Apply v5 tại 930021 ms tính từ đầu cửa sổ, với bốn HTTP 304 tiếp theo trong cửa sổ. Run-02 ABORTED/INVALID, thiếu mốc mở, count null. Emulator gateway có 2 chu kỳ và thuộc nhóm khác host HTTP. Cả ba dùng APK `814347F…` | Pass |
| Template môn và minh họa app | Có template được giảng viên cung cấp và ảnh thật của app | Bản review dùng lớp `report`, sơ đồ kiến trúc và timeline log. Repo chưa có template môn và ảnh app cho phần minh họa | Not run |
| Video trên Drive | Có video, link xem và manifest đã xác minh | Manifest nháp ở `daf009b` ghi `NOT_RUN`, `drive_url=null`, quyền Drive và playback chưa xác minh. [PR SEM-53 #34](https://github.com/ThanhTris/Seminar-IE307/pull/34) | Not run |
| Candidate/main | Có dữ liệu main và clock kiểm soát cho kết luận về latency; có evidence E02 FCM đầu cuối và E05 race | Bản review dùng evidence đã bàn giao, gồm pilot và kiểm logic đã có. Chưa chạy bổ sung trên thiết bị trong SEM-50. [CHECKS SEM-45](../SEM-45/CHECKS.md) | Not run |

Tectonic báo cảnh báo đường dẫn font Windows và khoảng trắng ở hai đoạn khi dàn trang. Build hoàn tất, log không báo thiếu glyph, citation chưa giải quyết hoặc hộp tràn lề. Tái lập từng byte được kiểm trên cùng phiên bản công cụ và font.

## Đã hoàn thành

- Chuyển bản nháp sang LaTeX theo bố cục yêu cầu, biên dịch PDF, thêm hướng dẫn build, phụ lục phân công, bibliography và CLAIMS.
- Dùng đầu ra SEM-19/20/21/22 cho mô hình và nghiên cứu. Dùng [SUMMARY SEM-43](../../../experiments/SUMMARY.md) ở `007a1aa` cho loạt SEM-41 và kế hoạch main. Đối chiếu ba pilot E01 ngày 20/11 từ [CSV SEM-45](../../../experiments/results.csv), [CHECKS SEM-42](../SEM-42/CHECKS.md) và [build manifest](../../../release/BUILD_MANIFEST.json). SEM-43 có thể cập nhật SUMMARY riêng theo CSV mới.

## Chưa hoàn thành và bàn giao còn thiếu

| Hạng mục | Cần nhận | Phần còn lại |
|---|---|---|
| Template LaTeX | Bộ template chính thức của môn (file lớp hoặc nguồn LaTeX và tài nguyên đi kèm) từ nhóm hoặc giảng viên | SEM-50 chuyển nội dung sang template và kiểm lại PDF |
| Ảnh app và timeline | Ảnh thật từ người chạy demo, kèm run/build tương ứng để truy vết | SEM-50 chèn ảnh và chú thích tại §2.7 |
| Video demo | SEM-53 (Trí) bàn giao `release/VIDEO_MANIFEST.json`, video và link Drive với quyền cho giảng viên | SEM-55 (Tuấn) xác minh quyền xem, chèn link vào §2.9 và biên dịch lại PDF |
| Dữ liệu main | Candidate của SEM-37, run main và dữ liệu clock đủ căn cứ; SEM-44 nếu có kiểm độc lập | Chương Kết quả hiện dùng pilot, giữ main N/A cho tới khi có dữ liệu đủ điều kiện |

Bản review và CLAIMS có thể dùng cho SEM-51 và SEM-52 theo phạm vi pilot đã ghi. SEM-55 dùng PDF biên dịch lại sau khi nhận đủ template, hình minh họa và link xem video.
