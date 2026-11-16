# SEM-48 — CHECKS và bàn giao phần kết quả

Vinh (`Vinh5905`), **16/11/2026, UTC+7**. Nhánh `codex/SEM-48-results-presentation` tiếp nối source SUMMARY `fce39b0df8086ede8d91d26171bf00436b83da31` ở PR [SEM-43 #31](https://github.com/ThanhTris/Seminar-IE307/pull/31), chưa merge khi nhận. Main base `007a1aa`. Theo task, không có gate bắt đầu; đầu vào chưa nhận được ghi NOT_RUN/giới hạn.

## Đầu ra

- [VINH.md](../../../slides/inputs/VINH.md): nội dung slide 7, lời dẫn mục tiêu 105 giây (11:00–12:45), bản rút 75 giây, notes/Q&A và link run/build.
- [results/](../../../slides/inputs/results/README.md): hai biểu đồ PNG/SVG 16:9, hai CSV phục vụ hình, INPUTS/source hash, renderer và dependency ghim.
- [VERIFICATION.json](VERIFICATION.json): kiểm nguồn, phép đếm, ảnh/CSV tái sinh và checksum đầu ra. Đây là kiểm input trình bày, không phải audit độc lập SEM-44 hoặc rehearsal đo được.

Phần output không sửa SUMMARY, results.csv/parser SEM-45, audit SEM-44, app/server hay log nguồn. Không tạo deck cuối thay SEM-51. Không tự cập nhật trạng thái Project hoặc gán hoàn tất thực nghiệm từ ảnh.

## Nhận đầu vào

| Đầu vào | Expected | Actual | Kết quả |
|---|---|---|---|
| SEM-43 SUMMARY | Run/build, quan sát và giới hạn truy được nguồn | Đã nhận snapshot `fce39b0` của PR #31; 8 pilot hợp lệ mới, 12 INVALID cũ, main/OPPO chưa có | Pass — input đang review, chưa merge |
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

Validation đã đối chiếu **71 file nguồn, 20 dòng pilot, 6 artifact tái sinh khớp byte, 55 link local/1 anchor và 8 bảng Markdown**. Đã xem hai PNG; không có phép đo runtime hoặc thống kê latency mới.

## Tái lập và kiểm

[README results](../../../slides/inputs/results/README.md#tái-sinh) có lệnh cài dependency/render trong venv riêng. Renderer chỉ làm input đồ họa, kiểm source/worktree khớp blob Git và dừng khi có input mới. Chỉ ghi file ở output; không chạy ADB/FCM/build hoặc sửa log.

```sh
python3.12 -m venv .local/sem48/venv
.local/sem48/venv/bin/python -m pip install -r slides/inputs/results/requirements.txt
.local/sem48/venv/bin/python -B slides/inputs/results/render_results.py --output .local/sem48/repro
git diff --check
```

Đối chiếu SHA-256 ở VERIFICATION cho files bàn giao; INPUTS ghim 71 file nguồn ở `fce39b0`. Lượt render thứ hai xuất riêng và so từng byte của 6 artifact. Không cần lặp Android/tool unit suite vì không sửa runtime; kiểm tập trung vào count/provenance, tái sinh ảnh, lời dẫn và visual QA. Không gọi các mốc 105/75 giây là kết quả diễn tập; SEM-54 cần đo thời lượng thật sau ghép deck.

## Bàn giao cho SEM-51

Đã chuẩn bị hình chính và notes dùng được ngay với nhãn pilot/giới hạn. Hình main chỉ cho biết phần chưa chạy; đặt phụ lục hoặc thay hình chính, không thêm thời gian/slide vào bài nói. CSV/renderer/SVG giúp dựng lại chart native trong deck, PNG dùng làm bản dự phòng.

Khi CSV/audit/main đúng revision được bàn giao, SEM-48 cập nhật plots/notes và n_complete/n_total, missing/timeout, build/device, clock. PR SEM-43 #31 cần được merge hoặc người nhận xác nhận revision đầu vào trước khi merge tiếp nhánh này. Chưa có phép đo mới hoặc đầu vào hiệu năng main thì giữ NOT_RUN; không đổi nhãn pilot để lấp bảng.
