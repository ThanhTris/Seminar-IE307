# Phân tích manifest/JSONL — SEM-45

Phiên bản công cụ **0.7.0**, Tuấn (`mtuan2491`), cập nhật 21/11/2026 theo review cửa sổ E02 và dữ liệu pilot mới. Python **3.9+**, standard library và Git khi dùng index nguồn. Đã kiểm trên Windows với Python 3.12.14 và Ubuntu 24.04. Analyzer đọc dữ liệu offline và xuất CSV, summary, report có checksum. [Yêu cầu SEM-45](../tasks/backlog/SEM-45.md) · [CHECKS](../docs/evidence/SEM-45/CHECKS.md).

## Bộ kết quả bàn giao

[results.csv](results.csv) có **23 dòng OBSERVED/pilot** từ snapshot main `aa425c3`. PR #29 cung cấp 20 lượt, gồm 12 lượt lịch sử INVALID sau audit collector và 8 lượt chạy lại VALID. PR #35 cung cấp 3 lượt E01, gồm 2 VALID/COMPLETED và 1 INVALID/ABORTED. `source_pr` và `source_merge_commit` được ghi cho từng input. Tất cả là pilot và mẫu số main bằng 0. [INPUTS.json](../docs/evidence/SEM-45/INPUTS.json).

OPPO `run-sem42-oppo-e01-03` có 5 chu kỳ theo Android elapsed trong 90 phút và apply v5 ở `930021 ms` tính từ đầu cửa sổ, qua `ADB_REVERSE` khi cấp nguồn USB. Emulator `run-sem41-pilot-e01-1-20261120-8d5816` có 2 chu kỳ, dưới mục tiêu 3, qua `EMULATOR_HOST_GATEWAY`. Lượt OPPO `run-sem42-oppo-e01-02` bị hủy và thiếu mốc mở nên không có số chu kỳ trong cửa sổ. [CHECKS SEM-42](../docs/evidence/SEM-42/CHECKS.md).

Ba pilot E01 của PR #35 cùng ghi APK `814347F…`, provenance ở PR #37. `DBAAD…` là SHA của bản debug dưới `release/`. Nhóm thống kê dùng toàn bộ `build`, `device` và `config`, gồm `server_route` và `powered`. Event Android thiếu boot ID nên các metric đã xác minh cùng boot vẫn để trống. Hai cột `pilot_elapsed_*_unverified_boot` mô tả phép đếm/đối chiếu elapsed của pilot E01 hoàn tất theo mốc khai báo. Đồng hồ liên máy chưa kiểm soát nên latency server → Android để trống. [Build manifest](../release/BUILD_MANIFEST.json) · [Giới hạn](../docs/evidence/SEM-45/CHECKS.md).

## Tái lập bộ kết quả

Từ root repo, dùng Python 3.9+ đang hoạt động. Khi Windows alias không hoạt động, thay `python` bằng đường dẫn executable đã cài. Các lệnh dưới dùng cú pháp shell hỗ trợ `\` để xuống dòng, trên PowerShell có thể viết mỗi lệnh thành một dòng.

```sh
git fetch origin aa425c33bdee034afcc552ebc390cae6780f6dbe

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

### Checkout Windows đã có sẵn

Sau merge, file `export_logs.py` có thể còn CRLF dù `.gitattributes` quy định LF. CSV/summary vẫn tái lập được, còn `validator_sha256` phản ánh byte CRLF đang được dùng. Để đối chiếu report với byte LF đã commit, chạy đoạn PowerShell dưới từ root repo, rồi dùng batch ID mới để chạy analyzer. Đoạn kiểm so sánh nội dung với HEAD trước khi ghi lại cả hai file từ Git. Nếu có sửa nội dung local, Git trả lỗi và quá trình dừng để giữ phần chỉnh sửa đó.

```powershell
@'
from pathlib import Path
import subprocess
paths = ["experiments/scripts/analyze.py", "experiments/scripts/export_logs.py"]
for path in paths:
    subprocess.run(["git", "diff", "--quiet", "HEAD", "--", path], check=True)
for path in paths:
    content = subprocess.check_output(["git", "show", "HEAD:" + path])
    Path(path).write_bytes(content)
'@ | python -
```

Đã thử trên bản checkout local riêng với validator CRLF. Report lệch đúng trường `validator_sha256`, sau khi lấy byte LF từ Git thì report khớp sau chuẩn hóa `batch_id`. Report vẫn hash byte thực tế của mã được chạy.

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

### Điều kiện hợp lệ theo ca

- **E02** cần `server_updated` duy nhất của target version và event sender có cùng `update_id`, version và tín hiệu. Sender `accepted` hoặc `unknown` phải đi cùng callback `push_received` có cùng `run_id`, `device_alias`, `signal_id`. Cùng tín hiệu phải nối được qua `work_enqueued`, `work_started` và `snapshot_applied` theo request/work và attempt thực hiện apply. Callback phải đi trước hoặc cùng mốc elapsed với enqueue và worker start cùng boot. Log xác nhận enqueue có thể xuất hiện sau worker start do cách WorkManager xác nhận, khi đó `queue_ms` để trống. Mốc phản hồi server có thể được ghi sau callback.
- E02 khai báo `SUCCESS` mà chuỗi không xác minh được nhận `E02_PUSH_CHAIN_UNVERIFIED`, giữ outcome và event gốc, loại khỏi mẫu số và để trống timing dựa vào chuỗi chưa đủ căn cứ. Lượt timeout/lỗi đủ cửa sổ vẫn được tính khi không có apply trong cửa sổ. Event gửi thất bại vẫn có trong report để truy vết.
- Khi clock liên máy đã xác minh được, E02 quy đổi target commit sang Android UTC và xét sai số. Nếu cả khoảng commit nằm sau callback hoặc apply của cùng chuỗi trong cửa sổ, analyzer gắn `E02_PUSH_CLOCK_ORDER_CONFLICT` và loại lượt khỏi mẫu số. Khi khoảng sai số chồng lên callback/apply, thứ tự chưa thể kết luận mâu thuẫn và latency liên quan có thể để trống. Thời điểm server ghi nhận phản hồi FCM có thể muộn hơn callback.
- E02 kiểm riêng clock của cửa sổ. Khi mốc mở nằm ngoài khoảng commit đã quy đổi ± sai số, analyzer gắn `E02_WINDOW_START_CLOCK_CONFLICT` và loại lượt khỏi mẫu số, kể cả khi outcome là `TIMEOUT`. Các mốc cửa sổ, nhãn late theo cửa sổ đã khai báo, outcome và event gốc được giữ để truy vết.
- **E03** cần `deep_idle_during=IDLE`, mốc start/enter/exit/end có thứ tự và tách đủ 5 phút baseline, 20 phút deep Doze, 10 phút sau thoát. Tổng thời lượng UTC phải khớp khoảng elapsed realtime trong dung sai 1 giây. Mốc pha dùng cùng clock quan sát khai báo trong manifest. Trạng thái thiếu/mâu thuẫn hay pha thiếu, đảo thứ tự hoặc quá ngắn bị gắn cờ và loại khỏi mẫu số. Outcome và event nguồn vẫn đọc được. Xác nhận checkpoint thực tế trong lúc Doze và phase event counts dựa vào audit của lượt chạy. [Protocol](PROTOCOL.md).
- E03 áp dụng clock Android đã kiểm với mẫu trước/sau cửa sổ và mốc UTC–elapsed cùng boot. Toàn bộ khoảng sai số của `server_updated` duy nhất cho đúng target phải nằm trong `[idle_start_utc, idle_exit_utc)`. Update ở baseline hoặc sau khi thoát Doze nhận `E03_TARGET_UPDATE_OUTSIDE_DOZE`. Thiếu mốc update duy nhất, clock chưa đối chiếu được hoặc khoảng sai số chồng ranh giới nhận `E03_TARGET_UPDATE_TIME_UNVERIFIED`. Apply chắc chắn có trước target commit nhận `E03_APPLIED_BEFORE_TARGET_UPDATE`. Các lượt có cờ này bị loại khỏi mẫu số, giữ nguyên outcome và event nguồn.

- **E04** cần `offline_utc`, `reconnect_utc`, mốc start/end và clock `ANDROID` đã controlled. Các mẫu clock phải bao quanh cửa sổ, anchor UTC − elapsed của event cùng boot phải khớp mốc manifest trong bound `2 × uncertainty`. Milestone được tiếp nhận trên cơ sở Android UTC đã khai báo và đối chiếu này. Milestone từ host hoặc chưa xác minh cơ sở clock nhận cờ `E04_RECOVERY_CLOCK_UNVERIFIED`.
- Khoảng offline phải đủ 2 phút, sau reconnect còn ít nhất 30 phút với PERIODIC hoặc 5 phút với PUSH. Khoảng không hợp lệ/cửa sổ ngắn nhận `E04_OFFLINE_INTERVAL_INVALID` hoặc `E04_RECOVERY_WINDOW_SHORT`. TIMEOUT đủ cửa sổ và evidence vẫn được giữ trong mẫu số hợp lệ.
- E04 cần một `server_updated` duy nhất cho target version. Quy đổi sang Android UTC bằng thời điểm server trừ offset server − Android, rồi xét toàn bộ khoảng ± uncertainty. Chỉ công nhận khi khoảng này nằm trọn trong `[offline_utc, reconnect_utc)`. Khoảng nằm ngoài nhận `E04_TARGET_UPDATE_OUTSIDE_OFFLINE`. Thiếu update đúng target, có nhiều update cùng target hoặc khoảng sai số chạm qua ranh giới nhận `E04_TARGET_UPDATE_TIME_UNVERIFIED`. Các lượt này giữ outcome và event để truy vết, để trống latency và bị loại khỏi mẫu số.
- Apply trước reconnect ngoài bound nhận `E04_APPLIED_BEFORE_RECONNECT` và bị loại khỏi mẫu số. Apply nằm trong bound quanh reconnect nhận `E04_APPLY_TIME_UNVERIFIED`. Các trường hợp chưa xác minh để completion null và `UNCERTAIN_WINDOW`; outcome nguồn được giữ để truy vết.
- **E06** cần chuỗi PERIODIC `work_started → snapshot_fetch_started → snapshot_fetch_completed → snapshot_applied` cùng request/work/attempt, cặp fetch cùng network_call_id. Fetch phải HTTP 200/success, đúng target version, cùng device/boot khác null và thứ tự elapsed không giảm. Log có thể được cung cấp khác thứ tự dòng.
- Thiếu fetch, sai correlation/target/status/thứ tự/boot nhận `E06_FETCH_CHAIN_UNVERIFIED` và loại khỏi mẫu số. Mâu thuẫn correlation nội bộ vẫn trả lỗi contract hiện có. Chuỗi đủ evidence mới được xét `APPLIED_TARGET`; TIMEOUT chưa có apply vẫn được đánh giá theo cửa sổ và evidence skip thật.
- E06 cần `push_send_skipped` cho cùng `update_id` và target version của `server_updated`. Nếu có `push_send_accepted`, `push_send_rejected` hoặc `push_send_unknown` cho cặp này, `E06_FAULT_SKIP_CONFLICTING_SEND` đánh dấu đã thử gửi qua provider và loại lượt khỏi mẫu số. Report vẫn giữ event skip/send, outcome khai báo và bằng chứng periodic apply để truy vết.

Bộ v0.7.0 có CSV, summary và report tái lập từ cùng source index. Đếm chu kỳ descriptive hoặc cùng boot đều dùng `work_started` nguồn PERIODIC, attempt 0, request ID riêng trong cửa sổ elapsed. Request có attempt 0 ngoài cửa sổ bị loại. Lượt hủy và thiếu mốc giữ giá trị trong cửa sổ là null.

## Nhóm thống kê và bàn giao tiếp

Nhóm dùng case/subscenario/device/mode/build/OS/config/protocol/schema/phase/intervention và context epoch có trong index. Bộ pilot này tạo 7 nhóm, tách store r2, r3 và epoch chưa biết. Nếu phân tích thư mục local thuộc nhiều epoch, cung cấp metadata epoch qua index hoặc chạy batch riêng.

`eligible=true` chỉ cho OBSERVED/main, VALID, COMPLETED, có cửa sổ đầy đủ và không có cờ chất lượng đã phát hiện. TIMEOUT/FAILURE/UNKNOWN hợp lệ được giữ trong mẫu số main. NOT_RUN/ABORTED/INVALID/NOT_ASSESSED/fixture/pilot có hàng kết quả và thống kê loại riêng.

Summary có `declared_outcomes` và `valid_completed_declared_outcomes` để đọc outcome nguồn. Sau thu hồi qualification, `valid_completed_declared_outcomes` rỗng ở cả 7 nhóm. `n_complete`, completion_rate và median/min/max dùng tập eligible có applied target đã xác minh, mỗi metric có n_measured/n_missing. Bộ pilot hiện có `n_eligible=0`, completion_rate=null. Chưa có cơ sở xuất tỷ lệ hoặc latency main.

Report lưu hash, raw/window event counts, bucket setup/window/late/unknown, fetch pairs và lý do clock. Summary hiện là whole-run. Phân tích riêng phase idle/offline E03/E04, race E05, callback FCM và so sánh OPPO vẫn Not run trong SEM-45. Các audit OS của người chạy được tham chiếu theo commit nguồn.

Khi có main logs từ SEM-41/42, nhận commit/build/config/clock/CHECKS, chạy `--dataset main` với danh sách run cụ thể, kiểm cờ và mẫu số rồi cập nhật bộ CSV/report/index. SEM-43 và SEM-48 có thể dùng bộ pilot mới để làm mới SUMMARY và biểu đồ theo từng build, thiết bị và route. SEM-50 có thể dẫn run-03 trực tiếp với nhãn pilot, điều kiện USB/ADB reverse và giới hạn clock/boot. SEM-44 tiếp nhận để kiểm độc lập.
