# SEM-20 - Hồ sơ nghiệm thu và rà soát bàn giao

- Người thực hiện: Tuấn (`mtuan2491`), ngày **03/11/2026 (UTC+7)**.
- Nhánh: `codex/SEM-20-paper-1`, đúng mẫu `codex/SEM-XX-ten-ngan` của [project](../../../tasks/README.md).
- Base: `5e1c643550e35aee5f08cd74002be038ee3d4b9e`; đã fetch `origin/main`, chuyển về `main` và kiểm fast-forward trước khi tạo nhánh. Không tạo SEM-20 từ nhánh SEM-19.
- Phạm vi ban đầu ngày 03/11/2026: làm trước phần nghiên cứu độc lập và commit cục bộ; sau đó nhánh đã được push theo yêu cầu người dùng và merge qua PR #14.
- Trạng thái hiện tại, đối chiếu ngày **06/11/2026 (UTC+7)**: SEM-20 đã **Done** trên GitHub Project và đã merge vào main. Phần kiểm tra ban đầu bên dưới được giữ để truy vết; [báo cáo rà soát đầu ra và consumer](REVIEW-2026-11-06.md) ghi kết luận hiện tại. Task nghiên cứu không yêu cầu chạy lại thí nghiệm của paper hoặc chạy E01-E06 để nghiệm thu.

## Artifact bàn giao

| File | Nội dung |
|---|---|
| [PAPER_1.md](../../../research/notes/PAPER_1.md) | Metadata, lý do chọn, phương pháp, kết quả có vị trí trang, phản biện, bốn đề xuất liên hệ case và phần bổ sung sau |
| [paper-1.bib](../../../research/metadata/paper-1.bib) | Một record bản xuất bản, citation key `Simon2017DiffsyncEnergy` |
| CHECKS này | Phạm vi, nguồn, phiên bản đọc và kiểm tra có thể truy vết |

## Nguồn và cách kiểm

- [Nhà xuất bản EUDL](https://eudl.eu/doi/10.4108/eai.30-6-2017.152756): tên bài/tác giả, BibTeX, volume 3, issue 11, xuất bản 30/06/2017 và license CC BY 3.0.
- [Bản xuất bản PDF](https://eudl.eu/pdf/10.4108/eai.30-6-2017.152756): đọc 9 trang qua công cụ duyệt web, bao gồm phương pháp ở mục 5.4, push-based ở mục 6, workload/cơ chế/rút ra ở mục 7, kết luận và tài liệu tham khảo. Không suy nội dung paper chỉ từ abstract.
- [Crossref](https://api.crossref.org/works/10.4108%2Feai.30-6-2017.152756): tải record vào `.local/sem20/crossref.json`, đối chiếu DOI/tên/tác giả/ngày/tạp chí/volume/issue. Crossref ghi `page=152756`; không dùng giá trị đó làm pagination khi nhà xuất bản dùng article e2.
- [arXiv v1](https://arxiv.org/abs/1601.01539v1): bản preprint nộp 07/01/2016, không coi là bài thứ hai hoặc phiên bản xuất bản 2017. File local `.local/sem20/paper-1-preprint-v1.pdf`, 9 trang, SHA-256 `4f6e998bb8f4b062f18e8404db680bd50f10f6b3d80f2a9510edaf42392bd7e0`.

CLI tải EUDL trả 403; screenshot bản xuất bản trong công cụ web bị cache miss. Đã đọc text bản xuất bản qua link Download, và render/quan sát **preprint** trang 5 và 8 bằng Poppler để hỗ trợ đọc bố cục/các giá trị. Không mô tả các ảnh này là ảnh bản xuất bản. Không trích tọa độ đồ thị hoặc tuyên bố visual QA toàn bộ publisher PDF. Không commit PDF hoặc ảnh nguồn.

Phần riêng của Tuấn không sửa note paper-2, bibliography tổng hoặc file của owner khác. Việc tham chiếu case dùng [EXPERIMENT_PROTOCOL](../../EXPERIMENT_PROTOCOL.md); thiết kế là nguồn đặt giả thuyết, không phải output runtime phải chờ trước khi đọc bài.

## Kiểm tra và kết quả

| Check | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| Nhánh từ main | Không lẫn commit SEM-19 | Base trùng main/origin/main tại lúc tạo; SEM-19 đã push riêng theo yêu cầu | Pass - Git |
| Metadata / DOI | Nguồn nhà xuất bản và DOI record khớp | Tên, ba tác giả, tạp chí, năm 2017, volume 3/issue 11 khớp; giữ dấu Jörg theo PDF; arXiv 2016 tách rõ | Pass - đối chiếu nguồn |
| Đọc toàn văn | Có phương pháp, môi trường và kết quả ngoài abstract | Notes dẫn mục 4-8, trang 3-8; đã đọc references trang 8-9 và nhận diện nguồn có trước | Pass - đọc tài liệu |
| Số liệu và provenance | Không nhầm mẫu/đơn vị/kết quả với demo | Tách >60.000 runner cycles và 100.000 server-log cycles; 96,8% là tỷ lệ cycle rỗng của paper; ví dụ 7 phút là định lượng theo giả định; không đổi sang mAh/OPPO | Pass - review nội dung |
| Giới hạn và liên hệ | Có ít nhất một lập luận gắn quyết định/case | Bốn đề xuất P1-H1..H4, nổi bật race ở E05-C; ghi rõ suy luận của người đọc, không chứng minh bởi paper | Pass - review nội dung |
| BibTeX / link / định dạng | Record parse được, metadata khớp, link nội bộ tồn tại | Citation.js parse một record, dấu Jörg giữ đúng; DOI/title/authors/journal/year/volume/issue khớp Crossref; 8 link nội bộ hợp lệ, 6 bảng đúng số cột, UTF-8/newline/fence/whitespace đạt | Pass - kiểm tĩnh |
| Tái lập paper / app / pin / FCM | Chỉ nhận đã đo khi có run thực | Không chạy experiment, không sửa app/server/thiết bị, không sinh dữ liệu đo | **Not run - ngoài phần được giao** |

Kiểm cục bộ: `node .local/sem20/validate-docs.cjs` dùng Citation.js core/BibTeX parser cài dưới `.local/sem20-tools/` với lifecycle scripts tắt; metadata Crossref lưu local. Script xác nhận HEAD bằng main/origin/main tại base và không chứa hai file tổng hợp SEM-19. `git diff --check` được bổ sung bằng kiểm whitespace riêng cho file mới; trước commit kiểm tiếp `git diff --cached --check` và đúng ba file của task. Công cụ, PDF preprint/ảnh và JSON kiểm tra nằm trong `.local/`, bị Git bỏ qua; không đổi package hoặc dependency của app/server.

## Phần bổ sung sau và người nhận

- **SEM-22:** nhận note + BibTeX để đối chiếu lập luận với API/bối cảnh Android; bài nghiên cứu này không thay documentation hiện hành.
- **SEM-50:** nhận metadata riêng và các giả thuyết đã gắn case; chỉ ghép bibliography/CLAIMS/report trong task tổng hợp, không coi số liệu paper là dữ liệu nhóm.
- **Khi chốt SEM-20:** đối chiếu thiết bị/scope và revision demo thực sự được bàn giao; ghi thay đổi hoặc giới hạn mới nếu có. SEM-11/12 đã có artifact trên main, không báo lại là dependency chưa Done và không bắt buộc chờ E01-E06 để hoàn thành task đọc bài.

- [PR #14](https://github.com/ThanhTris/Seminar-IE307/pull/14) đã được `ThanhTris` merge vào `main` ngày 05/11/2026 tại merge commit `9931af1e8b1bb326c035dc5855022dd20ae9ddc7`, xác minh bằng Git và GitHub PR API ngày 06/11/2026. Đây là thông tin merge; không suy ra một GitHub review approval riêng khi danh sách PR reviews rỗng.
- Trạng thái task SEM-20 trên GitHub Project 3 đã được cập nhật sang **Done** (item `PVTI_lAHOCnL5Fs4BpUDUzhEiXAk`).
