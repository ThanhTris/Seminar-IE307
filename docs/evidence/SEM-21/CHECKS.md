# SEM-21 — CHECKS và bàn giao bài nghiên cứu thứ hai

- Người thực hiện: Tâm (`HoaiTam`); ngày đối chiếu 04/11/2026 (UTC+7).
- Base source: `5e1c643550e35aee5f08cd74002be038ee3d4b9e` (`origin/main`); nhánh `codex/SEM-21-paper-2`.
- Đây là task đọc nguồn; không build/cài app, không chạy sender, FCM hay thí nghiệm E01–E06. Build/APK/config runtime: **Not run / không áp dụng**.
- Đầu vào hoàn tất: SEM-11 và SEM-12 đã Done trên Project; đã đối chiếu `docs/SCOPE.md`, cấu hình build và hồ sơ/CHECKS thiết bị trên base. SEM-12 ghi chưa có OPPO, FCM thật chưa kiểm; không suy thành kết quả mới.
- SEM-20 chưa được xác nhận bàn giao/Done; đối chiếu tham khảo nhánh `bb12ee63ebfca2136c6f3a4602ecfb7d25c6a56d`, không coi lựa chọn bài 1 là kết luận cuối.

## Kết quả kiểm

| Kiểm tra | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| DOI và metadata | Tên, tác giả, kỳ, mã bài khớp nguồn | Đối chiếu [Crossref](https://api.crossref.org/works/10.1016%2Fj.pmcj.2022.101550) với trang đầu PDF; DOI `10.1016/j.pmcj.2022.101550`, tập 81, mã 101550, kỳ 04/2022 | Pass |
| Toàn văn hợp lệ | Truy cập được nguồn gốc, ghi quyền | [PDF nhà xuất bản tại kho UJI](https://repositori.uji.es/bitstreams/369ca302-bfdc-4c69-901d-30b374277ba9/download), HTTP 200, 19 trang, trang đầu ghi CC BY 4.0; SHA-256 `1d61a221da43b222360355c7944798d50856c9435dac71a45a0575da63d8d1f5` | Pass |
| Nội dung và số liệu | Đọc phương pháp, kết quả, giới hạn; trỏ trang | Đọc PDF và đối chiếu trực quan bảng 1–4, hình 4; ghi điều kiện, ngoại lệ và hai điểm bất nhất trong [PAPER_2.md](../../../research/notes/PAPER_2.md) | Pass |
| Phạm vi và case | Phân biệt bài báo với demo, đề xuất case khả thi | Đối chiếu SCOPE, SEM-12 và protocol E01/E03/E04; không thay thiết kế hoặc khẳng định đã đo | Pass |
| Chạy lại nghiên cứu gốc | Chỉ báo kết quả nếu có run thật | Gói Zenodo chỉ được dẫn nguồn; không chạy lại | Not run |
| E01–E06, OPPO và FCM | Phải có log/run thật để kết luận | Không chạy trong SEM-21; chưa có OPPO theo SEM-12 | Not run |

## Bàn giao và blocker

- [Ghi chú toàn văn](../../../research/notes/PAPER_2.md), [metadata BibTeX](../../../research/metadata/paper-2.bib) và CHECKS này là đầu ra cho SEM-22, SEM-49, SEM-50. PDF không commit; link kho trường và DOI đủ truy cập nguồn.
- Không có blocker hoàn tất SEM-21 đối với đầu vào SEM-11/12. Chưa có OPPO là giới hạn của các phép đo tiếp theo, không phải dữ liệu bị thiếu của bài báo.
- Trưởng nhóm kiểm nhận PR; không tự merge hoặc chuyển Done. Sau bàn giao Review, chỉ sửa nội dung theo comment yêu cầu của trưởng nhóm.
