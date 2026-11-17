# Ảnh và dữ liệu trình bày SEM-48

Bộ input cho [lời dẫn Vinh](../VINH.md), source SUMMARY ở `fce39b0df8086ede8d91d26171bf00436b83da31` ([PR SEM-43 #31](https://github.com/ThanhTris/Seminar-IE307/pull/31), đã merge vào main `1475e67`). Commit nguồn `fce39b0` vẫn nằm trong lịch sử main, nên giữ nguyên revision/hash và sáu artifact gốc. [INPUTS.json](INPUTS.json) ghim 71 file nguồn bằng SHA-256; ảnh chỉ mô tả evidence tại revision này.

## File dùng trong deck

| File | Mục đích / đơn vị | Nên dùng |
|---|---|---|
| [pilot_inventory.png](pilot_inventory.png), [SVG](pilot_inventory.svg) | Inventory 20 lần thử pilot theo outcome gốc/validity, đơn vị run; 8 VALID/SUCCESS mới và 12 INVALID cũ | Hình chính slide 7, 16:9; giữ tiêu đề, chú giải và caption |
| [main_coverage.png](main_coverage.png), [SVG](main_coverage.svg) | Số **slot kế hoạch** theo thiết bị, main 0 run, n_complete/n_total=0/0, median/rate N/A | Phụ lục hoặc thay hình chính; không thêm một lượt nói ngoài 105 giây |
| [pilot_inventory.csv](pilot_inventory.csv) | Một dòng cho mỗi attempt; build/config/epoch/observer và đường dẫn manifest/events/audit | Data để dựng lại chart native/tra nguồn; không phải results.csv SEM-45 |
| [main_coverage.csv](main_coverage.csv) | Hai dòng thiết bị, planned/observed riêng; rate/median rỗng | Dựng lại hình độ phủ, không tính 0/33 là tỷ lệ thất bại |

PNG có kích thước **1920×1080**, SVG giữ text và vector; DejaVu Sans được Matplotlib dùng để hỗ trợ tiếng Việt. Nếu dựng chart native trong SEM-51, dùng CSV và quy tắc nhóm/chú giải dưới đây. SVG không phải đối tượng chart PowerPoint native; SEM-51 có thể tạo chart native từ cùng dữ liệu. Không đổi build/nhãn pilot thành main khi đưa ảnh vào deck.

### Nội dung tương đương ảnh

- E01 PERIODIC: 1 VALID/SUCCESS mới, 2 INVALID/TIMEOUT, 1 INVALID/ABORTED; n_input=4.
- E03 PERIODIC: 2 VALID/SUCCESS mới, 3 INVALID/SUCCESS, 1 INVALID/ABORTED; n_input=6.
- E04 PERIODIC: 3 VALID/SUCCESS mới, 2 INVALID/SUCCESS, 1 INVALID/TIMEOUT; n_input=6.
- E06 HYBRID: 2 VALID/SUCCESS mới, 2 INVALID/TIMEOUT; n_input=4.
- Main: emulator 27 slot kế hoạch, OPPO 6; chưa nhận run main cho cả hai. Không có completion rate/latency đo được.

Màu xanh đặc = VALID/SUCCESS mới; các phần có gạch = INVALID cũ, tách SUCCESS, TIMEOUT, ABORTED. Không dựa vào màu một mình: giữ label/legend. Các nhóm collector/epoch khác nhau chỉ nằm chung **inventory trạng thái**, không gộp thành sample hiệu năng. Event/clock/outcome gốc không bị sửa hoặc tính lại latency ở SEM-48.

## Tái sinh

Từ root repo, dùng Python **3.12** và môi trường riêng. `requirements.txt` ghim đúng dependency đã dùng; không cần Android SDK, máy ảo hay Firebase:

```sh
python3.12 -m venv .local/sem48/venv
.local/sem48/venv/bin/python -m pip install -r slides/inputs/results/requirements.txt
.local/sem48/venv/bin/python -B slides/inputs/results/render_results.py
```

Windows dùng đường dẫn Python trong `Scripts` của venv. `core.autocrlf=true` được hỗ trợ: renderer kiểm SHA-256 chính xác của blob Git đã ghim, rồi chỉ chuẩn hóa CRLF→LF khi so nội dung checkout. Sửa outcome/version, thêm khoảng trắng, BOM, đổi newline cuối file hoặc sửa blob đều vẫn bị chặn. SVG/CSV xuất ra luôn LF; không tắt guard hoặc sửa hash để bỏ qua nội dung thay đổi.

Xuất vào thư mục riêng để đối chiếu mà không ghi lại ảnh bàn giao:

```sh
.local/sem48/venv/bin/python -B slides/inputs/results/render_results.py --output .local/sem48/repro
```

Renderer chỉ đọc source đã ghim (cho phép khác CRLF/LF của checkout); kiểm manifest/audit/phase/outcome, ghi hai CSV và bốn file ảnh. Nó từ chối nguồn/hash thay đổi, outcome mới hoặc khi xuất hiện main data: cần nhận CSV/audit và cập nhật nội dung thay vì tự vẽ biểu đồ hiệu năng. SVG bỏ timestamp và dùng hash salt cố định. Hai lần render trong môi trường đã ghim khớp byte; font/Freetype khác giữa OS có thể thay byte ảnh, khi đó đối chiếu CSV, dependency/font và xem lại hình.

## Kiểm Windows với core.autocrlf=true

Dùng checkout mới để Git thực sự chuyển line ending, không chỉ đổi config trên checkout đã có. Trong PowerShell:

```powershell
git clone --config core.autocrlf=true https://github.com/ThanhTris/Seminar-IE307.git Seminar-IE307-sem48-crlf
cd Seminar-IE307-sem48-crlf
git switch codex/SEM-48-results-presentation
py -3.12 -m venv .local/sem48/venv
./.local/sem48/venv/Scripts/python.exe -m pip install -r slides/inputs/results/requirements.txt
./.local/sem48/venv/Scripts/python.exe -B -m unittest discover -s slides/inputs/results/tests -v
./.local/sem48/venv/Scripts/python.exe -B slides/inputs/results/verify_reproduction.py --require-crlf --output .local/sem48/windows-repro
```

Chọn thư mục output trống cho mỗi lần kiểm. [verify_reproduction.py](verify_reproduction.py) ghi `reproduction-report.json`: OS/Python, config Git, số source đã được chuẩn hóa, SHA-256 của đủ 6 artifact và hash code đã chạy. Golden lấy từ blob Git `HEAD` và VERIFICATION, không so với SVG/CSV checkout có thể đã đổi CRLF. Output không được chuẩn hóa trước khi hash; bất kỳ khác byte thật nào cũng làm kiểm thất bại.

[Workflow Windows](../../../.github/workflows/sem48-reproduction.yml) chạy cùng lệnh trên runner Windows thật, bật autocrlf trước checkout, chạy 7 regression tests và lưu báo cáo. [Tests](tests/test_source_validation.py) giữ kiểm phân biệt line ending với thay đổi nội dung; đây là kiểm công cụ, không phải sample thực nghiệm. [Báo cáo Windows native](../../../docs/evidence/SEM-48/WINDOWS_REPRODUCTION.json) ghi 51/71 file checkout đổi CRLF, 7 tests đạt và đủ 6 SHA-256 khớp; [CI](https://github.com/ThanhTris/Seminar-IE307/actions/runs/44093928981) đã chạy thành công.

## Giới hạn bàn giao

**Biểu đồ hiệu năng main từ CSV đã audit: NOT_RUN.** [AUDIT SEM-44](../../../experiments/AUDIT.md) chưa ký bộ nguồn mới. Draft [SEM-45 #30](https://github.com/ThanhTris/Seminar-IE307/pull/30), head `1a0c667`, có 12 pilot cũ INVALID, không có 8 pilot mới. Renderer không lấy bộ đó làm kết quả main và không tạo bản thay thế parser/CSV của Tuấn.

Không vẽ latency/median, pin, so sánh periodic–push hoặc OPPO–emulator khi chưa có mẫu hợp lệ/clock. Khi có dữ liệu mới, cập nhật INPUTS/source revision, biểu đồ, captions và lời nói; giữ n_complete/n_total, timeout/missing và giới hạn build/device. [CHECKS](../../../docs/evidence/SEM-48/CHECKS.md) ghi phép kiểm và phần chưa chạy.
