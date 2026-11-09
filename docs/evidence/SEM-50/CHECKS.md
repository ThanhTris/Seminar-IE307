# WIP — SEM-50 chưa hoàn thành, chưa đủ điều kiện merge

Tuấn (`mtuan2491`), ngày 09/11/2026. Nhánh `codex/SEM-50-report-claims` tạo riêng từ main `54d48c2ed48588b59b16cc652a8d1b77912c15b7` sau khi push phần làm trước SEM-46.

**Đang chờ SEM-43 và SEM-45 bàn giao SUMMARY, CSV tập chính và CHECKS.** Nhóm trưởng review phần soạn trước, chờ hoàn tất bước 3 trước khi merge task.

## Ba bước thực hiện

| Bước | Đầu ra | Trạng thái |
|---|---|---|
| 1. Ghép nguồn và lập CLAIMS | references.bib, DOI/metadata/citation keys, ma trận claim và cách tiếp nhận SEM-22 | **Hoàn tất phần nguồn, `0f364ce`** |
| 2. Soạn báo cáo phần độc lập | Bối cảnh, hai nghiên cứu, cơ chế, phương pháp, khung kết quả/giới hạn và kiểm liên kết | **Hoàn tất phần dự thảo độc lập, commit bước 2** |
| 3. Chốt kết quả và báo cáo hoàn tất | Nhận SEM-43/45, nối CSV/SUMMARY/run/build/evidence, kiểm claims và kết luận cuối | **Chờ đầu vào, Not run** |

Mỗi bước thực hiện xong có một commit riêng. `git log --oneline -- docs/evidence/SEM-50/CHECKS.md` cho biết các commit đã ghi nhận.

## Tiếp nhận nguồn

| Nguồn | Artifact / kiểm chứng | Trạng thái sử dụng |
|---|---|---|
| SEM-19, Done | [MECHANISMS](../../MECHANISMS.md), [QUESTIONS](../../QUESTIONS.md), [CHECKS](../SEM-19/CHECKS.md) | Nhận cơ chế/câu hỏi và giới hạn evidence |
| SEM-20, Done | [PAPER_1](../../../research/notes/PAPER_1.md), [metadata](../../../research/metadata/paper-1.bib), [CHECKS](../SEM-20/CHECKS.md) | Dùng phương pháp, giới hạn, §6–7 và giả thuyết case |
| SEM-21, Done | [PAPER_2](../../../research/notes/PAPER_2.md), [metadata](../../../research/metadata/paper-2.bib), [CHECKS](../SEM-21/CHECKS.md) | Dùng cơ chế alarm/NTD, kết quả có điều kiện và hai điểm bất nhất đã ghi |
| SEM-22, Done | [API_CROSSCHECK](../../../research/notes/API_CROSSCHECK.md), [CHECKS](../SEM-22/CHECKS.md) | Nhận ma trận 8 claim, ghi cách thu hẹp từng luận điểm trong CLAIMS §3 |
| SEM-43, Todo ở base | [Yêu cầu SEM-43](../../../tasks/backlog/SEM-43.md) | SUMMARY và CHECKS còn chờ |
| SEM-45, Todo ở base | [Yêu cầu SEM-45](../../../tasks/backlog/SEM-45.md) | Parser đang ở nhánh task riêng, CSV tập chính và CHECKS hoàn tất còn chờ |

## Kiểm nguồn bước 1

- DOI hai paper được đọc lại qua Crossref ngày 09/11. Title, họ tác giả, năm, volume/issue và article number được đối chiếu với hai file metadata. Crossref dùng Jorg cho Paper 1, source note giữ Jörg theo bản PDF đã đọc ở SEM-20.
- Trang EUDL đọc được. Trang UJI/ScienceDirect trả 403 trong lần kiểm web, nội dung học thuật Paper 2 sử dụng notes/CHECKS toàn văn đã nhận từ SEM-21. Metadata Paper 2 được kiểm lại qua Crossref bằng CLI.
- Đã xem lại các mục periodic work, routing v1/callback, priority và Doze của documentation Android/Firebase ngày 09/11. Navigation hiện có AndroidConfigV2, báo cáo pin baseline theo scope của project.
- Bibliography tổng hợp giữ nguyên hai article record nguồn và bổ sung bốn record documentation, các key được ghi trong CLAIMS. Key Paper 2 được thống nhất về `GonzalezPerez2022AndroidScheduling`.

Nguồn trực tiếp gồm [EUDL](https://eudl.eu/doi/10.4108/eai.30-6-2017.152756), [Crossref paper 1](https://api.crossref.org/works/10.4108%2Feai.30-6-2017.152756), [Crossref paper 2](https://api.crossref.org/works/10.1016%2Fj.pmcj.2022.101550) và bốn URL documentation trong [references.bib](../../../research/references.bib).

Artifact bước 1 là [CLAIMS](../../CLAIMS.md) và bibliography. Review claim dùng cùng source và case đã có, các kết quả runtime của SEM-50 hiện **Not run**.

Citation.js core/BibTeX có sẵn ở `.local/sem20-tools` được dùng để parse 6 record, kiểm key duy nhất và đối chiếu đầy đủ hai article record với nguồn sau khi bỏ metadata nội bộ `_graph` của parser. DOI/title/họ tác giả/volume/năm khớp Crossref. Kiểm tĩnh 2 file Markdown đạt 41 link nội bộ và 5 bảng, whitespace hợp lệ. Có 16 claim và 7 quyết định tiếp nhận luận điểm nguồn trong CLAIMS.

## Kiểm và phạm vi bàn giao bước 2

| Check | Expected | Actual | Kết quả |
|---|---|---|---|
| Báo cáo / hai nghiên cứu | Hai bài có vai trò trong lập luận, nguồn truy được | REPORT §2 gắn hai paper với câu hỏi/case, §8 ánh xạ bibliography, CLAIMS giữ vị trí mục/trang | Đã review nội dung |
| Cơ chế / phương pháp | Khớp scope/API/schema/protocol | REPORT §3–4 dùng endpoint/version/correlation theo contract và giữ window/số lượt ở mức thiết kế | Đã review nội dung |
| Kết quả còn chờ | Có trạng thái và đầu vào cụ thể | REPORT §5 ghi PENDING_INPUT, các ô kết quả CHỜ, §6–7 chờ CSV/SUMMARY để chốt | **Chưa nghiệm thu toàn task** |
| Run/clock/OEM/race/HYBRID của nhóm | Có evidence runtime bàn giao | Đang chờ SEM-43/45 | **Not run trong SEM-50** |
| Link / citation / cấu trúc file | Đọc được nguồn và truy đúng bibliography | 4 file Markdown đạt 88 link nội bộ, 14 bảng, fence/whitespace hợp lệ, 6 citation key của REPORT có trong 6 record BibTeX, 16 claim duy nhất | Pass cho kiểm tĩnh |

Báo cáo phần làm trước là [REPORT.md](../../../report/REPORT.md). Phần draft cho SEM-51/52/55 review cấu trúc và interface nguồn. Những task nhận vẫn chờ bản SEM-50 hoàn tất theo gate hiện hành. Các bước tiếp theo gồm nhận CSV/SUMMARY/CHECKS, nối run/group/build/config/phase, xử lý mâu thuẫn, điền kết quả, cập nhật claim và chốt kết luận. Ghi chú WIP ở REPORT, CLAIMS, task và CHECKS giúp nhận biết bản làm trước trên GitHub.
