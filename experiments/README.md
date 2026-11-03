# Công cụ thực nghiệm — SEM-24

Python **3.9+**, đã kiểm bằng Python **3.9.6** trên máy Vinh; chỉ dùng standard library, chạy từ root repo. [PROTOCOL 1.0.0](PROTOCOL.md), [lịch dự trù](RUN_SCHEDULE.md), [API](../docs/API.md), [event schema 2.0.0](../docs/EVENT_SCHEMA.md) và [CHECKS SEM-24](../docs/evidence/SEM-24/CHECKS.md) là đầu vào đối chiếu. Công cụ này xuất dữ liệu; không chạy thí nghiệm, gửi FCM hoặc phân tích kết quả thay SEM-45/44.

## 1. Template và nhãn dữ liệu

Sao chép [RUN_MANIFEST_TEMPLATE.json](RUN_MANIFEST_TEMPLATE.json) vào `experiments/private/` rồi điền dữ liệu của run. Template có `data_kind=TEMPLATE`, outcome/status `NOT_RUN` và trường chưa biết là `null`; exporter **từ chối export nguyên template**. Không lấy commit tài liệu hiện tại làm commit app/server đã đo.

| Nhóm | Cách điền |
|---|---|
| Nhận dạng | `manifest_version=1.0.0`, `protocol_version`, `event_schema_version=2.0.0`, case/subscenario/repetition, `run_id`, `device_alias`, operator alias, mode |
| Dữ liệu thật | `data_kind=OBSERVED`; `run_phase=development/pilot/main`; execution/outcome/validity do người chạy ghi dựa trên evidence, không do exporter đoán |
| Fixture | `data_kind=FIXTURE`, phase **development**, bắt buộc CLI `--fixture`; mọi ID/UTC/hash trong fixture đi kèm chỉ là dữ liệu tổng hợp để kiểm công cụ |
| Build | Full app/server commit SHA 40 hex, APK SHA-256 64 hex, package/version, min/target/compile SDK và trạng thái candidate gate từ SEM-37. Để null nếu chưa biết; không bịa hash |
| Thiết bị | OS/API/ColorOS/build/ABI/page size/Google Play services đọc thật tại setup. `build_fingerprint` là fingerprint bản build đã kiểm không chứa định danh, không phải serial/boot ID |
| Config | Pin/nguồn/Battery Saver/optimization, transport, màn hình/idle/stopped, scheduler/flex/policy/constraint, TTL/collapse, timeout/backoff/attempt limit thực tế. Giá trị dự kiến trong PROTOCOL không tự biến thành giá trị đã đo |
| Quan sát | Start/end UTC `...Z`, planned window, actual duration, elapsed realtime và boot alias, version trước/target/cuối, cycle và milestones theo từng ca. Giữ cả applied muộn; không đổi outcome timeout vì phát hiện event sau window |
| Clock | `controlled=false` khi chưa kiểm soát. Ghi client clock **HOST hoặc ANDROID**, method code, offset signed integer ms, uncertainty ms và ≥3 mẫu trước/sau khi đánh dấu controlled. Mỗi sample có `client_send_utc`, `server_utc`, `client_receive_utc`, `resolution_ms`; không ghép mẫu host thành phép đo offset Android |
| Cleanup | Status `NOT_RUN/PASS/FAIL`, các trường work/idle/network/stopped thật; `reason_codes` dùng mã an toàn, không exception text |
| Evidence | `evidence_files` chỉ là tên file đã làm sạch, không chứa path/serial. Exporter không tự sao chép các file này; người chạy bổ sung evidence tương ứng vào thư mục run sau export trước bàn giao |

Ví dụ hình dạng **một clock sample giả để mô tả cấu trúc**, không phải số đo:

```json
{"client_send_utc":"2026-11-03T00:00:00Z","server_utc":"2026-11-03T00:00:00.005Z","client_receive_utc":"2026-11-03T00:00:00.010Z","resolution_ms":1}
```

Template lưu `server_route` dưới dạng nhãn như `EMULATOR_HOST`, `ADB_REVERSE`, `LAN`; URL/IP cụ thể và mapping alias → serial giữ private. Điều này tránh công bố địa chỉ cá nhân. Không sửa timestamp/version/outcome/event ID khi loại định danh. Nếu cần báo endpoint thật cho người chạy, bàn giao cấu hình local ngoài repo public.

Main được ghi `validity=VALID` phải có app/server commit, APK checksum, candidate gate true, OS/model/API và các trường window. Validator chỉ kiểm cấu trúc/metadata đã khai, **không xác nhận candidate thực sự được duyệt, window từng ca đúng hoặc phép tính latency đúng**. SEM-44 kiểm độc lập; SEM-45 phân tích. Run không đủ evidence vẫn được lưu dưới INVALID/NOT_ASSESSED với lý do, không bị xóa để làm đẹp kết quả. Không có OPPO: lưu NOT_RUN + `DEVICE_UNAVAILABLE`, không lấy emulator làm mẫu thay.

## 2. Kiểm bằng fixture có nhãn

[fixtures/sem24](fixtures/sem24/) chứa manifest và log **tổng hợp**; mỗi event có extension `fixture=true`. Có trường token/serial **giả** để kiểm loại trường nhạy cảm; không có credential thật. [Bản export mẫu](fixture_exports/run-sem24-fixture/) là fixture, không nằm trong `runs/`, không được dùng làm pilot/main hay số liệu trình bày.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s experiments/scripts/tests -v

# Tái lập độc lập, không ghi đè bản export mẫu đã commit.
python3 experiments/scripts/export_logs.py \
  --manifest experiments/fixtures/sem24/manifest.json \
  --android-log experiments/fixtures/sem24/android.jsonl \
  --server-log experiments/fixtures/sem24/server.jsonl \
  --device-alias fixture-device --run-id run-sem24-fixture \
  --fixture --output-base .local/sem24-reproduce
```

Kết quả dự kiến: **8 event**, 1 dòng run khác bị loại, 1 event replay giống hệt được deduplicate; token/serial giả và extension ngoài schema không có trong output. Thứ tự giữ theo input (Android trước server trong CLI này), **không phải thứ tự nhân quả**. Script không sort hai clock hoặc suy thời điểm nhận từ accepted. Các assertions của test đối chiếu chính xác trường đo/correlation đầu vào và đầu ra.

Output gồm `manifest.json`, `events.jsonl`, `export_report.json`. Report lưu SHA-256 byte UTF-8 đầu vào, số dòng được chọn/bỏ/trùng và số trường event ngoài schema bị bỏ; không có path nguồn, serial hoặc nội dung lỗi gốc. Tất cả parse/validation/privacy check hoàn tất trước khi tạo output. Thư mục output đã có → từ chối ghi đè; để tái lập lần nữa, chọn `--output-base .local/sem24-reproduce-2` (không xóa run/evidence cũ).

## 3. Export file của run thật theo alias/run_id

Nguồn phải là JSONL UTF-8 schema **2.0.0**, đủ mọi key kể cả null, một object/dòng, không dòng trống. Không đưa raw logcat, SQLite/Room v1 hoặc stdout CLI sender hiện tại vào đây. Công cụ hỗ trợ đúng version đã kiểm; future version/type/outcome phải được cập nhật/kiểm trước, không tự đổi schema hoặc bỏ mất event chưa nhận diện.

Chuẩn bị riêng `experiments/private/<run_id>/manifest.json`, `android.jsonl`, `server.jsonl` và `experiments/private/deny-values.json`. File deny là JSON array chứa **serial thật và tất cả token/credential/định danh nhạy cảm có thể xuất hiện**, mỗi giá trị ≥4 ký tự. File này bắt buộc với OBSERVED, chỉ đọc local, không export. Đừng truyền token làm CLI argument hoặc paste raw logs vào repo.

```sh
# Thay mã run/alias bằng đúng manifest đã ghi từ ca thực tế.
python3 experiments/scripts/export_logs.py \
  --manifest experiments/private/run-e02-emu-001/manifest.json \
  --android-log experiments/private/run-e02-emu-001/android.jsonl \
  --server-log experiments/private/run-e02-emu-001/server.jsonl \
  --deny-values experiments/private/deny-values.json \
  --device-alias emulator-main --run-id run-e02-emu-001
```

OBSERVED mặc định ra `experiments/runs/<run_id>/`; FIXTURE ra `experiments/fixture_exports/<run_id>/`. `--output-base` chỉ đổi thư mục cha, vẫn giữ hai nhánh tách biệt. Một run chưa chạy có thể export manifest NOT_RUN không cần log (events rỗng); run đã chạy phải có ít nhất một nguồn log. Nếu thiếu nguồn server/client, report ghi đúng nguồn đã nhận; không suy các event không có thành success/timeout hoặc tự điền null cho event thiếu field.

Lọc **cả run_id và device_alias**, kiểm mode/origin; deduplicate theo event ID khi canonical fields giống hệt. Cùng ID khác timestamp/version/outcome/correlation → dừng, giữ nguyên nguồn private để điều tra. Không gộp event theo message ID, version hoặc timestamp. Event ngoài window được giữ, người phân tích dựa manifest để phân biệt late/timeout; exporter không biến NOT_RUN thành thực nghiệm.

Privacy: chỉ export trường manifest/template và 27 trường event của schema; bỏ các trường ngoài allowlist, kể cả token/serial lồng trong block metadata ngoài template. Giá trị nhạy cảm nằm trong **trường được giữ** → từ chối thay vì redact/sửa giá trị đo. Có thêm scan signature token/key/JWT/private IP; deny list phải chứa định danh local thực tế vì không có regex nào nhận diện mọi serial/secret hay thông tin cá nhân trong một chuỗi opaque. Trước commit vẫn rà output và các evidence phụ; đừng cam kết an toàn raw log chỉ từ tên field.

## 4. Thu từ Android bằng ADB — hợp đồng với producer

Tùy chọn `--adb` dùng `exec-out run-as <package> cat files/experiment-events.jsonl`; đây là **giao diện thu thập yêu cầu module Android cung cấp**, không phải xác nhận source hiện đã tạo file đó. SEM-25/32 cần ghi/flush canonical JSONL v2 vào file này từ event thật; SEM-27/35 cung cấp SERVER JSONL v2 từ ledger/outbox/send thật. Nếu producer chọn giao diện khác, xuất file JSONL private bằng giao diện được bàn giao rồi dùng mục 3. Không chuyển Room v1 thành v2 bằng cách bịa device/mode/signal/correlation.

Với debug APK hỗ trợ `run-as`, lập `experiments/private/devices.json` dạng `{"emulator-main":"<SERIAL_LOCAL>"}` và **thay placeholder bằng serial local đúng máy**, không commit file này. Serial chỉ nằm trong file map/deny local và argv tiến trình ADB; không ghi vào output public hoặc stderr công cụ. Mọi serial trong map đều được thêm vào deny values.

```sh
python3 experiments/scripts/export_logs.py \
  --manifest experiments/private/run-e02-emu-001/manifest.json \
  --adb "$HOME/Library/Android/sdk/platform-tools/adb" \
  --device-map experiments/private/devices.json \
  --server-log experiments/private/run-e02-emu-001/server.jsonl \
  --deny-values experiments/private/deny-values.json \
  --device-alias emulator-main --run-id run-e02-emu-001
```

ADB capture thô được giữ trong `experiments/private/captures/<alias>/<run_id>/capture-*/android.raw.jsonl` (capture dir 0700, file 0600); mỗi capture mới có thư mục riêng. Khi parse/privacy check lỗi, bản thô vẫn ở private và không tạo public run. Thiếu app/file/quyền run-as hoặc ADB lỗi → `ADB_CAPTURE_FAILED`, **không fallback raw logcat**, không in stdout/stderr ADB vốn có thể chứa token/serial. `--adb` và `--android-log` loại trừ nhau; không tự `adb connect` hoặc bật root/debugging.

Hiện app trên emulator chưa được SEM-24 build/cài/kiểm producer; phần ADB được test bằng subprocess giả, **Not run trên thiết bị thật**. Không dùng kết quả fixture làm bằng chứng app/server đã phát log v2.

## 5. Reset, cleanup và bàn giao

Exporter chỉ đọc log, không clear logcat/cache, force-stop, cancel work, thay idle/mạng hoặc gửi push. Người chạy làm theo [PROTOCOL mục 3](PROTOCOL.md#3-cấu-hình-cố-định-và-reset-giữa-run), [Doze](PROTOCOL.md#6-quy-trình-doze-và-hoàn-tác) và [force-stop](PROTOCOL.md#7-ca-mô-tả-lifecycle-bổ-sung-và-force-stop):

1. Export/đóng run cũ trước khi xóa bất kỳ dữ liệu nào; hủy trigger qua module app đã bàn giao, đợi cancel/drain xác nhận hoàn tất. Chưa có giao diện cancel/drain thì ghi blocker, không giả định `am force-stop` thay thế tương đương.
2. Tạo run mới, cô lập pending push cũ, giữ version server tăng đơn điệu; MANUAL chuẩn bị cache chỉ ngoài window rồi drain. Ghi app/server/APK/config thực tế, không đổi code giữa run.
3. Sau ca Doze, kể cả lỗi/ngắt: `deviceidle unforce` và `battery reset`, xác nhận idle/nguồn rồi khôi phục màn hình. Sau mất mạng, khôi phục từng transport và xác minh kết nối. Sau force-stop, **người dùng mở lại**, ghi mốc/stopped=false; chỉ quan sát tiếp sau mở lại.
4. Ghi `cleanup.status` và từng trạng thái xác minh; giữ thiết bị bị khóa nếu cleanup Fail. Chỉ gỡ reverse/rule do run tạo, không xóa mapping hoặc dữ liệu của tác vụ khác.
5. Hoàn tất manifest từ evidence thật, export, kiểm report/số event/dữ liệu nhạy cảm và thêm evidence phụ đã làm sạch. Không sửa timestamp/version/outcome để vượt validator; lỗi source trả về đúng task sở hữu. Bản gốc giữ `experiments/private/` (đã gitignore), không upload.

Clock phải được thu trước/sau run bởi công cụ/đồng hồ được kiểm nhận và ghi trong manifest; exporter không tự lấy mẫu hay xác nhận offset. Source server hiện có `server_time_utc` trong health, nhưng [API v2](../docs/API.md#get-health) không bảo đảm field đó: chỉ dùng sau khi xác nhận đúng implementation/độ phân giải và client clock, không coi GET health/ADB reverse là clock calibration.

Task nhận: SEM-28 (M1/export), SEM-29/34 (pilot), SEM-41/42 (main), SEM-45 (parser). Ghi version exporter/manifest/schema/protocol và commit artifact khi bàn giao; exporter không tự cập nhật Project hoặc chuyển Done. Thiếu OPPO vẫn giữ blocker; kiểm fixture cho công cụ SEM-24 không phụ thuộc có OPPO.
