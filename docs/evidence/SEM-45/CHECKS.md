# SEM-45 — Kiểm parser và bàn giao kết quả offline

- Người thực hiện Tuấn (`mtuan2491`), cập nhật **19/11/2026 (UTC+7)** theo review E02/E03 của Trí trên `0faf74d`.
- Nhánh `codex/SEM-45-log-parser`, tạo từ main `d29532ac19a2fba402d2d1c6d25dfb63a306a87a` ngày 08/11. Đã nhận main `9caaf38` bằng merge commit `42a466a`, gồm code sau PR #29 và các consumer SEM-43/44/48.
- **Đầu ra SEM-45 được sửa theo review**, gồm parser, CSV của 12 lượt pilot lịch sử, index nguồn, summary/report và hướng dẫn tái lập. Bộ được chọn hiện có **0 VALID / 12 INVALID** do thu hồi qualification. Trạng thái Project vẫn In Progress trong lần bàn giao này.
- Chính sách task hiện hành cho phép bàn giao đầu ra có thật cùng Not run/giới hạn cho đầu vào chưa nhận. Ghi chú chờ toàn bộ SEM-41/42 ngày 08/11 đã được thay bằng phạm vi kiểm chứng dưới đây. [Quy định SEM-45](../../../tasks/backlog/SEM-45.md).

## Các bước và commit

| Bước tiếp tục ngày 15/11 | Kết quả | Commit |
|---|---|---|
| 1. Cập nhật nền | Merge main mới nhất và kiểm lại 71 test cũ | `0d4a0e9` |
| 2. Kiểm parser với đầu vào mới | Giữ dữ liệu thiếu boot ở trạng thái chưa xác minh, thêm nguồn pinned/hash và outcome khai báo. 80 test đạt | `c8ae2fe` |
| 3. Sinh artifact thật | CSV 12 dòng pilot và report tái lập từ nguồn cố định, giữ các lượt INVALID | `fd3aa8c` |
| 4. Rà bàn giao | Tách nhóm epoch store, giữ LF để checksum ổn định, chạy 81 test, sinh lại artifact, ghi giới hạn và chuẩn bị Draft PR | `dec00b7` |

Lịch sử công cụ ngày 08/11 gồm loader `85aab1c`, metrics `f7c1958`, CLI/tests/docs `eba13fe` và ghi chú tiến độ `648c81c`. Merge nền trước lần cập nhật này là `559c87c`. Các kiểm thử synthetic lịch sử đạt 71/71.

## Sửa theo review ngày 16/11

| Bước | Kết quả | Commit |
|---|---|---|
| 1. Nhận revision nguồn mới | Pin `42ca000`, kiểm 12 manifest hiện INVALID, giữ nguyên event bytes, ghi rõ phạm vi 12 lượt cũ và 6 lượt mới ngoài bộ chọn | `d202701` |
| 2. Tái sinh và kiểm artifact | CSV/summary/report/VERIFICATION mới, 81 test đạt, tái lập và checksum khớp, VALID = 0 và INVALID = 12 | `0629f24` |
| 3. Đồng bộ tài liệu bàn giao | Sửa số liệu, lý do thu hồi và giới hạn trong CHECKS/ANALYSIS/task, kiểm snapshot/link/whitespace | `1a0c667` |

## Sửa theo review ngày 18/11

| Bước | Kết quả | Commit |
|---|---|---|
| 1. Cập nhật nền | Merge main `9caaf38` vào nhánh SEM-45 | `42a466a` |
| 2. Sửa E04 | Kiểm clock/milestone/reconnect, loại apply offline, giữ uncertainty và TIMEOUT đủ cửa sổ; 6 test hồi quy | `fd53736` |
| 3. Sửa E06 | Bắt buộc fetch thành công đúng target/correlation/thứ tự trước apply; 6 test hồi quy | `5654664` |
| 4. Bàn giao | Tái sinh artifact v0.3.0, kiểm Windows/Ubuntu và CRLF → LF, cập nhật hướng dẫn/giới hạn và Draft PR | `2887ce9` |

## Sửa theo review ngày 19/11

Đã chạy `git pull --no-rebase origin main` trước khi sửa. Nhánh đã chứa main `9caaf38`, Git báo `Already up to date`.

| Bước | Kết quả | Commit |
|---|---|---|
| 1. E04 | Quy đổi `server_updated` đúng target sang Android UTC, xét khoảng sai số so với offline/reconnect và thêm 4 test hồi quy | `bfbcdea` |
| 2. E06 | Phát hiện thử gửi push cho đúng update và target, giữ ca chỉ skip cùng chuỗi periodic, thêm 2 test hồi quy | `399044d` |
| 3. Bàn giao | Tái sinh artifact v0.4.0, đối chiếu kết quả test và ghi giới hạn | `0faf74d` |

## Sửa theo review E02/E03 trên `0faf74d`

| Bước | Kết quả | Commit |
|---|---|---|
| 1. E02 | Nối update, sender, callback, enqueue và work attempt apply qua ID; bảo toàn timeout/lỗi đủ cửa sổ. Thêm 4 test | `5829ebf` |
| 2. E03 | Kiểm deep IDLE, thứ tự mốc và ba pha 5/20/10 phút trước khi tính mẫu. Thêm 5 test | `98dee5c` |
| 3. Bàn giao | Rà protocol E01–E06, tái sinh artifact v0.5.0 và kiểm Windows/Ubuntu | Commit chứa CHECKS này, tra `git log -1 -- docs/evidence/SEM-45/CHECKS.md` |

Đã đối chiếu điều kiện E01–E06 trong hai tài liệu protocol với analyzer, exporter, template, schema v2, cách app phát event và công cụ audit. Analyzer kiểm các bất biến có evidence trong manifest/event. Trạng thái background, checkpoint Doze đầu/giữa/cuối, điều kiện race E05, candidate và môi trường thiết bị cần evidence của owner và kiểm độc lập theo protocol. [Protocol cốt lõi](../../EXPERIMENT_PROTOCOL.md) · [Protocol chạy](../../../experiments/PROTOCOL.md) · [Schema](../../EVENT_SCHEMA.md).

## Đầu vào và provenance

| Nguồn | Artifact và cách sử dụng |
|---|---|
| SEM-24 / Done | [Exporter](../../../experiments/scripts/export_logs.py), [template](../../../experiments/RUN_MANIFEST_TEMPLATE.json), [CHECKS](../SEM-24/CHECKS.md). Tái sử dụng validator của exporter |
| SEM-26 / Done | [EVENT_SCHEMA](../../EVENT_SCHEMA.md), [API](../../API.md), [CHECKS](../SEM-26/CHECKS.md). Event 2.0.0 có 27 key |
| Protocol | [PROTOCOL 1.0.0](../../../experiments/PROTOCOL.md) và [EXPERIMENT_PROTOCOL](../../EXPERIMENT_PROTOCOL.md) |
| SEM-41 / snapshot đã pin | 12 cặp manifest/events canonical v2 tại commit `42ca000da1de2b7465851e1485fec2631f4b1a3c`, nhận lúc PR #29 còn Draft. CHECKS, PILOT_RESULTS, SCHEDULER_OBSERVER_AUDIT và EMULATOR_PLAN nguồn đều được pin/hash trong [INPUTS.json](INPUTS.json) |
| SEM-42 | Chưa nhận bộ manifest/events OPPO cho lần bàn giao này. Phân tích OPPO **Not run** |

Nguồn SEM-41 tại lúc nhận là Draft PR #29, PR này hiện đã merge vào main. Phạm vi bản sửa vẫn là 12 pilot lịch sử tại commit đã pin, giữ outcome/validity của snapshot đó. Các lượt đo lại đã có trên main được nhận riêng theo revision và evidence của batch tương ứng. [PR nguồn](https://github.com/ThanhTris/Seminar-IE307/pull/29).

Audit mới thu hồi qualification của 8 lượt từng VALID với `scheduler_observation_status=FAIL` và lý do `IN_WINDOW_JOB_DUMP_CAN_REEVALUATE_TIMERS`. `FINAL_VERIFICATION.json` của SEM-41 vẫn là snapshot lịch sử trước audit và đã được nguồn ghi là superseded. Index lần này dùng SCHEDULER_OBSERVER_AUDIT để truy vết việc thu hồi. [Audit collector](https://github.com/ThanhTris/Seminar-IE307/blob/42ca000da1de2b7465851e1485fec2631f4b1a3c/docs/evidence/SEM-41/SCHEDULER_OBSERVER_AUDIT.json).

PILOT_RESULTS tại revision đã pin có thêm 6 lượt chạy lại VALID và batch đo lại còn RUNNING. Bộ SEM-45 giữ nguyên cohort 12 lượt đã review tại `dec00b7`, cập nhật validity theo nguồn mới. Sáu lượt mới được liệt kê ngoài phạm vi tại `selection_scope.excluded_new_run_directories`; số 0 VALID trong CHECKS chỉ áp dụng cho 12 lượt được chọn. Khi nhận batch đo lại, cần pin commit và kiểm evidence riêng.

Build đo trong manifest nguồn có app commit `9e7e55b76c646ff113a152022cc23317a202e533`, server commit `c77772e426c00ae464240f00942f8368c638aaa8`, APK SHA-256 `bde050c084d655c66f9f1497c57900a7f0efc39e12a9da55110771926c3f2e23`, package `com.thanhtris.seminarie307`, version 0.1.0/1, SDK 24/37/37 và `candidate_gate_passed=false`. Config/provenance đầy đủ của từng nhóm được giữ trong report. Các epoch r2/r3 và epoch chưa biết được tách thành 7 nhóm. [analysis_report.json](analysis_report.json).

## Kết quả thực tế

| Case và mode | Tổng dòng | VALID/COMPLETED | Outcome của các lượt VALID/COMPLETED | INVALID được giữ |
|---|---|---|---|---|
| E01 PERIODIC | 3 | 0 | Không có | 3 |
| E03 PERIODIC | 4 | 0 | Không có | 4 |
| E04 PERIODIC | 3 | 0 | Không có | 3 |
| E06 HYBRID | 2 | 0 | Không có | 2 |
| Tổng | 12 | 0 | Không có | 12 |

Outcome lịch sử của toàn bộ 12 lượt gồm 5 SUCCESS, 5 TIMEOUT và 2 FAILURE, đều đi cùng validity INVALID. Event Android đều thiếu boot ID, nên analyzer giữ 12 dòng `UNCERTAIN_WINDOW`, `window_events_verified=false` và các metric/count trong cửa sổ chưa xác minh là null. Các raw event count toàn export và giá trị khai báo vẫn đọc được riêng. Mẫu số main bằng **0**, completion_rate main là **null**. [results.csv](../../../experiments/results.csv) · [summary.json](summary.json).

## Các phép kiểm đã chạy

Môi trường Windows, Python **3.12.14**, standard library và Ubuntu 24.04 qua WSL. TEMP/TMP/TMPDIR của tiến trình test Windows đặt vào `.local/sem45-temp`. Công cụ và validator có LF theo `.gitattributes` để hash byte ổn định qua checkout.

| Check | Expected | Actual | Kết quả |
|---|---|---|---|
| Unit/regression và tích hợp main | Giữ contract, correlation, timeout, clock, dataset, provenance và nhóm epoch | **160/160 test đạt trên Ubuntu**, gồm 72 SEM-45, 36 exporter và 52 test khác từ main. Windows đạt 72/72 SEM-45 | Pass |
| Nguồn pinned | Hash đúng cho 12 manifest, 12 JSONL và 4 evidence nguồn | Đọc Git object trực tiếp tại full commit, tất cả hash khớp index | Pass — dữ liệu pilot thật |
| Giá trị nguồn | Giữ manifest/events và kết quả giống đọc thư mục canonical | Toàn bộ 12 analysis khớp khi đọc export được trích nguyên byte, có cùng metadata epoch | Pass — offline |
| Tái lập | CSV/summary ổn định, report chỉ khác batch ID | Batch `windows` và `ubuntu` trong `.local/sem45-chain-review` cho CSV/summary giống từng byte, report khớp sau chuẩn hóa batch ID | Pass |
| Checkout Windows có CRLF | Có thể phục hồi byte LF đúng từ Git để so report | Bản checkout riêng với validator CRLF chỉ lệch `validator_sha256`; lấy lại LF từ Git thì report v0.5.0 khớp. Hướng dẫn PowerShell nằm trong ANALYSIS | Pass |
| Checksum artifact | CSV/summary/index/analyzer/validator khớp report | Hash kiểm trên byte file bàn giao | Pass |
| Dataset và mẫu số | Giữ 12 pilot, loại INVALID và toàn bộ pilot khỏi main | 0 VALID/COMPLETED, 12 INVALID, 7 nhóm, n_eligible main = 0; valid_completed_declared_outcomes rỗng ở cả 7 nhóm | Pass |
| Thu hồi qualification | Theo validity mới và giữ lịch sử đo | Tám qualification bị thu hồi; cả 12 dòng hiện INVALID. Event bytes/outcome/timing/count gốc được giữ | Pass |
| Hồi quy E04 | Chỉ công nhận phục hồi sau reconnect trên clock đã đối chiếu | Apply giây 7 trước reconnect phút 2 bị loại; apply sau reconnect đủ cửa sổ được nhận; thiếu clock/mốc hoặc sát bound là unverified; TIMEOUT đủ cửa sổ còn trong mẫu số | Pass — synthetic |
| Hồi quy E06 | Apply có work/fetch đúng target/correlation/thứ tự | Thiếu start/completed, sai request/work/attempt/target/status hoặc đảo thứ tự bị chặn; chuỗi đầy đủ được nhận; TIMEOUT chưa có apply vẫn giữ outcome | Pass — synthetic |
| E04 update ngoài khoảng offline | Kiểm đúng target với offset và uncertainty | Mốc server `00:03:01`, offset `+1 s`, reconnect Android `00:02:00`, apply `00:03:20` cho `E04_TARGET_UPDATE_OUTSIDE_OFFLINE`, `eligible=false`, latency rỗng và giữ `SUCCESS`. Update trước offline cũng bị loại. Update đã quy đổi nằm trọn trong offline được tính hợp lệ | Pass — synthetic |
| E04 update chưa xác minh | Loại khi thời điểm hoặc định danh update chưa đủ căn cứ | Khoảng sai số trùm mốc offline/reconnect, thiếu update đúng target hoặc nhiều update cùng target cho `E04_TARGET_UPDATE_TIME_UNVERIFIED` | Pass — synthetic |
| E06 skip mâu thuẫn send | Kiểm cùng update ID và target version | Skip cùng accepted, rejected hoặc unknown cho `E06_FAULT_SKIP_CONFLICTING_SEND` và mẫu số bằng 0. Ca chỉ skip và chuỗi periodic/fetch hợp lệ vẫn đủ điều kiện, send của update khác và lỗi trước khi gọi provider không tạo cờ mâu thuẫn | Pass — synthetic |
| E02 nối sender và worker | Chỉ tính apply có chuỗi tín hiệu đúng | Đổi `signal-demo-001` phía sender thành `unrelated-signal` cho `E02_PUSH_CHAIN_UNVERIFIED`, `n_eligible=0`, `n_complete=0`, outcome giữ `SUCCESS`. Sai update/version hoặc thiếu callback/enqueue/work cũng bị loại. Ca cùng tín hiệu hoàn chỉnh cho `n_complete=1`. TIMEOUT và provider FAILURE đủ cửa sổ giữ trong mẫu số | Pass — synthetic |
| E03 kiểm deep Doze và các pha | Xác minh deep IDLE, thứ tự và thời lượng từng đoạn | Ca ACTIVE và idle một phút trong cửa sổ 35 phút nhận `E03_DEEP_DOZE_NOT_CONFIRMED` và `E03_DOZE_PHASE_TOO_SHORT`, `n_eligible=0`, `n_complete=0`. Ca đủ 5/20/10 phút đạt ở PERIODIC và PUSH, TIMEOUT đủ điều kiện vẫn được giữ | Pass — synthetic |
| Boot/clock thiếu | Completion/duration/count window chưa biết là null, outcome khai báo giữ nguyên | 12 UNCERTAIN_WINDOW, latency và count cửa sổ rỗng | Pass |
| Fixture | Fixture giữ NOT_RUN và mẫu số 0 | CLI fixture đạt, nguồn fixture có nhãn riêng | Pass |
| Kiểm từ chối | Pilot bị chặn khi chọn main, legacy bị chặn, batch cũ không bị ghi đè | Các lệnh trả exit 2 với mã lỗi tương ứng | Pass |
| Syntax/tài liệu/whitespace | Python 3.9 syntax, link nội bộ hợp lệ, diff sạch | AST, link/fence/table và `git diff --check` được kiểm trước commit cuối | Pass |
| Snapshot và tài liệu nền | Metadata task và tài liệu SEM-19 hợp lệ | `update_task_snapshot.py --check` đạt 45 task; validator SEM-19 đạt 174 link nội bộ | Pass |
| Runtime main, OPPO và các phase | Có log/clock/evidence thật trước công bố kết quả | Chưa chạy các phép đo này trong SEM-45 | **Not run** |

Chi tiết máy kiểm và kết quả assertions được ghi trong [VERIFICATION.json](VERIFICATION.json). Lệnh tái lập nằm trong [ANALYSIS.md](../../../experiments/ANALYSIS.md). Suite đầy đủ chạy trên Ubuntu do test SEM-41 cần quyền tạo symlink. Các ca hồi quy E02/E03 là dữ liệu tổng hợp có nhãn.

v0.5.0 giữ các giá trị đo và source index của 12 pilot. CSV/summary/report đã được sinh lại với checksum mới. Một dòng E03 lịch sử có thêm cờ kiểm pha, cả 12 dòng vẫn INVALID.

## Phần thiếu, chưa rõ và chưa chắc chắn

| Phần | Tình trạng và ảnh hưởng | Nguồn cần bổ sung |
|---|---|---|
| Main emulator | 27 slot main trong plan nguồn còn NOT_RUN. CSV hiện chỉ chứa các run pilot đã có artifact | Vinh / SEM-41, candidate/profile SEM-37 |
| OPPO | Chưa nhận log/CHECKS OPPO E01/E02. So sánh emulator–OPPO và kết luận OEM **Not run** | Trí / SEM-42 |
| Boot ID event | Producer để null dù manifest có boot collector. Chưa xác minh được membership/timing từng event từ canonical input. Count window và completion để null | Producer/exporter và owner SEM-41/42, kèm evidence cùng boot |
| Clock liên máy | controlled=false, không có mẫu offset/drift đủ căn cứ. Latency server → Android để null | Owner run SEM-41/42 |
| Kết quả khai báo | Toàn bộ 12 lượt cũ INVALID sau audit collector, qualification trước đây bị thu hồi. Outcome giữ để truy vết; chưa có mẫu scheduler hợp lệ trong bộ này | Review source PR #29 và SEM-44 |
| E01 và batch đo lại | Các phiên E01 cũ INVALID. Nguồn có lượt chạy lại đạt 5 cycle/90 phút trong 6 lượt mới, nhưng các lượt mới nằm ngoài bộ chọn hiện tại và batch còn RUNNING | Vinh / SEM-41, nhận batch mới theo revision/evidence riêng |
| E03/E04 | E04 đã có guard reconnect với mốc Android UTC/boot/clock được đối chiếu, nhưng 12 pilot cũ thiếu điều kiện để dùng guard làm bằng chứng phục hồi. Summary vẫn whole-run, aggregation phase idle/offline chưa chạy | Owner run và SEM-44 khi cần biểu đồ theo phase |
| Firebase/E02/E05/E06 | Profile đo FIREBASE_NOT_CONFIGURED. E06 có event deliberate skip, callback/token/push thật và hybrid trên profile Firebase **Not run**. E02/E05 chưa có pilot trong bộ này | Owner runtime và SEM-41/42 |
| Candidate | Manifest nguồn gate=false, release main vẫn NOT_READY/NOT_BUILT tại nền cập nhật. Hash APK đo pilot đã có trong manifest nguồn, freeze/bàn giao main còn thiếu | Trung / SEM-37, SEM-52 |
| DB writes và năng lượng | Chưa instrument số write SQL/items, `db_write_count=null`. Chưa có phép đo mAh | Owner instrumentation/run khi có phép đo tương ứng |
| Review độc lập | Main đã có audit SEM-44 theo bản producer `1a0c667`. Trí đã kiểm v0.4.0 trên `0faf74d`. Bản v0.5.0 đang ở Draft để kiểm lại E02/E03 và checksum | Tâm / SEM-44 và Trí / reviewer |

Các lý do INVALID cũ vẫn được giữ, gồm `89b884` chưa bắt đầu measurement, `760217` và `c12a28` có baseline payload mismatch, `0d277e` bị cắt cửa sổ post-idle. Audit scheduler bổ sung lý do thu hồi 8 qualification và giữ đủ 12 lượt INVALID. Outcome gốc được giữ, kể cả SUCCESS ở lượt INVALID. Epoch được lấy từ PILOT_RESULTS đã pin và đối chiếu theo artifact_directory. [Đối chiếu nguồn](https://github.com/ThanhTris/Seminar-IE307/blob/42ca000da1de2b7465851e1485fec2631f4b1a3c/docs/evidence/SEM-41/CHECKS.md).

## Đầu ra bàn giao và điều kiện cập nhật

- [analyze.py](../../../experiments/scripts/analyze.py), [tests](../../../experiments/scripts/tests/test_analyze.py) và [hướng dẫn](../../../experiments/ANALYSIS.md).
- [results.csv](../../../experiments/results.csv), [INPUTS.json](INPUTS.json), [summary.json](summary.json), [analysis_report.json](analysis_report.json) và [VERIFICATION.json](VERIFICATION.json).
- SEM-43/44/48/50 nhận bộ pilot/INVALID cùng provenance/giới hạn ở đây để kiểm pipeline và truy vết. Bộ này có 0 mẫu scheduler hợp lệ sau thu hồi qualification. Các lượt đo lại được tiếp nhận riêng khi có revision/evidence phù hợp.
- Khi nhận main/OPPO hoặc nguồn sửa kết quả, cập nhật index theo đúng commit, chạy lại analyzer, kiểm clock/window/mẫu số rồi cập nhật artifact và CHECKS. Bản bàn giao này được đưa lên Draft PR để Tuấn review.
