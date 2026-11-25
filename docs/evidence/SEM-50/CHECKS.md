# SEM-50 — Kiểm chứng và bàn giao báo cáo LaTeX

Tuấn (`mtuan2491`), 26/11/2026. Nhánh `codex/SEM-50-latex-report` bắt đầu từ `main` tại `db8dc5f` (merge SEM-45). Nguồn biên dịch tại `376d3ac710d581960295f5debcb83119b518a0c2`. Trạng thái bàn giao là bản review.

[Yêu cầu SEM-50](../../../tasks/backlog/SEM-50.md) · [Yêu cầu giảng viên](../../SUBMISSION_REQUIREMENTS.md) · [Nguồn LaTeX và hướng dẫn build](../../../report/latex/README.md) · [PDF](../../../report/seminar-ie307.pdf) · [Bibliography](../../../research/references.bib) · [CLAIMS](../../CLAIMS.md)

## Kiểm chứng

| Kiểm tra | Mong đợi | Thực tế | Kết quả |
|---|---|---|---|
| Bố cục và hiển thị | Bìa, mục lục, danh sách hình, danh sách bảng, tóm tắt, ba chương và phụ lục | PDF A4 16 trang. Đã render và xem đủ 16 trang. Chương Hiện thực có đủ chín mục. Kiểm tiếng Việt, danh sách tự sinh, số trang, ba hình và hai bảng | Pass |
| Phụ lục phân công | Mỗi task xuất hiện đúng một lần với owner đúng | 45/45 task khớp [catalog](../../../tasks/catalog.json) và bảng [TEAM_ASSIGNMENTS](../../TEAM_ASSIGNMENTS.md). `scripts/update_task_snapshot.py --check` xác minh 45 thẻ Project, mỗi thẻ có một assignee khớp owner | Pass |
| Trích dẫn và truy vết | Hai paper có DOI, nội dung nằm trong phạm vi nguồn. Citation và link evidence dùng được | Cả hai DOI có trong bibliography và là link trong PDF. Đã kiểm 31 đích ghim theo commit. CLAIMS ghi case, vị trí, evidence và trạng thái | Pass |
| Biên dịch lại | Nguồn đã commit tạo PDF với mục lục và citation đầy đủ | Tectonic `0.17.0+20260731`, Windows, Times New Roman, BibTeX và `SOURCE_DATE_EPOCH=1795651200`. Hai lượt build ra thư mục riêng cho PDF khớp từng byte. SHA-256 `15fd04d091d83419bc66af70fc8ce1336ae49dc953533750ac4aaba5e8496184` | Pass |
| Tái lập dữ liệu | CSV và summary khớp bộ đã merge | Analyzer v0.7.0 chạy `--dataset pilot --source-index docs/evidence/SEM-45/INPUTS.json` với output riêng. `results.csv` và `summary.json` khớp từng byte | Pass |
| Phạm vi mẫu | Giữ riêng pilot, nhóm route/build và mẫu số main | 23 pilot, 10 nhóm, 10 VALID/COMPLETED, 13 INVALID; outcome nguồn 15 SUCCESS / 5 TIMEOUT / 2 FAILURE / 1 UNKNOWN. Tất cả `eligible=false`. Kế hoạch main có 33 slot, số lượt main hợp lệ bằng 0, latency main N/A | Pass |
| E01 ngày 20/11 | Số chu kỳ theo elapsed, target và route khớp với log/manifest | OPPO run-03 có 5 request PERIODIC riêng, attempt 0, trong cửa sổ. Apply v5 tại 930021 ms tính từ đầu cửa sổ, với bốn HTTP 304 tiếp theo trong cửa sổ. Run-02 ABORTED/INVALID, thiếu mốc mở, count null. Emulator gateway có 2 chu kỳ và thuộc nhóm khác host HTTP. Cả ba dùng APK `814347F…` | Pass |
| Lược đồ Room | Tên bảng, khóa chính và các cột minh họa khớp source | Đối chiếu `bulletin_items`/`id`, `sync_metadata`/`key`, `timeline_events`/`eventId` với entity Room v2. Hình mô tả schema từ source | Pass |
| Timeline OPPO | Vị trí năm mốc và kết quả từng request khớp log | Phút 15,500 / 31,346 / 46,717 / 63,875 / 78,877. Nối theo request ID và work ID. Lần đầu HTTP 200 và apply v5, bốn lần sau HTTP 304 và giữ v5 | Pass |
| Ảnh app và Database Inspector | Có ảnh chụp thật kèm run/build cho §2.7 | Có mã nguồn UI, schema và log đã kiểm. Chưa nhận ảnh chụp từ lượt demo | Not run |
| Video trên Drive | Có video, link xem và manifest đã xác minh | Manifest nháp ở `daf009b` ghi `NOT_RUN`, `drive_url=null`, quyền Drive và playback chưa xác minh. [PR SEM-53 #34](https://github.com/ThanhTris/Seminar-IE307/pull/34) | Not run |
| Candidate/main | Có dữ liệu main và clock kiểm soát cho kết luận về latency; có evidence E02 FCM đầu cuối và E05 race | Bản review dùng evidence đã bàn giao, gồm pilot và kiểm logic đã có. Chưa chạy bổ sung trên thiết bị trong SEM-50. [CHECKS SEM-45](../SEM-45/CHECKS.md) | Not run |

Tectonic báo cảnh báo đường dẫn font Windows và thay thế cỡ font LaTeX tối đa 1 pt. Build hoàn tất, log không báo thiếu glyph, citation chưa giải quyết hoặc hộp tràn lề. Tái lập từng byte được kiểm trên cùng phiên bản công cụ và font.

## Đã hoàn thành

- Chuyển mẫu Word sang LaTeX, biên dịch PDF theo bố cục yêu cầu và bàn giao nguồn, phụ lục phân công, bibliography, CLAIMS và hướng dẫn build.
- Bổ sung sơ đồ kiến trúc, lược đồ ba bảng Room theo source và timeline OPPO run-03 từ JSONL. Bảng protocol phân biệt điều kiện, cửa sổ và tiêu chí quan sát cho E01–E06.
- Dùng đầu ra SEM-19/20/21/22 cho mô hình và nghiên cứu. Dùng [SUMMARY SEM-43](../../../experiments/SUMMARY.md) ở `007a1aa` cho loạt SEM-41 và kế hoạch main. Đối chiếu ba pilot E01 ngày 20/11 từ [CSV SEM-45](../../../experiments/results.csv), [CHECKS SEM-42](../SEM-42/CHECKS.md) và [build manifest](../../../release/BUILD_MANIFEST.json). SEM-43 có thể cập nhật SUMMARY riêng theo CSV mới.

## Chưa hoàn thành và bàn giao còn thiếu

| Hạng mục | Cần nhận | Phần còn lại |
|---|---|---|
| Trang bìa | Số nhóm, họ tên đầy đủ và MSSV đã xác nhận, cùng thời gian thực hiện nếu cần ghi theo mẫu | SEM-50 bổ sung thông tin hành chính trước bản nộp |
| §2.7.1 — Ảnh các bảng Room | Ảnh Database Inspector cho `bulletin_items`, `sync_metadata`, `timeline_events` từ một build và run đã xác định. Ẩn giá trị token trong metadata | SEM-50 chèn ảnh bảng/dòng minh họa kèm nguồn và phiên bản bên cạnh lược đồ |
| §2.7.2 — Ảnh giao diện và mốc thực thi | Ảnh màn hình bảng tin có mode, cache version và timeline, kèm run/build. Dùng lượt PERIODIC đã kiểm. Bổ sung ảnh PUSH với chuỗi callback–apply và HYBRID với log skip và apply PERIODIC khi có evidence tương ứng | SEM-50 chèn ảnh và chú thích theo từng cơ chế. Đối chiếu với log trước khi mô tả kết quả |
| §2.9 — Video demo | SEM-53 (Trí) bàn giao `release/VIDEO_MANIFEST.json`, video, link Drive và quyền cho giảng viên | SEM-55 (Tuấn) xác minh quyền xem, chèn link vào §2.9 và biên dịch lại PDF |
| Dữ liệu main | Candidate của SEM-37, run main và dữ liệu clock đủ căn cứ; SEM-44 nếu có kiểm độc lập | Chương Kết quả hiện dùng pilot, giữ main N/A cho tới khi có dữ liệu đủ điều kiện |

Bản review và CLAIMS có thể dùng cho SEM-51 và SEM-52 theo phạm vi pilot đã ghi. SEM-55 dùng PDF biên dịch lại sau khi bổ sung thông tin bìa, hình minh chứng và link video.
