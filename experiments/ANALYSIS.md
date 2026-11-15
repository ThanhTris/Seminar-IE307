# Phân tích manifest/JSONL — SEM-45

Phiên bản công cụ **0.2.0**, Tuấn (`mtuan2491`), cập nhật 16/11/2026 theo review của Trí. Python **3.9+**, standard library và Git khi dùng index nguồn. Đã kiểm trên Windows với Python 3.12.14. Analyzer đọc dữ liệu offline và xuất CSV, summary, report có checksum. [Yêu cầu SEM-45](../tasks/backlog/SEM-45.md) · [CHECKS](../docs/evidence/SEM-45/CHECKS.md).

## Bộ kết quả bàn giao

[results.csv](results.csv) giữ **12 dòng OBSERVED/pilot đã bàn giao tại `dec00b7`**, đọc lại theo commit `42ca000da1de2b7465851e1485fec2631f4b1a3c` của Draft PR #29. Bộ này có **0 VALID / 12 INVALID** sau audit collector. Nguồn thu hồi qualification của 8 lượt từng VALID vì `dumpsys jobscheduler` trong cửa sổ có thể tác động timer, với lý do `IN_WINDOW_JOB_DUMP_CAN_REEVALUATE_TIMERS`. `eligible=false` ở cả 12 dòng và mẫu số main bằng 0. [Nguồn SEM-41](https://github.com/ThanhTris/Seminar-IE307/blob/42ca000da1de2b7465851e1485fec2631f4b1a3c/docs/evidence/SEM-41/CHECKS.md).

Revision nguồn còn có 6 lượt chạy lại được đánh dấu VALID, batch đo lại đang RUNNING. Lần sửa theo review này giữ phạm vi 12 lượt cũ. Sáu lượt mới nằm ngoài CSV và được liệt kê tại `selection_scope.excluded_new_run_directories` trong index. Qualification của bộ cũ là `REVOKED_AFTER_SCHEDULER_COLLECTOR_AUDIT`. [INPUTS.json](../docs/evidence/SEM-45/INPUTS.json).

Event Android trong bộ này có `boot_session_id=null`. CSV giữ `observed_completion=UNCERTAIN_WINDOW`, các count trong cửa sổ, completion và duration chưa xác minh để rỗng. Outcome lịch sử gồm 5 SUCCESS, 5 TIMEOUT và 2 FAILURE được giữ cùng validity INVALID để truy vết. Nguồn còn ghi 27 slot main chưa chạy và profile đo chưa cấu hình Firebase. OPPO chưa có bộ log nhận cho lần bàn giao này. [Giới hạn và phần Not run](../docs/evidence/SEM-45/CHECKS.md).

## Tái lập bộ kết quả

Từ root repo, dùng Python 3.9+ đang hoạt động. Khi Windows alias không hoạt động, thay `python` bằng đường dẫn executable đã cài. Các lệnh dưới dùng cú pháp shell hỗ trợ `\` để xuống dòng, trên PowerShell có thể viết mỗi lệnh thành một dòng.

```sh
git fetch origin 42ca000da1de2b7465851e1485fec2631f4b1a3c

python -B experiments/scripts/analyze.py --dataset pilot \
  --source-index docs/evidence/SEM-45/INPUTS.json \
  --output-base .local/sem45-review --batch-id review-1

python -B experiments/scripts/analyze.py --dataset pilot \
  --source-index docs/evidence/SEM-45/INPUTS.json \
  --output-base .local/sem45-review --batch-id review-2

python -B -m unittest discover -s experiments/scripts/tests
git diff --check
```

Nếu object nguồn đã có local thì có thể chạy analyzer trực tiếp. Analyzer đọc bằng `git show` theo full commit, không tự truy cập mạng. Thiếu object trả `SOURCE_OBJECT_UNAVAILABLE`. Index ghi đường dẫn, SHA-256 manifest/events, evidence nguồn và epoch store của từng run. Hash lệch dừng toàn batch trước khi tạo output. Source PR và trạng thái Draft tại lúc nhận được lưu trong index/report. [INPUTS.json](../docs/evidence/SEM-45/INPUTS.json).

So sánh các file sau với bộ được commit. CSV và summary của hai batch phải giống từng byte. Report giữ batch ID nên trường đó thay theo lần chạy.

| File tái lập dưới `pilot_analysis/<batch-id>/` | File bàn giao |
|---|---|
| `results.csv` | [experiments/results.csv](results.csv) |
| `summary.json` | [summary.json](../docs/evidence/SEM-45/summary.json) |
| `analysis_report.json` | [analysis_report.json](../docs/evidence/SEM-45/analysis_report.json) |

`.gitattributes` giữ LF cho CSV, JSON của SEM-45 và hai file Python được hash trong report. SHA-256 được tính trên byte thực tế. Khi công cụ/validator/index thay đổi có chủ ý, phải sinh lại report và kiểm lại kết quả. Batch có sẵn bị từ chối với `OUTPUT_EXISTS`, chọn ID mới để chạy lại.

Trên máy sandbox, có thể đặt TEMP/TMP/TMPDIR của tiến trình kiểm vào thư mục `.local/` đã tạo. Các file tạm không thuộc artifact bàn giao.

## Fixture và thư mục run local

```sh
python -B experiments/scripts/analyze.py --dataset fixture \
  --run experiments/fixture_exports/run-sem24-fixture \
  --output-base .local/sem45-review --batch-id fixture-1
```

Mỗi `--run` nhận một thư mục chứa manifest.json và events.jsonl canonical. Lặp tham số để phân tích nhiều run. `--run` và `--source-index` là hai cách cung cấp đầu vào cho cùng loader. Dataset mặc định là `main`, cần chọn `pilot` hoặc `fixture` khi phân tích bộ tương ứng. Output luôn ở `<output-base>/<dataset>_analysis/<batch-id>/`.

- `main` nhận OBSERVED/main với candidate gate hợp lệ theo validator SEM-24.
- `pilot` nhận OBSERVED/pilot. Bộ cập nhật ngày 16/11 dùng lựa chọn này.
- `fixture` nhận FIXTURE/development. Fixture SEM-24 giữ outcome NOT_RUN và mẫu số main bằng 0.

Loader tái sử dụng validator SEM-24, nhận manifest/protocol 1.0.0 và API/event 2.0.0, đúng 27 key/event. Schema lạ, field/type sai, route run/device/mode lẫn nhau, duplicate ID xung đột và JSON không hợp lệ bị từ chối. Replay cùng ID/giá trị được dedup và có count trong report. Pilot SEM-29 dùng `legacy-room-v1` trả `CONTRACT_VERSION_UNSUPPORTED`. [Exporter](README.md) · [Event schema](../docs/EVENT_SCHEMA.md).

Chỉ dùng export đã được làm sạch và có evidence nguồn. Metadata build/config phải bảo đảm an toàn công bố. Hash và validator hỗ trợ truy vết, người xuất vẫn cần rà dữ liệu nhạy cảm theo quy trình nguồn.

## Cột CSV và quy tắc tính

| Trường | Ý nghĩa |
|---|---|
| Nhận dạng, phase, build và hash | Một dòng/run; giữ run/device/case/subscenario/mode, phase, app/server commit, APK hash và SHA-256 input |
| `server_store_epoch` | Metadata từ PILOT_RESULTS nguồn, được đối chiếu khi lập index và dùng tách nhóm. Manifest canonical hiện chưa có trường này |
| `outcome`, `validity`, `execution_status` | Giá trị do manifest nguồn khai báo |
| `declared_cached_version_after`, `declared_natural_periodic_cycles` | Giá trị người chạy ghi trong manifest; tách khỏi count mà analyzer kiểm từ event |
| `window_basis`, `window_events_verified` | Có mốc monotonic trong manifest và khả năng phân loại tất cả event Android theo cùng boot |
| `observed_completion` | NOT_RUN / APPLIED_TARGET / LATE_TARGET / NO_TARGET_EVIDENCE / UNCERTAIN_WINDOW |
| `target_applied_in_window` | Có snapshot_applied đúng target/source trong cửa sổ cùng boot. Không xác minh được membership thì để rỗng |
| `*_event_count_all` | Count event toàn export đã dedup, gồm cả setup và ngoài cửa sổ. Giữ riêng server_updated, send accepted/skipped, received, enqueue, started, fetch started và applied |
| `natural_periodic_cycles` | Count request PERIODIC mới, attempt 0 bắt đầu trong cửa sổ; request đã bắt đầu ở setup được loại |
| `work_attempt_count`, `get_started_count`, retry/applied count | Event trong cửa sổ, loại MANUAL. Cửa sổ/event boot chưa đủ thì để rỗng |
| `received_to_enqueue_ms` | Receipt nối qua signal IDs tới enqueue của request áp dụng target. Join mơ hồ để rỗng |
| `queue_ms` | Enqueue → work_started attempt 0 cùng request/work |
| `sync_ms` | Work_started → snapshot_applied của cùng attempt áp dụng target |
| `update_to_received_ms`, `update_to_applied_ms` | Server update đúng target → Android event, với clock ANDROID đủ mẫu và uncertainty |
| `db_write_count` | Rỗng vì schema chưa instrument số write SQL/items |
| `flags` | Các giới hạn/mâu thuẫn phát hiện được, nối bằng ký tự pipe |

Duration Android dùng elapsed realtime cùng device và boot khác null. Fetch được nối bằng network_call_id/request/work/attempt, thiếu đầu/cuối hoặc thời gian âm để null. Work ID dùng chung giữa các periodic cycle vẫn cần request ID riêng.

Clock liên máy dùng offset server − Android. Mẫu trước/sau phải bao quanh event, uncertainty bao được RTT/2 + resolution và sai lệch offset khai báo. Bound gồm uncertainty lớn nhất và nửa chênh offset trước/sau. UTC/monotonic mâu thuẫn hoặc estimate − bound âm khiến latency null. Accepted, received, enqueue và applied có mốc riêng theo schema. [Protocol](PROTOCOL.md).

Giá trị chưa đủ căn cứ là ô CSV rỗng hoặc JSON null. Số 0 biểu thị count/duration đã kiểm được bằng 0. Với event thiếu boot, `OUTCOME_EVIDENCE_UNVERIFIED` thể hiện chưa đối chiếu được một SUCCESS khai báo. Khi cửa sổ đầy đủ và outcome trái evidence, công cụ ghi `OUTCOME_EVIDENCE_CONFLICT`. TIMEOUT cùng late apply giữ nguyên TIMEOUT và báo late riêng.

## Nhóm thống kê và bàn giao tiếp

Nhóm dùng case/subscenario/device/mode/build/OS/config/protocol/schema/phase/intervention và context epoch có trong index. Bộ pilot này tạo 7 nhóm, tách store r2, r3 và epoch chưa biết. Nếu phân tích thư mục local thuộc nhiều epoch, cung cấp metadata epoch qua index hoặc chạy batch riêng.

`eligible=true` chỉ cho OBSERVED/main, VALID, COMPLETED, có cửa sổ đầy đủ và không có cờ chất lượng đã phát hiện. TIMEOUT/FAILURE/UNKNOWN hợp lệ được giữ trong mẫu số main. NOT_RUN/ABORTED/INVALID/NOT_ASSESSED/fixture/pilot có hàng kết quả và thống kê loại riêng.

Summary có `declared_outcomes` và `valid_completed_declared_outcomes` để đọc outcome nguồn. Sau thu hồi qualification, `valid_completed_declared_outcomes` rỗng ở cả 7 nhóm. `n_complete`, completion_rate và median/min/max dùng tập eligible có applied target đã xác minh, mỗi metric có n_measured/n_missing. Bộ pilot hiện có `n_eligible=0`, completion_rate=null. Chưa có cơ sở xuất tỷ lệ hoặc latency main.

Report lưu hash, raw/window event counts, bucket setup/window/late/unknown, fetch pairs và lý do clock. Summary hiện là whole-run. Phân tích riêng phase idle/offline E03/E04, race E05, callback FCM và so sánh OPPO vẫn Not run trong SEM-45. Các audit OS của người chạy được tham chiếu theo commit nguồn.

Khi có main logs từ SEM-41/42, nhận commit/build/config/clock/CHECKS, chạy `--dataset main` với danh sách run cụ thể, kiểm cờ và mẫu số rồi cập nhật bộ CSV/report/index. SEM-43/44/48/50 nhận bộ hiện tại với nhãn pilot/INVALID để kiểm pipeline và truy vết lịch sử. Qualification bị thu hồi khiến bộ này chưa có mẫu scheduler hợp lệ cho kết luận thực nghiệm. SEM-44 tiếp nhận để kiểm độc lập. Các lượt đo lại cần được nhận riêng theo commit/evidence của batch tương ứng.
