# SEM-48 — CHECKS và bàn giao phần kết quả

Vinh (`Vinh5905`), **16/11/2026, UTC+7**. Nhánh `codex/SEM-48-results-presentation` tiếp nối source SUMMARY `fce39b0df8086ede8d91d26171bf00436b83da31` ở PR [SEM-43 #31](https://github.com/ThanhTris/Seminar-IE307/pull/31), đã merge vào main `1475e67` ngày 16/11. Nhánh SEM-48 đã merge main mới, giữ nguồn `fce39b0` vì commit này vẫn là ancestor của main. Theo task, không có gate bắt đầu; đầu vào chưa nhận được ghi NOT_RUN/giới hạn.

## Đầu ra

- [VINH.md](../../../slides/inputs/VINH.md): nội dung slide 7, lời dẫn mục tiêu 105 giây (11:00–12:45), bản rút 75 giây, notes/Q&A và link run/build.
- [results/](../../../slides/inputs/results/README.md): hai biểu đồ PNG/SVG 16:9, hai CSV phục vụ hình, INPUTS/source hash, renderer và dependency ghim.
- [VERIFICATION.json](VERIFICATION.json): kiểm nguồn, phép đếm, ảnh/CSV tái sinh và checksum đầu ra. Đây là kiểm input trình bày, không phải audit độc lập SEM-44 hoặc rehearsal đo được.

Phần output không sửa SUMMARY, results.csv/parser SEM-45, audit SEM-44, app/server hay log nguồn. Không tạo deck cuối thay SEM-51. Không tự cập nhật trạng thái Project hoặc gán hoàn tất thực nghiệm từ ảnh.

## Nhận đầu vào

| Đầu vào | Expected | Actual | Kết quả |
|---|---|---|---|
| SEM-43 SUMMARY | Run/build, quan sát và giới hạn truy được nguồn | Đã nhận snapshot `fce39b0` của PR #31; 8 pilot hợp lệ mới, 12 INVALID cũ, main/OPPO chưa có | Pass — input đã merge, giữ revision đã ghim |
| CSV SEM-45 | CSV đúng bộ dữ liệu/phiên bản và có audit | PR #30 head `1a0c667` chỉ có 12 pilot cũ INVALID, chưa chứa 8 pilot mới; chưa merge | Chưa nhận CSV hiệu năng hiện hành |
| SEM-44 audit | Kiểm độc lập main/CSV theo source hiện hành | AUDIT/AUDIT_RESULTS lịch sử NOT_RUN, chưa kiểm bộ mới | NOT_RUN |
| Main emulator/OPPO | Các run main đúng candidate | 0 main; 27 emulator + 6 OPPO là slot kế hoạch | NOT_RUN |
| Device/build/config | Metadata hiển thị và nối được run | Emulator Android 17/API 37, app `9e7e55b`, server `c77772e`, APK hash trong VINH/manifest, FIREBASE_NOT_CONFIGURED, candidate gate false | Pass — giới hạn pilot |

**Không có CSV đã audit thì không thể bàn giao biểu đồ completion/latency main thật.** Phần đó giữ NOT_RUN. Bộ bàn giao hiện tại hoàn thiện nội dung có thể dùng: inventory outcome/validity, độ phủ thiếu dữ liệu, lời dẫn và quy trình cập nhật. Không trình bày chúng như thống kê main.

## Expected / actual

| Hạng mục | Expected | Actual | Trạng thái |
|---|---|---|---|
| Lời dẫn chính | Đúng khung 1 phút 45 giây, có giới hạn | Sáu đoạn 5+20+25+20+30+5=105 giây theo ngân sách, khoảng 286 đơn vị tách khoảng trắng; gồm chuyển vai | Pass — nội dung/kế hoạch; rehearsal NOT_RUN |
| Biến thể Q&A | Rút 30 giây theo PRESENTATION_PLAN | Năm đoạn 5+20+25+20+5=75 giây | Pass — nội dung/kế hoạch; rehearsal NOT_RUN |
| Inventory pilot | Giữ mọi outcome, số mẫu và validity | 20 attempt: 8 VALID/SUCCESS; 12 INVALID gồm 5 SUCCESS, 5 TIMEOUT, 2 ABORTED/FAILURE. Phân case/mode, giữ build/config/epoch/observer trong CSV | Pass — mô tả nguồn, không rate |
| Main coverage | Kế hoạch tách observed, không suy 0% | 27/6 slot dự kiến; observed main=0, n_complete/n_total=0/0; median/rate N/A và ô CSV rỗng | Pass — trạng thái NOT_RUN |
| Phép tính/diễn giải | Không gộp clock hay kết luận pin/OEM | Không tính latency/median; không xếp hạng hai cơ chế, không suy pin từ count; OPPO/FCM/E05 ghi giới hạn | Pass |
| Tái sinh | Ảnh/data có code và phiên bản | Matplotlib 3.10.7, Python 3.12; dependency exact trong requirements, source/hash trong INPUTS | Pass |
| Kiểm hình | Ảnh đọc được, tiếng Việt/legend/caption đủ, không tràn | Đã mở xem cả hai PNG, SVG giữ text, 1920×1080. Source và NOT_RUN/pilot nằm trên ảnh | Pass — visual QA |
| So byte | Hai lần render cùng môi trường | Hai CSV và bốn ảnh PNG/SVG giống từng byte | Pass |
| Nguồn và link | Trace source/run, không sửa đầu vào | Hash source và nội dung CSV đối chiếu manifest/audit; link/anchor/bảng, checksum ở VERIFICATION | Pass |
| Biểu đồ main từ CSV audited | Có n_complete/n_total, timeout và clock cho metric thật | Chưa có CSV/audit/main tương ứng | NOT_RUN |

Validation đã đối chiếu **71 file nguồn, 20 dòng pilot, 6 artifact tái sinh khớp byte, 62 link local/1 anchor và 8 bảng Markdown**. Đã xem hai PNG; không có phép đo runtime hoặc thống kê latency mới.

## Tái lập và kiểm

[README results](../../../slides/inputs/results/README.md#tái-sinh) có lệnh cài dependency/render trong venv riêng. Renderer chỉ làm input đồ họa, kiểm hash blob Git và nội dung worktree khớp sau chuẩn hóa chỉ CRLF→LF và dừng khi có input mới. Chỉ ghi file ở output; không chạy ADB/FCM/build hoặc sửa log.

```sh
python3.12 -m venv .local/sem48/venv
.local/sem48/venv/bin/python -m pip install -r slides/inputs/results/requirements.txt
.local/sem48/venv/bin/python -B slides/inputs/results/render_results.py --output .local/sem48/repro
git diff --check
```

Đối chiếu SHA-256 ở VERIFICATION cho files bàn giao; INPUTS ghim 71 file nguồn ở `fce39b0`. Lượt render thứ hai xuất riêng và so từng byte của 6 artifact. Không cần lặp Android/tool unit suite vì không sửa runtime; kiểm tập trung vào count/provenance, tái sinh ảnh, lời dẫn và visual QA. Không gọi các mốc 105/75 giây là kết quả diễn tập; SEM-54 cần đo thời lượng thật sau ghép deck.

## Bàn giao cho SEM-51

Đã chuẩn bị hình chính và notes dùng được ngay với nhãn pilot/giới hạn. Hình main chỉ cho biết phần chưa chạy; đặt phụ lục hoặc thay hình chính, không thêm thời gian/slide vào bài nói. CSV/renderer/SVG giúp dựng lại chart native trong deck, PNG dùng làm bản dự phòng.

Khi CSV/audit/main đúng revision được bàn giao, SEM-48 cập nhật plots/notes và n_complete/n_total, missing/timeout, build/device, clock. PR SEM-43 #31 đã merge; main `1475e67` đã nhận. Chưa có phép đo mới hoặc đầu vào hiệu năng main thì giữ NOT_RUN; không đổi nhãn pilot để lấp bảng.

## Sửa theo comment PR #32 ngày 17/11/2026

[Comment review](https://github.com/ThanhTris/Seminar-IE307/pull/32#issuecomment-6918001419) yêu cầu hỗ trợ checkout Windows/autocrlf và giữ LF khi ghi SVG. Đã tách kiểm hash chính xác của Git blob khỏi kiểm nội dung checkout; chỉ khác CRLF/LF được chấp nhận, không parse/rewrite JSON hoặc bỏ whitespace. `svg.write_text` ghi `newline="\n"` rõ ràng. Thêm 7 regression tests cho LF/CRLF, mixed line ending, sửa nội dung, khoảng trắng/EOF, BOM/lone-CR và đổi blob.

Đã xác nhận toàn bộ 71 source có byte không đổi giữa `fce39b0` và main merge `1475e67`; `fce39b0` là ancestor của main nên không cần đổi source revision hoặc hash gốc. Không phải trường hợp squash làm mất commit nguồn. Sáu artifact không đổi so với bản đã review.

[Workflow](../../../.github/workflows/sem48-reproduction.yml) bật autocrlf trước checkout và kiểm trên Windows thật; [checker](../../../slides/inputs/results/verify_reproduction.py) so SHA-256 cả 6 output với blob Git/golden, bắt CRLF ở output và lưu report. Kiểm macOS đã đạt 7/7 tests và 6/6 SHA. Kết quả Windows native được ghi theo CI, không gọi phép mô phỏng CRLF trên macOS là test Windows.

### Kết quả Windows native

[CI Windows thành công](https://github.com/ThanhTris/Seminar-IE307/actions/runs/44093928981) trên head code `bccca07`, Windows/Python 3.12.10, `core.autocrlf=true`. 7/7 regression tests đạt. 51/71 source có CRLF của checkout, nội dung/hash blob vẫn đúng; **cả 6 output khớp SHA-256 canonical**, SVG/CSV giữ LF. [WINDOWS_REPRODUCTION.json](WINDOWS_REPRODUCTION.json) là báo cáo tải nguyên byte từ artifact CI, gồm hash code đã chạy và từng file; đối chiếu hash code với nhánh hiện tại đạt. Đây là kiểm tái sinh, không phải phép đo main hoặc rehearsal.
