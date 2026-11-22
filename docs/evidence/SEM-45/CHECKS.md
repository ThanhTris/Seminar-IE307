# SEM-45 — Kiểm parser và bàn giao kết quả offline

- Người thực hiện Tuấn (`mtuan2491`), cập nhật **21/11/2026 (UTC+7)** theo review mốc mở cửa sổ E02 và dữ liệu OPPO.
- Nhánh `codex/SEM-45-log-parser` nhận main `aa425c3` bằng merge commit `adc5ac8`, gồm dữ liệu PR #35 và provenance PR #37.
- **Đầu ra SEM-45 v0.7.0** gồm parser, CSV của **23 lượt pilot**, index nguồn, summary/report và hướng dẫn tái lập. Manifest nguồn ghi **10 VALID/COMPLETED và 13 INVALID**. Trạng thái Project vẫn In Progress.
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
| 3. Bàn giao | Rà protocol E01–E06, tái sinh artifact v0.5.0 và kiểm Windows/Ubuntu | `a270a9b` |

Đã đối chiếu điều kiện E01–E06 trong hai tài liệu protocol với analyzer, exporter, template, schema v2, cách app phát event và công cụ audit. Analyzer kiểm các bất biến có evidence trong manifest/event. Trạng thái background, checkpoint Doze đầu/giữa/cuối, điều kiện race E05, candidate và môi trường thiết bị cần evidence của owner và kiểm độc lập theo protocol. [Protocol cốt lõi](../../EXPERIMENT_PROTOCOL.md) · [Protocol chạy](../../../experiments/PROTOCOL.md) · [Schema](../../EVENT_SCHEMA.md).

## Sửa theo review thứ tự clock trên `a270a9b`

| Bước | Kết quả | Commit |
|---|---|---|
| 1. E02 | Từ offset và sai số, phát hiện callback/apply chắc chắn trước target commit. Thêm 3 test | `6877b00` |
| 2. E03 | Yêu cầu commit đúng target nằm trong pha deep Doze theo clock Android đã đối chiếu. Thêm 4 test | `f844bdb` |
| 3. Bàn giao | Tái sinh artifact v0.6.0 và kiểm Windows/Ubuntu | `741e375` |

## Sửa theo review ngày 21/11

| Bước | Kết quả | Commit |
|---|---|---|
| 1. E02 | So mốc mở cửa sổ với target commit đã quy đổi, thêm hai test hồi quy và đối chứng | `9cf1156` |
| 2. Pilot E01 | Ghim 23 input và nguồn PR từng run, tái đếm elapsed, kiểm tách nhóm route/build | `d550ba1` |
| 3. Bàn giao | Tái sinh CSV/summary/report/verification v0.7.0 và kiểm chéo nền tảng | Commit chứa CHECKS này, tra `git log -1 -- docs/evidence/SEM-45/CHECKS.md` |

## Đầu vào và provenance

| Nguồn | Artifact và cách sử dụng |
|---|---|
| SEM-24 / Done | [Exporter](../../../experiments/scripts/export_logs.py), [template](../../../experiments/RUN_MANIFEST_TEMPLATE.json), [CHECKS](../SEM-24/CHECKS.md). Tái sử dụng validator của exporter |
| SEM-26 / Done | [EVENT_SCHEMA](../../EVENT_SCHEMA.md), [API](../../API.md), [CHECKS](../SEM-26/CHECKS.md). Event 2.0.0 có 27 key |
| Protocol | [PROTOCOL 1.0.0](../../../experiments/PROTOCOL.md) và [EXPERIMENT_PROTOCOL](../../EXPERIMENT_PROTOCOL.md) |
| SEM-41 / PR #29 | 20 cặp manifest/events trong snapshot đã merge `007a1aa`, gồm 12 run lịch sử và 8 run đo lại. [PILOT_RESULTS](../SEM-41/PILOT_RESULTS.json) |
| SEM-42 / PR #35 | Hai pilot OPPO và một pilot emulator E01, merge tại `3f0871c`. Manifest, canonical events và export reports đều được ghim SHA-256. [CHECKS SEM-42](../SEM-42/CHECKS.md) |
| Provenance APK / PR #37 | APK pilot `814347F09EF9A61331910D7C4267FEF827A4749377F3AF53AE21FBB882EBAF5B`, app/server `76fece00110e0dba83c59b3e56bdabd2b4b7934e`. [Build manifest](../../../release/BUILD_MANIFEST.json) |

Snapshot nguồn chung là `aa425c33bdee034afcc552ebc390cae6780f6dbe`. Index ghi `source_pr` và `source_merge_commit` cho từng run và mỗi evidence. Đã đối chiếu byte manifest/events với merge commit của PR xuất bản. [INPUTS.json](INPUTS.json).

Audit mới thu hồi qualification của 8 lượt từng VALID với `scheduler_observation_status=FAIL` và lý do `IN_WINDOW_JOB_DUMP_CAN_REEVALUATE_TIMERS`. `FINAL_VERIFICATION.json` của SEM-41 vẫn là snapshot lịch sử trước audit và đã được nguồn ghi là superseded. Index lần này dùng SCHEDULER_OBSERVER_AUDIT để truy vết việc thu hồi. [Audit collector](https://github.com/ThanhTris/Seminar-IE307/blob/42ca000da1de2b7465851e1485fec2631f4b1a3c/docs/evidence/SEM-41/SCHEDULER_OBSERVER_AUDIT.json).

Ba run PR #35 khớp APK pilot `814347F…`. Bản debug dưới `release/` có SHA `DBAAD…`, còn loạt SEM-41 cũ có manifest ghi `BDE050…`. `group_id` bao gồm toàn bộ build, cấu hình thiết bị và `server_route`, cùng store epoch khi có. Các run `EMULATOR_HOST_GATEWAY`, `EMULATOR_HOST_HTTP` và `ADB_REVERSE` thuộc các nhóm riêng. [analysis_report.json](analysis_report.json) · [Provenance PR #37](https://github.com/ThanhTris/Seminar-IE307/pull/37).

## Kết quả thực tế

| Case và mode | Tổng dòng | VALID/COMPLETED | Outcome của các lượt VALID/COMPLETED | INVALID được giữ |
|---|---|---|---|---|
| E01 PERIODIC | 7 | 3 | 3 SUCCESS | 4 |
| E03 PERIODIC | 6 | 2 | 2 SUCCESS | 4 |
| E04 PERIODIC | 6 | 3 | 3 SUCCESS | 3 |
| E06 HYBRID | 4 | 2 | 2 SUCCESS | 2 |
| Tổng | 23 | 10 | 10 SUCCESS | 13 |

| Run E01 mới | Route / nguồn | Kết quả theo manifest | Tái đếm theo Android elapsed | Apply target theo elapsed từ đầu lượt |
|---|---|---|---|---|
| `run-sem42-oppo-e01-03` | `ADB_REVERSE`, nguồn USB | `COMPLETED / SUCCESS / VALID` | 5 chu kỳ trong 90 phút | v5 tại `930021 ms` |
| `run-sem42-oppo-e01-02` | `ADB_REVERSE`, nguồn USB | `ABORTED / UNKNOWN / INVALID` | Null vì thiếu mốc mở và app lên tiền cảnh | Null |
| `run-sem41-pilot-e01-1-20261120-8d5816` | `EMULATOR_HOST_GATEWAY` | `COMPLETED / SUCCESS / VALID` | 2 chu kỳ, dưới mục tiêu 3 | v3 tại `2194372 ms` |

Chỉ đếm `work_started` PERIODIC, attempt 0 và request ID riêng trong cửa sổ elapsed. Các số tái đếm và mốc apply theo elapsed nằm trong các cột `pilot_elapsed_*_unverified_boot`. Manifest và event PR #35 thiếu boot ID. Cả 23 dòng giữ `UNCERTAIN_WINDOW` và `window_events_verified=false`. Số chu kỳ đã xác minh cùng boot và latency liên máy để null. Có **10 nhóm**, mẫu số main bằng **0** và completion_rate main là **null**. [results.csv](../../../experiments/results.csv) · [summary.json](summary.json).

## Các phép kiểm đã chạy

Môi trường Windows, Python **3.12.14**, standard library và Ubuntu 24.04 qua WSL. TEMP/TMP/TMPDIR của tiến trình test Windows đặt vào `.local/sem45-temp`. Công cụ và validator có LF theo `.gitattributes` để hash byte ổn định qua checkout.

| Check | Expected | Actual | Kết quả |
|---|---|---|---|
| Unit/regression và tích hợp main | Giữ contract, correlation, timeout, clock, dataset, provenance và nhóm epoch | **170/170 test đạt trên Ubuntu** và **82/82 test analyzer trên Windows** | Pass |
| Nguồn pinned | Hash đúng cho 23 manifest, 23 JSONL và các evidence nguồn | Đọc Git object từ snapshot main, hash khớp index. Manifest và event khớp byte với merge commit của PR nguồn | Pass — dữ liệu pilot thật |
| Giá trị nguồn | Giữ manifest/events và kết quả giống đọc thư mục canonical | Toàn bộ 23 analysis khớp khi đọc export được trích nguyên byte, có cùng metadata epoch | Pass — offline |
| Tái lập | CSV/summary ổn định, report chỉ khác batch ID | Batch `windows` và `ubuntu` trong `.local/sem45-oppo-review` cho CSV/summary giống từng byte, report khớp sau chuẩn hóa batch ID | Pass |
| Checkout Windows có CRLF | Có thể phục hồi byte LF đúng từ Git để so report | Bản checkout riêng v0.5.0 với validator CRLF chỉ lệch `validator_sha256`. Hướng dẫn lấy byte LF nằm trong ANALYSIS | Pass ở v0.5.0 |
| Checksum artifact | CSV/summary/index/analyzer/validator khớp report | Hash kiểm trên byte file bàn giao | Pass |
| Dataset và mẫu số | Giữ đủ pilot cùng trạng thái nguồn và loại khỏi main | 23 pilot, 10 VALID/COMPLETED và 13 INVALID, 10 nhóm, n_eligible main = 0 | Pass |
| Chu kỳ và nhóm E01 | Tái đếm theo PERIODIC attempt 0 và request, audit route/build | OPPO hoàn tất 5, emulator gateway 2, OPPO hủy null. Route HTTP/gateway, APK và nguồn điện ảnh hưởng group ID | Pass |
| Thu hồi qualification | Theo validity mới và giữ lịch sử đo | Tám qualification bị thu hồi trong loạt cũ. Cả 12 run lịch sử vẫn INVALID và giữ outcome gốc | Pass |
| Hồi quy E04 | Chỉ công nhận phục hồi sau reconnect trên clock đã đối chiếu | Apply giây 7 trước reconnect phút 2 bị loại; apply sau reconnect đủ cửa sổ được nhận; thiếu clock/mốc hoặc sát bound là unverified; TIMEOUT đủ cửa sổ còn trong mẫu số | Pass — synthetic |
| Hồi quy E06 | Apply có work/fetch đúng target/correlation/thứ tự | Thiếu start/completed, sai request/work/attempt/target/status hoặc đảo thứ tự bị chặn; chuỗi đầy đủ được nhận; TIMEOUT chưa có apply vẫn giữ outcome | Pass — synthetic |
| E04 update ngoài khoảng offline | Kiểm đúng target với offset và uncertainty | Mốc server `00:03:01`, offset `+1 s`, reconnect Android `00:02:00`, apply `00:03:20` cho `E04_TARGET_UPDATE_OUTSIDE_OFFLINE`, `eligible=false`, latency rỗng và giữ `SUCCESS`. Update trước offline cũng bị loại. Update đã quy đổi nằm trọn trong offline được tính hợp lệ | Pass — synthetic |
| E04 update chưa xác minh | Loại khi thời điểm hoặc định danh update chưa đủ căn cứ | Khoảng sai số trùm mốc offline/reconnect, thiếu update đúng target hoặc nhiều update cùng target cho `E04_TARGET_UPDATE_TIME_UNVERIFIED` | Pass — synthetic |
| E06 skip mâu thuẫn send | Kiểm cùng update ID và target version | Skip cùng accepted, rejected hoặc unknown cho `E06_FAULT_SKIP_CONFLICTING_SEND` và mẫu số bằng 0. Ca chỉ skip và chuỗi periodic/fetch hợp lệ vẫn đủ điều kiện, send của update khác và lỗi trước khi gọi provider không tạo cờ mâu thuẫn | Pass — synthetic |
| E02 nối sender và worker | Chỉ tính apply có chuỗi tín hiệu đúng | Đổi `signal-demo-001` phía sender thành `unrelated-signal` cho `E02_PUSH_CHAIN_UNVERIFIED`, `n_eligible=0`, `n_complete=0`, outcome giữ `SUCCESS`. Sai update/version hoặc thiếu callback/enqueue/work cũng bị loại. Ca cùng tín hiệu hoàn chỉnh cho `n_complete=1`. TIMEOUT và provider FAILURE đủ cửa sổ giữ trong mẫu số | Pass — synthetic |
| E03 kiểm deep Doze và các pha | Xác minh deep IDLE, thứ tự và thời lượng từng đoạn | Ca ACTIVE và idle một phút trong cửa sổ 35 phút nhận `E03_DEEP_DOZE_NOT_CONFIRMED` và `E03_DOZE_PHASE_TOO_SHORT`, `n_eligible=0`, `n_complete=0`. Ca đủ 5/20/10 phút đạt ở PERIODIC và PUSH, TIMEOUT đủ điều kiện vẫn được giữ | Pass — synthetic |
| E02 thứ tự liên máy | Target commit đi trước callback/apply khi thứ tự xác định được | Offset +1 s, ±6 ms, commit quy đổi `00:01:00` sau callback `00:00:02` và apply `00:00:07` nhận `E02_PUSH_CLOCK_ORDER_CONFLICT`, `n_eligible=0`, `n_complete=0`, outcome `SUCCESS` giữ nguyên. Đối chứng có commit đúng thứ tự, phản hồi FCM ghi muộn và timeout hợp lệ đều đạt | Pass — synthetic |
| E03 thời điểm commit target và Doze | Target commit có khoảng sai số nằm trong deep Doze | Offset +1 s, ±6 ms, commit quy đổi `00:01:00` và apply `00:02:00` ở baseline nhận `E03_TARGET_UPDATE_OUTSIDE_DOZE`, `n_eligible=0`, `n_complete=0`. Update sau khi vào `IDLE` đạt. Khoảng chồng ranh giới hoặc clock chưa đối chiếu được nhận cờ chưa xác minh | Pass — synthetic |
| E02 mốc mở cửa sổ | Cửa sổ bắt đầu theo target commit đã đối chiếu clock | Mốc mở `00:00:00` lệch commit quy đổi `00:01:00` ±6 ms nhận `E02_WINDOW_START_CLOCK_CONFLICT` và `n_eligible=0`. Outcome `TIMEOUT` và late apply theo cửa sổ khai báo được giữ. Ca đúng mốc trong khoảng sai số với timeout thật vẫn `eligible=true` | Pass — synthetic |
| Boot/clock thiếu | Giữ metric chưa xác minh là null | 23 UNCERTAIN_WINDOW. Tái đếm E01 chỉ xuất ở cột descriptive riêng; latency liên máy và count đã xác minh theo boot để rỗng | Pass |
| Fixture | Fixture giữ NOT_RUN và mẫu số 0 | CLI fixture đạt, nguồn fixture có nhãn riêng | Pass |
| Kiểm từ chối | Pilot bị chặn khi chọn main, legacy bị chặn, batch cũ không bị ghi đè | Các lệnh trả exit 2 với mã lỗi tương ứng | Pass |
| Syntax/tài liệu/whitespace | Python 3.9 syntax, link nội bộ hợp lệ, diff sạch | AST, link/fence/table và `git diff --check` được kiểm trước commit cuối | Pass |
| Snapshot và tài liệu nền | Metadata task và tài liệu SEM-19 hợp lệ | `update_task_snapshot.py --check` đạt 45 task; validator SEM-19 đạt 174 link nội bộ | Pass |
| Runtime main, OPPO E02 và các phase | Có log/clock/evidence thật trước công bố kết quả | Chưa có run main trong bộ phân tích. OPPO E02 và đo riêng theo phase vẫn chưa chạy | **Not run** |

Chi tiết máy kiểm và kết quả assertions được ghi trong [VERIFICATION.json](VERIFICATION.json). Lệnh tái lập nằm trong [ANALYSIS.md](../../../experiments/ANALYSIS.md). Suite đầy đủ chạy trên Ubuntu do test SEM-41 cần quyền tạo symlink. Các ca hồi quy E02/E03 là dữ liệu tổng hợp có nhãn.

v0.7.0 giữ dữ liệu nguồn theo snapshot main và tái sinh CSV/summary/report từ parser cập nhật. Các giá trị được khai báo và kết quả tái đếm nằm ở cột riêng để đối chiếu.

## Phần thiếu, chưa rõ và chưa chắc chắn

| Phần | Tình trạng và ảnh hưởng | Nguồn cần bổ sung |
|---|---|---|
| Main emulator | 27 slot main trong plan nguồn còn NOT_RUN. CSV hiện chỉ chứa các run pilot đã có artifact | Vinh / SEM-41, candidate/profile SEM-37 |
| OPPO | Có hai pilot E01, gồm một lượt hoàn tất và một lượt bị hủy. OPPO E02 **Not run**. Khác route, nguồn điện và thiết bị giới hạn việc so sánh kết quả | Trí / SEM-42 |
| Boot ID event | Producer để null dù manifest có boot collector. Chưa xác minh được membership/timing từng event từ canonical input. Count window và completion để null | Producer/exporter và owner SEM-41/42, kèm evidence cùng boot |
| Clock liên máy | controlled=false, không có mẫu offset/drift đủ căn cứ. Latency server → Android để null | Owner run SEM-41/42 |
| Kết quả khai báo | 12 lượt cũ INVALID sau audit collector, outcome giữ để truy vết. Tám lượt chạy lại của SEM-41 và hai lượt hoàn tất PR #35 ghi VALID cho pilot | Review source PR #29/#35 và SEM-44 |
| Thiếu boot và clock | Kết quả E01 descriptive dựa trên Android elapsed khai báo. Thiếu boot cùng phiên nên cột xác minh vẫn để trống. Cả ba run mới giữ `candidate_gate_passed=false` và clock uncontrolled | Owner run khi bổ sung chứng cứ |
| E03/E04 | E04 đã có guard reconnect với mốc Android UTC/boot/clock được đối chiếu, nhưng 12 pilot cũ thiếu điều kiện để dùng guard làm bằng chứng phục hồi. Summary vẫn whole-run, aggregation phase idle/offline chưa chạy | Owner run và SEM-44 khi cần biểu đồ theo phase |
| Firebase/E02/E05/E06 | Profile đo FIREBASE_NOT_CONFIGURED. E06 có event deliberate skip, callback/token/push thật và hybrid trên profile Firebase **Not run**. E02/E05 chưa có pilot trong bộ này | Owner runtime và SEM-41/42 |
| Candidate | Manifest nguồn gate=false. Release có build debug `DBAAD…` và provenance riêng của APK pilot `814347F…`. Gate candidate cho main vẫn chưa đạt | Trung / SEM-37, SEM-52 |
| DB writes và năng lượng | Chưa instrument số write SQL/items, `db_write_count=null`. Chưa có phép đo mAh | Owner instrumentation/run khi có phép đo tương ứng |
| Review độc lập | Main đã có audit SEM-44 theo bản producer `1a0c667`. Trí đã kiểm v0.6.0 trên `741e375`. Bản v0.7.0 ở Draft để kiểm mốc mở cửa sổ E02 và dữ liệu mới | Tâm / SEM-44 và Trí / reviewer |

Các lý do INVALID cũ vẫn được giữ, gồm `89b884` chưa bắt đầu measurement, `760217` và `c12a28` có baseline payload mismatch, `0d277e` bị cắt cửa sổ post-idle. Audit scheduler bổ sung lý do thu hồi 8 qualification và giữ đủ 12 lượt INVALID. Outcome gốc được giữ, kể cả SUCCESS ở lượt INVALID. Epoch được lấy từ PILOT_RESULTS đã pin và đối chiếu theo artifact_directory. [Đối chiếu nguồn](https://github.com/ThanhTris/Seminar-IE307/blob/42ca000da1de2b7465851e1485fec2631f4b1a3c/docs/evidence/SEM-41/CHECKS.md).

## Đầu ra bàn giao và điều kiện cập nhật

- [analyze.py](../../../experiments/scripts/analyze.py), [tests](../../../experiments/scripts/tests/test_analyze.py) và [hướng dẫn](../../../experiments/ANALYSIS.md).
- [results.csv](../../../experiments/results.csv), [INPUTS.json](INPUTS.json), [summary.json](summary.json), [analysis_report.json](analysis_report.json) và [VERIFICATION.json](VERIFICATION.json).
- SEM-43 và SEM-48 có bộ CSV/summary mới để cập nhật SUMMARY và biểu đồ theo route/build. SEM-50 có thể dẫn trực tiếp [manifest OPPO run-03](../../../experiments/pilots/run-sem42-oppo-e01-03/manifest.json) cùng nhãn pilot, tuyến USB và giới hạn clock/boot.
- Khi nhận main hoặc nguồn sửa kết quả, cập nhật index theo đúng commit, chạy lại analyzer, kiểm clock/window/mẫu số rồi cập nhật artifact và CHECKS. Bản bàn giao này được đưa lên Draft PR để review.
