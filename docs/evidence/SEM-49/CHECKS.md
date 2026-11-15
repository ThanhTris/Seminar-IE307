# SEM-49 — CHECKS nội dung kiến trúc và Paper 2

- Owner duy nhất: Tâm (`HoaiTam`); kiểm ngày 09/11/2026 (UTC+7).
- Base source: `db5fab65920628eaa1cfa44ce229c7019b1b6905`; nhánh `codex/SEM-49-architecture-paper-2`.
- Task tài liệu: không sửa code, build/cài APK, gửi FCM hoặc chạy lại E01–E06. Build/config đo mới: **Not run / không áp dụng**. Các manifest/build/run dẫn trong nội dung thuộc evidence đã bàn giao, không phải run do SEM-49 tạo.
- Đã xác nhận SEM-18/21/27/35/40 Done trực tiếp trên Project khi bắt đầu; artifacts và CHECKS có trên base. Nhận source server/sender/skip-push, shared sync/adapter/UI, Paper 2/BibTeX và protocol/presentation plan.

## Expected / actual

| Kiểm tra | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| Đầu ra | File riêng cho SEM-51, có nguồn và lời nói | [TAM.md](../../../slides/inputs/TAM.md): slide 5 trong 60 giây, đoạn Paper 2 cho Tuấn ghép slide 8, notes/giới hạn và source links | Pass — kiểm nội dung |
| Kiến trúc | Đúng contract và code tại base | Đối chiếu server/store v2, sender, skip module; callback/adapter shared enqueuer, worker/repository version guard và UI Flow | Pass — rà soát source, runtime mới Not run |
| Phân biệt event | Accepted khác delivered/applied; skip không phải mất tin | Tách mốc trong lời nói và notes; E06 giữ điều kiện kết luận theo source/run/version | Pass |
| Nguồn Paper 2 | Tên/DOI/điều kiện và chỉ số đúng SEM-21 | Khớp PAPER_2.md và BibTeX key; số 84%, 0,39–1,24%, 39 ms có trang/bảng và giới hạn, không gán sang demo | Pass — đối chiếu artifact nghiên cứu đã nghiệm thu |
| Đối chiếu dữ liệu | Không biến pilot thành main hoặc retry thành cycle mới | Đọc hai manifest/log/analysis SEM-29; r2 6 start = 5 cycle mới + 1 recovery; 1 applied thuộc setup, clock uncontrolled/legacy format được giữ | Pass — kiểm artifact |
| Tái kiểm pilot | Analysis đã lưu khớp raw/manifest/hash | Import `docs/evidence/SEM-29/validate_pilot.py`, gọi `audit(run_dir)` cho cả hai run và so object với analysis.json: cả hai khớp; không ghi lại evidence | Pass |
| Kết quả main/E06/OPPO | Chỉ dùng sau bàn giao run/build/audit thật | Base có hai pilot; chưa có bộ main E03/E06/OPPO để dùng, không bổ sung số liệu giả | Not run / chưa có input đo tương ứng |
| Diễn tập thời lượng | Có đo thực nếu công bố đã đạt | Ghi 50–55 giây và 25–30 giây là dự kiến để SEM-54 kiểm; chưa diễn tập ở SEM-49 | Not run |
| Liên kết và định dạng | Đường dẫn nội bộ tồn tại, không lỗi diff | Kiểm toàn bộ link tương đối của hai file, code fence cân bằng, citation key khớp BibTeX; `git diff --cached --check` không báo lỗi | Pass |

Thao tác kiểm dữ liệu dùng Python đọc artifact có sẵn và validator của owner SEM-29. Đây là kiểm tính nhất quán provenance, không nâng trạng thái validity/canonical của pilot và không thay kiểm audit độc lập SEM-44.

## Bàn giao và giới hạn

- Bàn giao nội dung slide/notes và bảng liên hệ Paper 2 với pilot/phương pháp cho SEM-51. Đã có đủ đầu vào task để đề nghị Review; chưa có tập main không chặn phần phương pháp nhưng chặn mọi kết luận định lượng main/E06.
- Tài liệu kỹ thuật cũ như SYNC_CORE_API có nhận xét lịch sử “server v1”; SEM-49 đối chiếu source v2 trên base thay vì lặp lại trạng thái cũ. Không sửa tài liệu do task khác sở hữu.
- Giữ cả run pilot aborted, không công bố success rate chung, không đo latency xuyên thiết bị khi clock offset chưa được kiểm soát. Khi nhận run mới, người ghép slide phải kiểm đúng commit/config/audit trước khi dùng.
- Trưởng nhóm review và merge; không tự chuyển Done. Sau bàn giao chỉ sửa theo comment yêu cầu.
