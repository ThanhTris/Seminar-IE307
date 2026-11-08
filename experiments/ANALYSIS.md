# Phân tích manifest/JSONL — SEM-45

Phiên bản công cụ **0.1.0**, Tuấn (`mtuan2491`), 08/11/2026. Python **3.9+**, chỉ dùng standard library; đã kiểm bằng Python 3.12.14 trên Windows. Công cụ đọc log offline, không chạy app/server, gửi FCM hoặc sửa dữ liệu nguồn. Đây là phần làm trước SEM-45; chưa có CSV đo chính để nghiệm thu toàn task.

Nguồn: [SEM-24/exporter](README.md), [event schema 2.0.0](../docs/EVENT_SCHEMA.md), [PROTOCOL 1.0.0](PROTOCOL.md), [yêu cầu SEM-45](../tasks/backlog/SEM-45.md), [CHECKS](../docs/evidence/SEM-45/CHECKS.md).

## Chạy ngay bằng fixture

Từ root repo; `python` là Python 3.9+ đang hoạt động trên máy. Khi alias Windows không hoạt động, thay bằng đường dẫn executable đã cài. Không cần cài thư viện.

```sh
python -B experiments/scripts/analyze.py \
  --dataset fixture --run experiments/fixture_exports/run-sem24-fixture \
  --output-base .local/sem45 --batch-id fixture-check

python -B -m unittest discover -s experiments/scripts/tests -v
```

Output nằm trong `.local/sem45/fixture_analysis/fixture-check/`. Chạy lại phải chọn `--batch-id` mới: công cụ từ chối ghi đè. Fixture SEM-24 có event để kiểm pipeline nhưng manifest ghi **NOT_RUN**, không có cửa sổ monotonic được xác nhận; kết quả giữ nguyên NOT_RUN, có cờ thiếu cửa sổ và không vào mẫu số main. Các fixture ở unit tests có thêm success/timeout/late/retry/boot/clock để kiểm tính toán, vẫn hoàn toàn tổng hợp.

Trên PowerShell có thể đặt `$env:TMPDIR`, `$env:TMP`, `$env:TEMP` của phiên kiểm vào một thư mục `.local/` đã tạo nếu sandbox không cho ghi temp mặc định. Thiết lập này chỉ phục vụ test, không sửa code/config app hoặc cấu hình Windows toàn cục.

## Đầu vào và phân loại dữ liệu

- Mỗi `--run` là một thư mục có **manifest.json và events.jsonl canonical** đã được làm sạch/kiểm bàn giao. Lặp `--run` để phân tích nhiều run; không tự quét thư mục rồi vô tình lấy thêm pilot hoặc fixture.
- `--dataset main` là mặc định: chỉ nhận OBSERVED/main. `pilot` chỉ nhận OBSERVED/pilot; `fixture` chỉ nhận FIXTURE/development. Output luôn ở `<output-base>/<dataset>_analysis/<batch-id>/`; fixture/pilot không xuất thẳng vào `experiments/results.csv`.
- Nhận đúng manifest 1.0.0, protocol 1.0.0, API/event 2.0.0; event phải có đúng 27 key. Unknown field/type/version và log legacy bị từ chối, không tự điền trường hoặc nâng version. Bản 0.1.0 cố ý chỉ hỗ trợ contract đã kiểm.
- Dùng validator của SEM-24 để kiểm kiểu, version, source/outcome và correlation bắt buộc. Mọi event phải khớp run/device/mode của manifest; không lọc bỏ dòng khác run để che nguồn lẫn dữ liệu. Replay cùng event ID và giá trị được dedup; conflict ID dừng toàn batch.
- Hash SHA-256 được tính từ byte file thực tế. Giữ nguyên UTC, elapsed time, version, outcome và ID; không sort timeline liên máy thành quan hệ nhân quả. Chỉ sort các dòng CSV theo run/device để tái lập.
- Chỉ đưa export đã làm sạch vào analyzer. Kiểm signature trong validator không thay danh sách deny local hoặc rà dữ liệu nhạy cảm của người xuất. Analyzer không nhận raw logcat/DB/FCM response, không xuất message ID hoặc error text ra CLI. Metadata build/config được giữ trong report để truy vết, không được chứa secret.

[Pilot SEM-29](../docs/evidence/SEM-29/CHECKS.md) dùng Android `legacy-room-v1`, đã được nghiệm thu riêng cho pilot. Công cụ này **từ chối format đó**; không thêm alias/mode/clock/correlation giả để vượt validator, không dùng pilot thay SEM-41/42.

## File đầu ra

| File | Nội dung |
|---|---|
| `results.csv` trong batch | Một dòng/run; nhận dạng/dataset/build/hash, outcome/validity khai báo, evidence trong cửa sổ, counts, duration và cờ chất lượng |
| `summary.json` | Nhóm theo toàn bộ case/subscenario/device/mode/build/OS/config/protocol/schema/phase/intervention; số input/eligible/excluded/complete, outcome và thống kê có mẫu số |
| `analysis_report.json` | Marker COMPLETED ghi cuối, SHA-256 CSV/summary/analyzer/validator và input, counts toàn run/trong cửa sổ, fetch pairs, clock và lý do/cờ từng run |

Mỗi batch được kiểm hết trước khi tạo output. Nếu lỗi ghi file, công cụ báo `OUTPUT_WRITE_FAILED`; batch thiếu `analysis_report.json` COMPLETED không được dùng. Không ghi đè batch cũ, không sửa file nguồn. CSV/JSON xuất UTF-8/LF trên cả Windows. Khác batch ID làm report khác batch ID; CSV/summary không thay khi input/công cụ không đổi hoặc chỉ đổi thứ tự `--run`.

Giá trị chưa đủ căn cứ là **ô CSV rỗng / JSON null**, không phải 0. Số 0 chỉ là duration đo được bằng nhau hoặc số event đã phân loại bằng 0. Counts trong cửa sổ không chứng minh event vắng mặt khi cửa sổ/boot/log chưa đủ; luôn đọc `window_basis`, flags và input evidence cùng counts.

## Quy tắc tính

| Chỉ số / trường | Cách tính và giới hạn |
|---|---|
| `outcome`, `validity`, `execution_status` | Giữ nguyên manifest; không tự đổi TIMEOUT thành SUCCESS khi phát hiện late apply |
| Cửa sổ | Android elapsed nằm trong **[start, end]**, cùng boot alias khác null. Thiếu mốc/boot: unknown, không suy membership từ UTC chưa kiểm soát |
| `target_applied_in_window` | Có `snapshot_applied` đúng target version, source nền phù hợp và cùng cửa sổ. Hint/accepted/unchanged không thay bằng chứng applied; version lớn hơn target không tự được coi là đúng target |
| `observed_completion` | NOT_RUN / APPLIED_TARGET / LATE_TARGET / NO_TARGET_EVIDENCE / UNCERTAIN_WINDOW; là mô tả evidence, không ghi đè outcome hoặc chứng nhận ca đã Pass |
| `received_to_enqueue_ms` | Một receipt nối qua signal IDs tới enqueue của request áp dụng target; ambiguity/coalesce nhiều receipt để null |
| `queue_ms` | Enqueue → work_started attempt 0 của cùng request/work. Periodic không có one-time enqueue: null |
| `sync_ms` | Work_started → applied của **cùng attempt** áp dụng target; đây là attempt duration, không bao gồm toàn bộ backoff trước retry |
| `update_to_applied_ms`, `update_to_received_ms` | Server update đúng target → Android event; offset = server − Android. Chỉ xuất khi clock ANDROID có đủ mẫu hợp lệ, bao quanh event và UTC/monotonic không mâu thuẫn. Không đo accepted → received như delivery latency |
| Uncertainty liên máy | Estimate dùng trung bình offset trước/sau; bound = max uncertainty trước/sau + nửa chênh offset. Mỗi uncertainty phải bao được RTT/2 + resolution + độ lệch của mẫu so với offset khai báo. Khoảng estimate − bound < 0: null. Đây là mô hình offset có khai báo, không chứng nhận đồng hồ chính xác tuyệt đối |
| Fetch duration | Cặp start/completed cùng network_call_id/request/work/attempt và cùng boot. Thiếu đầu/cuối hoặc duration âm: null. ID reused/correlation conflict bị từ chối |
| `get_started_count` | Số network_call_id bắt đầu GET quan sát được trong cửa sổ, loại MANUAL; không chứng minh server nhận đủ request hoặc instrumentation đầy đủ |
| `natural_periodic_cycles` | Số request PERIODIC mới, attempt 0 bắt đầu trong cửa sổ; một work ID có nhiều cycle, retry không thành cycle mới. Request đã bắt đầu ở setup không tính lại |
| Retry / applied / DB writes | Đếm event retry/applied riêng; `db_write_count=null` vì schema chưa instrument số write SQL/items. Không quy đổi thành mAh |

Duration nội bộ chỉ trừ monotonic cùng alias/boot. Boot khác/không biết không được nối. Work ID không đủ để join các periodic cycle; request ID phải giữ cùng work/source. Send attempt/message ID không bị gán tùy tiện cho receipt; signal IDs nối server với callback. Event thiếu không tự tạo timeout hoặc thành công: outcome vẫn do người chạy khai từ cửa sổ/evidence.

### Mẫu số và thống kê

`eligible=true` chỉ cho OBSERVED/main, VALID, COMPLETED, có cửa sổ đầy đủ theo metadata và không có cờ mâu thuẫn đã phát hiện. TIMEOUT/FAILURE/UNKNOWN hợp lệ vẫn nằm trong mẫu số; NOT_RUN/ABORTED/INVALID/NOT_ASSESSED/fixture/pilot được lưu trong kết quả nhưng loại riêng khỏi mẫu số chính. Cờ setup/MANUAL/reopen trong window, source/mode sai, thiếu target/boot, cửa sổ ngắn hoặc outcome trái evidence chặn eligible.

`n_complete` là eligible có outcome SUCCESS và applied đúng target trong cửa sổ. Completion rate = n_complete/n_eligible. Median/min/max chỉ tính trên các complete có metric; mỗi metric có n_measured/n_missing. Thiếu clock không loại một run có outcome hợp lệ, chỉ khiến latency liên máy null. E01 vẫn là một session, không tách cycle thành run độc lập; dưới 3 cycle được báo count thật để owner quyết định chạy bổ sung.

Summary ở bản này là **whole-run**, không tự chứng nhận hoặc thống kê riêng phase idle/offline của E03/E04 từ mốc UTC không rõ hệ clock. Khi nhận dữ liệu chính, phải đối chiếu milestones, OS evidence và phase trước/trong/sau từ SEM-41/42; nếu cần phase aggregate thì bổ sung mapping clock có căn cứ và test trước khi công bố, rồi bàn giao SEM-44 kiểm độc lập. Tương tự, số applied không tự chứng minh race E05/không ghi trùng, hay fault injection E06 đã được tạo đúng. `eligible` là bộ lọc dựa trên manifest/cờ, **không thay kiểm độc lập của SEM-44**.

## Bước 4 — sau khi nhận SEM-41/42

1. Nhận CHECKS, commit/candidate/APK/config, manifest, event canonical v2 và evidence thật; giữ run chưa chạy/thiếu OPPO đúng NOT_RUN. Đối chiếu schema/window/clock/case và các phase, không đổi legacy thành v2 bằng giả định.
2. Chạy với danh sách run được nhận, không dùng wildcard lấy cả pilot. Ví dụ cấu trúc lệnh dưới phải thay đường dẫn bằng run thực tế, **chưa được chạy trong SEM-45**:

```sh
python -B experiments/scripts/analyze.py --dataset main \
  --run experiments/runs/<emulator-main-run> \
  --run experiments/runs/<oppo-main-run> \
  --output-base .local/sem45 --batch-id main-review
```

3. Tự kiểm report/hash/flags/denominator, xử lý thiếu instrumentation hoặc phase mapping tại đúng owner; đưa CSV main đã kiểm vào `experiments/results.csv`, ghi lệnh/danh sách run và commit trong CHECKS để bàn giao SEM-43/44/48/50. SEM-44 nhận CSV từ SEM-45 để kiểm độc lập, không phải gate đầu vào mới của SEM-45. Không đánh dấu SEM-45 Done chỉ vì test fixture đạt.
