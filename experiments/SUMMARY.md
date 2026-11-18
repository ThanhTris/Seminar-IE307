# SEM-43 — Tổng hợp evidence thực nghiệm

**Snapshot ngày 16/11/2026 (UTC+7), main `007a1aa31d02d7af47570f4cf7b60a7ed8135a33`.** PR [SEM-41 #29](https://github.com/ThanhTris/Seminar-IE307/pull/29) đã merge. Đã có **8 pilot mới được SEM-41 ghi VALID/SUCCESS**, nhưng **chưa có run main** trên emulator hoặc OPPO. Tài liệu này chốt những quan sát có thể dùng từ snapshot hiện hành và ghi rõ phần NOT_RUN; không chứng nhận đã hoàn tất thực nghiệm E01–E06 trên hai máy.

[EVIDENCE_INDEX.json](../docs/evidence/SEM-43/EVIDENCE_INDEX.json) ghim commit và SHA-256 của nguồn, 20 lần thử SEM-41, hai pilot legacy và ba control development. Đây là sổ nguồn cho SUMMARY, không thay parser SEM-45 hoặc kiểm độc lập SEM-44. [CHECKS SEM-43](../docs/evidence/SEM-43/CHECKS.md) ghi kiểm chứng và bàn giao.

## 1. Đầu vào đã nhận và giới hạn snapshot

| Nguồn | Artifact/phiên bản đã đối chiếu | Kết luận sử dụng |
|---|---|---|
| SEM-41 | [PILOT_RESULTS](../docs/evidence/SEM-41/PILOT_RESULTS.json), [CHECKS](../docs/evidence/SEM-41/CHECKS.md), [kiểm cuối](../docs/evidence/SEM-41/REQUALIFICATION_VERIFICATION.json) | 20 lần thử: 8 VALID/SUCCESS mới, 12 INVALID cũ. Chỉ mô tả pilot theo build/config; 27 main slot NOT_RUN |
| SEM-42 | [Yêu cầu OPPO](../tasks/backlog/SEM-42.md), [lịch 6 main slot](RUN_SCHEDULE.md#5-main-oppo-và-dự-phòng--07112026) | Chưa nhận manifest/events hoặc CHECKS OPPO; không có đối chiếu OEM |
| SEM-44 | [AUDIT](AUDIT.md), [AUDIT_RESULTS](AUDIT_RESULTS.md), [CHECKS](../docs/evidence/SEM-44/CHECKS.md) | Báo cáo lịch sử 03/11 ghi NOT_RUN, 0 main run/0 CSV row. Chưa kiểm độc lập bộ pilot mới hoặc tập main; không dùng báo cáo cũ để phủ nhận pilot vừa nhận |
| SEM-45 | [Draft PR #30](https://github.com/ThanhTris/Seminar-IE307/pull/30), head `1a0c667c93391553cd08f054407d7eb04be2d4ef` | Chưa merge vào snapshot main. CSV trong PR có 12 pilot cũ, 0 VALID/12 INVALID; không chứa 8 pilot mới |
| SEM-37 | [Candidate manifest](../release/CANDIDATE_MANIFEST.json), app `9e7e55b`, server `c77772e` | `NOT_READY`, gate false, APK freeze chưa bàn giao. Follow-up unit test đã đạt [32/32](../docs/evidence/SEM-41/UNIT_FOLLOWUP.json); lý do build/test cũ trong release manifest không phải trạng thái kiểm mới nhất |

CSV đã xem ở [revision SEM-45 được ghim](https://github.com/ThanhTris/Seminar-IE307/blob/1a0c667c93391553cd08f054407d7eb04be2d4ef/experiments/results.csv), cùng [INPUTS](https://github.com/ThanhTris/Seminar-IE307/blob/1a0c667c93391553cd08f054407d7eb04be2d4ef/docs/evidence/SEM-45/INPUTS.json) và [CHECKS](https://github.com/ThanhTris/Seminar-IE307/blob/1a0c667c93391553cd08f054407d7eb04be2d4ef/docs/evidence/SEM-45/CHECKS.md). Bộ đó ghim nguồn SEM-41 tại `42ca000`, trước khi đóng cả batch r6; không đại diện inventory hiện hành đã có 20 lần thử. Không sao chép hoặc tự sửa CSV của owner SEM-45 trong task này.

## 2. Tập main: mẫu còn thiếu

Theo [protocol](PROTOCOL.md), [ma trận emulator](plans/SEM-41/EMULATOR_PLAN.json) và [định mức hai máy](RUN_SCHEDULE.md#2-ngân-sách-quan-sát-tối-thiểu):

| Case / thiết bị / mode | Số main slot dự kiến | Window mỗi slot | Main artifacts đã nhận | Trạng thái |
|---|---:|---|---:|---|
| E01 / emulator / PERIODIC | 1 | 90 phút | 0 | NOT_RUN |
| E01 / OPPO / PERIODIC | 1 | 90 phút | 0 | NOT_RUN |
| E02 / emulator / PUSH | 5 | 120 giây | 0 | NOT_RUN |
| E02 / OPPO / PUSH | 5 | 120 giây | 0 | NOT_RUN |
| E03 / emulator / PERIODIC | 2 | 5 baseline + 20 Doze + 10 sau thoát | 0 | NOT_RUN |
| E03 / emulator / PUSH | 2 | 5 baseline + 20 Doze + 10 sau thoát | 0 | NOT_RUN |
| E04 / emulator / PERIODIC | 3 | 2 offline + 30 sau nối lại | 0 | NOT_RUN |
| E04 / emulator / PUSH | 3 | 2 offline + 5 sau nối lại | 0 | NOT_RUN |
| E05 duplicate / emulator / PUSH | 3 | 15 phút | 0 | NOT_RUN |
| E05 stale hint / emulator / PUSH | 3 | 15 phút | 0 | NOT_RUN |
| E05 signal khi worker chạy / emulator / PUSH | 3 | 15 phút | 0 | NOT_RUN |
| E06 / emulator / HYBRID | 2 | 45 phút | 0 | NOT_RUN |
| **Tổng kế hoạch** | **33** | **682 phút, chưa tính setup/pilot** | **0** | **NOT_RUN** |

Main có **n_complete=0, n_total=0**; completion rate, median và min–max đều **N/A/null**. 33 là số slot kế hoạch, không phải mẫu số của tỷ lệ thành công đã đo. Không báo 0% thất bại hoặc 8/33 hoàn thành từ các pilot. Duyệt manifest theo `run_phase`, không theo tên thư mục: hai run trong `experiments/runs/` hiện là pilot legacy SEM-29.

## 3. Pilot SEM-41: nhận dạng build và cấu hình

Tám run ở bảng dưới cùng app **`9e7e55b76c646ff113a152022cc23317a202e533`**, server **`c77772e426c00ae464240f00942f8368c638aaa8`**, APK SHA-256 **`bde050c084d655c66f9f1497c57900a7f0efc39e12a9da55110771926c3f2e23`**, schema/API 2.0.0, protocol 1.0.0, `run_phase=pilot`, `data_kind=OBSERVED`, candidate gate false. Không dùng commit merge tài liệu thay source APK đã đo.

Thiết bị `emulator-main`: Google `sdk_gphone16k_arm64`, Android 17/API 37, ARM64, page size 16384, Play services 26.43.30. Interval/flex 15 phút, policy UPDATE, network constraint CONNECTED; baseline màn hình ON, Battery Saver false, pin 100%/không cấp nguồn theo manifest. `battery_optimization=null` là chưa có giá trị, không phải xác nhận đã tắt tối ưu pin. Profile **FIREBASE_NOT_CONFIGURED**.

Observer `db98fa8d275c3ca2d10895daa61f00bf53f59cd7` không dump scheduler trong window; review helper `7ce599d52ba5035bbd62f9d1045ee72bf71f0ba2` bổ sung kiểm E04/cleanup. Retained store epoch `pilots-20261115-r3`, không seed lại version/payload. Giữ từng nhóm **case/device/mode/build/config/phase/intervention/epoch/observer**; E03 force-idle và E06 deliberate skip mang nhãn INJECTED. Không gộp chúng thành baseline tự nhiên E01 hoặc thành các trial độc lập giữa thiết bị.

### Registry run hợp lệ

Mỗi link ở cột run mở manifest có full run_id/build; cột log/audit nối tới event và kiểm producer. Duration là thời lượng **cửa sổ quan sát từ collector**, không phải latency đồng bộ. Cycle là `work_started` PERIODIC mới trong window sau khi loại setup.

| Case / run | Log / kiểm producer | Duration (ms) | Cache trước→sau; target | Cycle | Outcome |
|---|---|---:|---|---:|---|
| [E01:1 / 575a7a](pilots/run-sem41-pilot-e01-1-20261115-575a7a/manifest.json) | [events](pilots/run-sem41-pilot-e01-1-20261115-575a7a/events.jsonl) · [audit](pilots/run-sem41-pilot-e01-1-20261115-575a7a/audit.json) | 5,400,720 | 15→16; V=16 | 5 | SUCCESS |
| [E03:1 / dc9cc9](pilots/run-sem41-pilot-e03-1-20261115-dc9cc9/manifest.json) | [events](pilots/run-sem41-pilot-e03-1-20261115-dc9cc9/events.jsonl) · [audit](pilots/run-sem41-pilot-e03-1-20261115-dc9cc9/audit.json) | 2,103,830 | 16→17; V=17 | 1 | SUCCESS |
| [E03:2 / 7f63e0](pilots/run-sem41-pilot-e03-2-20261115-7f63e0/manifest.json) | [events](pilots/run-sem41-pilot-e03-2-20261115-7f63e0/events.jsonl) · [audit](pilots/run-sem41-pilot-e03-2-20261115-7f63e0/audit.json) | 2,103,090 | 17→18; V=18 | 1 | SUCCESS |
| [E04:1 / cda576](pilots/run-sem41-pilot-e04-1-20261115-cda576/manifest.json) | [events](pilots/run-sem41-pilot-e04-1-20261115-cda576/events.jsonl) · [audit](pilots/run-sem41-pilot-e04-1-20261115-cda576/audit.json) | 1,931,840 | 18→19; V=19 | 2 | SUCCESS |
| [E04:2 / 3bde4f](pilots/run-sem41-pilot-e04-2-20261115-3bde4f/manifest.json) | [events](pilots/run-sem41-pilot-e04-2-20261115-3bde4f/events.jsonl) · [audit](pilots/run-sem41-pilot-e04-2-20261115-3bde4f/audit.json) | 1,928,540 | 19→20; V=20 | 1 | SUCCESS |
| [E04:3 / 54c1a9](pilots/run-sem41-pilot-e04-3-20261115-54c1a9/manifest.json) | [events](pilots/run-sem41-pilot-e04-3-20261115-54c1a9/events.jsonl) · [audit](pilots/run-sem41-pilot-e04-3-20261115-54c1a9/audit.json) | 1,928,690 | 20→21; V=21 | 1 | SUCCESS |
| [E06:1 / aa16ca](pilots/run-sem41-pilot-e06-1-20261116-aa16ca/manifest.json) | [events](pilots/run-sem41-pilot-e06-1-20261116-aa16ca/events.jsonl) · [audit](pilots/run-sem41-pilot-e06-1-20261116-aa16ca/audit.json) | 2,700,870 | 21→22; V=22 | 2 | SUCCESS |
| [E06:2 / 8f734c](pilots/run-sem41-pilot-e06-2-20261116-8f734c/manifest.json) | [events](pilots/run-sem41-pilot-e06-2-20261116-8f734c/events.jsonl) · [audit](pilots/run-sem41-pilot-e06-2-20261116-8f734c/audit.json) | 2,700,670 | 22→23; V=23 | 2 | SUCCESS |

Đây là **8 outcome SUCCESS do producer review xác nhận** trong 8 pilot hợp lệ mới, không phải tỷ lệ đảm bảo thành công chung. Nhóm E01 có 1/1 run, E03 2/2, E04 3/3, E06 2/2 ghi SUCCESS; mẫu nhỏ, thứ tự tuần tự và cùng một emulator. Không dùng cycle trong một run làm nhiều run độc lập. [Cleanup](../docs/evidence/SEM-41/REQUALIFICATION_DEVICE_CLEANUP.json) đạt, không còn sync work active/server riêng; [host continuity](../docs/evidence/SEM-41/REQUALIFICATION_HOST_CONTINUITY.json) không ghi nhận host ngủ trong batch.

## 4. Giả thuyết → quan sát → giải thích → giới hạn

Mọi nhận xét dưới đây chỉ áp dụng build/config của registry trên; giả thuyết lấy từ [protocol từng ca](PROTOCOL.md#4-checklist-từng-ca-cốt-lõi).

| Case / giả thuyết cần kiểm | Quan sát có nguồn | Cách giải thích được phép | Giới hạn |
|---|---|---|---|
| E01 PERIODIC: lịch đã đăng ký có thể tự chạy khi đủ điều kiện | Run [575a7a](pilots/run-sem41-pilot-e01-1-20261115-575a7a/audit.json): 5 cycle mới/90 phút, apply target 16, không direct dispatch | Phù hợp khả năng đồng bộ periodic nền trên emulator này; đạt mục tiêu ≥3 cycle trong phiên pilot | Một phiên, chưa main/OPPO; không chứng minh chạy chính xác mỗi 15 phút hoặc nhanh hơn push |
| E02 PUSH: nhận tín hiệu và áp dụng là hai mốc riêng | [SEM-34](../docs/evidence/SEM-34/CHECKS.md) ghi thiếu Firebase; không có pilot/main FCM thật cho build này | Chưa có quan sát để kết luận receipt, callback hoặc end-to-end | NOT_RUN; FCM accepted không thay cho received/applied |
| E03 PERIODIC: phân biệt trước/trong/sau confirmed Doze | Audit [dc9cc9](pilots/run-sem41-pilot-e03-1-20261115-dc9cc9/audit.json), [7f63e0](pilots/run-sem41-pilot-e03-2-20261115-7f63e0/audit.json): baseline/idle không có event; mỗi post_idle có 1 chuỗi work→fetch→apply | Trong hai phép thử force-idle này, cập nhật được quan sát sau thoát idle | INJECTED; không chứng minh mọi Doze tự nhiên luôn hoãn, không kiểm normal-priority push khi Doze |
| E04 PERIODIC: phục hồi sau mất mạng | Ba run [cda576](pilots/run-sem41-pilot-e04-1-20261115-cda576/manifest.json), [3bde4f](pilots/run-sem41-pilot-e04-2-20261115-3bde4f/manifest.json), [54c1a9](pilots/run-sem41-pilot-e04-3-20261115-54c1a9/manifest.json); [kiểm reconnect](../docs/evidence/SEM-41/PR_REVIEW_FIXES.json): target đều applied sau nối lại, giữ đủ window | Phù hợp đường network-constrained work phục hồi sau reconnect trên profile này | Không suy số retry/backoff từ khoảng im lặng; PUSH/TTL chưa kiểm, không gọi mọi network error là FCM lỗi |
| E05: duplicate/stale/race không làm giảm version hoặc mất cập nhật mới | Chưa có 9 run main và test logic/race bàn giao trong bộ nguồn này; [plan](plans/SEM-41/EMULATOR_PLAN.json) ghi NOT_RUN | Chưa xác nhận idempotency/coalescing/race bằng tập thực nghiệm E05 | Không suy E05 đạt từ SUCCESS E01/E06 hoặc từ unit-test tổng |
| E06 HYBRID: bỏ gửi có chủ đích, periodic vẫn phục hồi | [aa16ca](pilots/run-sem41-pilot-e06-1-20261116-aa16ca/events.jsonl), [8f734c](pilots/run-sem41-pilot-e06-2-20261116-8f734c/events.jsonl): mỗi run có một `push_send_skipped`, reason FAULT_INJECTION_SKIP, message/send_attempt null; apply nguồn PERIODIC | Chứng minh đường periodic phục hồi trong mode HYBRID với deliberate skip trên APK không có Firebase | INJECTED; không phải FCM làm mất tin, không kiểm hai trigger thật cùng hoạt động, không vượt force-stop |
| OPPO E01/E02 và lifecycle OEM | [SEM-42](../tasks/backlog/SEM-42.md) chưa có bộ artifacts bàn giao | Chỉ ghi thiếu dữ liệu | Không suy OPPO/ColorOS giống emulator; không có kết luận process death, vuốt recent hay force-stop trên máy thật |

## 5. Run lỗi, timeout và control được giữ riêng

### 12 lần thử SEM-41 cũ: INVALID

Chúng cùng APK nhưng khác điều kiện collector và có các epoch/baseline khác nhau; không gộp vào nhóm mới. Bảng dưới giữ **5 SUCCESS, 5 TIMEOUT, 2 FAILURE/ABORTED** như producer đã ghi. Không đổi timeout thành 0 ms hoặc xóa khỏi lịch sử. Mỗi manifest liên kết log/raw/report; chi tiết hash tại EVIDENCE_INDEX.

| Run cũ | Execution / outcome gốc | Lý do không dùng làm mẫu scheduler hợp lệ |
|---|---|---|
| [89b884](pilots/run-sem41-pilot-e01-1-20261115-89b884/manifest.json) | ABORTED / FAILURE | Setup aborted, chưa mở window |
| [760217](pilots/run-sem41-pilot-e01-1-20261115-760217/manifest.json) | COMPLETED / TIMEOUT | Dump trong window; baseline cùng version nhưng khác payload |
| [5db4eb](pilots/run-sem41-pilot-e03-1-20261115-5db4eb/manifest.json) | COMPLETED / SUCCESS | Dump trong window |
| [0d277e](pilots/run-sem41-pilot-e03-2-20261115-0d277e/manifest.json) | ABORTED / FAILURE | Measurement aborted; dump trong window |
| [c12a28](pilots/run-sem41-pilot-e03-2-20261115-c12a28/manifest.json) | COMPLETED / SUCCESS | Dump trong window; baseline khác payload |
| [a52b51](pilots/run-sem41-pilot-e04-1-20261115-a52b51/manifest.json) | COMPLETED / SUCCESS | Dump trong window |
| [b5e415](pilots/run-sem41-pilot-e04-2-20261115-b5e415/manifest.json) | COMPLETED / TIMEOUT | Dump trong window |
| [f9f6a0](pilots/run-sem41-pilot-e04-3-20261115-f9f6a0/manifest.json) | COMPLETED / SUCCESS | Dump trong window |
| [18fec8](pilots/run-sem41-pilot-e06-1-20261115-18fec8/manifest.json) | COMPLETED / TIMEOUT | Dump trong window |
| [f56fc9](pilots/run-sem41-pilot-e06-2-20261115-f56fc9/manifest.json) | COMPLETED / TIMEOUT | Dump trong window |
| [33a460](pilots/run-sem41-pilot-e03-2-20261115-33a460/manifest.json) | COMPLETED / SUCCESS | Dump trong window |
| [9a8b41](pilots/run-sem41-pilot-e01-1-20261115-9a8b41/manifest.json) | COMPLETED / TIMEOUT | Dump trong window |

[Audit collector](../docs/evidence/SEM-41/SCHEDULER_OBSERVER_AUDIT.json) ghi dump readiness có thể evaluate TimeController và thay đổi timer trên image này; 10 window đã đóng và một window aborted có dấu vết chuyển timer. Qualification cũ bị thu hồi cả SUCCESS lẫn TIMEOUT. [Đối chứng collector](../docs/evidence/SEM-41/COLLECTOR_COMPARISON.json) ghi E01 mới tự chạy sau khi bỏ dump. Đây là lý do không quy các timeout bị nhiễu thành hành vi Android/app tự nhiên. Snapshot `FINAL_VERIFICATION.json` lịch sử đã superseded; dùng [REQUALIFICATION_VERIFICATION](../docs/evidence/SEM-41/REQUALIFICATION_VERIFICATION.json) hiện hành.

### Development, legacy và fixture

| Bộ evidence / build | Vai trò và cách sử dụng |
|---|---|
| [SEM-41 manual smoke](development/run-sem41-v2-smoke-20261115/manifest.json), app `9e7e55b` | MANUAL control, cache 3→4, kiểm serializer/export v2; không tính thành công nền |
| [SEM-41 dispatch diagnostic](development/run-sem41-dispatch-diagnostic-1715327d9b29/manifest.json), app `9e7e55b` | CONTROL/INJECTED, có collector cũ và một direct dispatch sau 20 phút; xác nhận worker/core apply target 15, không phải E01 tự nhiên |
| [SEM-34 config control](development/run-sem34-fcm-config-20261112/manifest.json), app `decdef6` | Firebase chưa cấu hình; không phải phép gửi/nhận FCM thành công |
| [SEM-29 lần đầu](runs/run-sem29-periodic-emulator-20261107/manifest.json), app `a26646d`; [r2](runs/run-sem29-periodic-emulator-20261107-r2/manifest.json), app `95eeecb` | Pilot legacy-room-v1, build/Play services khác; giữ evidence lịch sử và validity gốc, không nâng schema hoặc cộng vào pilot build mới/main |
| [Fixture SEM-24](fixture_exports/run-sem24-fixture/manifest.json) | FIXTURE kiểm công cụ; không phải dữ liệu chạy thật |

## 6. Quy tắc diễn giải số liệu

- **Main và pilot:** chỉ tập `run_phase=main` với metadata/candidate/validity được kiểm mới tạo thống kê main. INVALID vẫn hiện trong inventory và số loại trừ, timeout hợp lệ phải giữ trong mẫu số của đúng nhóm. Không trộn build, config, epoch hoặc observer bị nhiễu.
- **Mẫu số:** SUMMARY này chỉ trình bày outcome/count do producer ghi và trạng thái bàn giao. Chưa có kết quả parser/kiểm độc lập cho 8 run mới; không tự gọi các count đó là `n_eligible` của SEM-45.
- **Clock:** collector có boot alias đã kiểm để xác minh duration cửa sổ. Android event vẫn `boot_session_id=null`, clock controlled=false. Không tự bổ sung boot ID vào event; không tính received→enqueue, queue, sync hoặc update→applied median/min–max trong SUMMARY này. Duration window ở registry không phải duration của worker.
- **Median về sau:** khi nhận CSV/audit đúng revision, mỗi metric phải có `n_complete/n_total`, số sample duration đo được và missing/timeout; chỉ tính trên sample có căn cứ clock. N/A/null không phải 0 ms. Tách accepted, received, enqueued, started, fetched và applied.
- **Pin và tốc độ:** số request/cycle/DB write không chuyển thành mAh hoặc kết luận tiết kiệm pin. Không xếp hạng periodic và push khi chưa kiểm soát thời điểm update trong chu kỳ; không có phép so latency hai máy tại snapshot này.
- **Độ khái quát:** một emulator, một build không đại diện mọi Android/OEM. 8 pilot SUCCESS không chứng minh độ tin cậy thống kê rộng hoặc thay 33 main slot.

## 7. Bàn giao cho report/slide và cập nhật tiếp

Có thể dùng: “Trên một emulator với APK không có Firebase, tám pilot hợp lệ ghi nhận periodic tự chạy, phục hồi sau các tình huống Doze/mất mạng được điều khiển, và cập nhật khi chủ đích bỏ gửi push. E01 có 5 cycle trong phiên 90 phút. Tập main và đối chiếu OPPO chưa chạy.” Luôn kèm build, nhãn pilot và giới hạn trên.

Chưa có căn cứ cho các câu “silent push đã nhận thành công”, “hybrid xử lý FCM mất tin”, “nhanh hơn/tiết kiệm pin hơn”, “OPPO hoạt động giống emulator”, hoặc “đã hoàn thành E01–E06 main”.

Đầu ra này phục vụ [SEM-48](../tasks/backlog/SEM-48.md), [SEM-50](../tasks/backlog/SEM-50.md), [SEM-52](../tasks/backlog/SEM-52.md), [SEM-55](../tasks/backlog/SEM-55.md). Khi có đầu vào mới:

1. SEM-41/42 bàn giao main manifest/events đúng artifact/config, giữ timeout và mọi run bị nhiễu. Không đổi nhãn pilot hồi tố từ SUMMARY.
2. SEM-45 cập nhật nguồn đã ghim và tái sinh CSV đúng phạm vi; 8 run mới hiện nằm ngoài CSV ở PR #30.
3. SEM-44 kiểm độc lập trigger/window/clock/mẫu số và ghi audit theo revision mới. Audit producer SEM-41 không thay chữ ký kiểm độc lập này.
4. SEM-43 cập nhật snapshot/hash, từng hàng quan sát và giới hạn; chỉ điền median/rate khi CSV/audit cho phép. Nếu candidate đổi code/config ảnh hưởng, nhận requalification/rerun tương ứng trước khi mở rộng kết luận.
