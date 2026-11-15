# SEM-41 — Emulator main readiness và kiểm candidate

## Nhận dạng và đầu vào

- Vinh (`Vinh5905`) thực hiện ngày **15/11/2026, UTC+7**. Nhánh `codex/SEM-41-emulator-main` từ main `6e87411b60e8504d431cd06e577be94b7bb2244f`, sau merge SEM-34 PR #26. Hạn gốc 07/11/2026 13 giờ được giữ trong task.
- [SEM-16](../SEM-16/CHECKS.md) và [SEM-24](../SEM-24/CHECKS.md) đã nhận. Task SEM-41 hiện cho phép bắt đầu trước SEM-37, còn [protocol](../../../experiments/PROTOCOL.md) yêu cầu candidate trước khi ghi phase `main`.
- SEM-41 dùng **emulator**. Máy OPPO do Trí thực hiện tại [SEM-42](../../../tasks/backlog/SEM-42.md).
- Candidate đang ở [PR #28](https://github.com/ThanhTris/Seminar-IE307/pull/28), draft, branch `codex/SEM-36-37-52-trung-final`, head mới đã kiểm `1f79ee93e9a52af2b21c82372f23a6ac684d3ceb`. Manifest nguồn ghim app `9e7e55b76c646ff113a152022cc23317a202e533`, server `c77772e426c00ae464240f00942f8368c638aaa8`, `candidate_status=NOT_READY`, `release_gate.passed=false`, APK/hash để null.
- Đã build đúng app revision ghim trong worktree detached, kiểm runtime Android/server không đổi so với head PR #28. File nguồn của task Trung được giữ trong worktree riêng để kiểm, phần thay đổi SEM-41 gồm plan và evidence.

## Kiểm thực tế ngày 15/11

| Hạng mục | Expected | Actual | Kết quả |
|---|---|---|---|
| Toolchain máy Vinh | Có SDK/license để build revision candidate | JDK 21.0.11, Gradle 9.6.0, SDK 37, Build Tools 36.0.0 và license có sẵn | Pass |
| Assemble app/test APK | Có artifact từ source ghim | `assembleDebug` và `assembleDebugAndroidTest` tạo APK trên local | Pass — build artifact |
| Unit tests tại source `9e7e55b` | Toàn bộ suite đạt trước freeze | 32 tests, **31 pass / 1 fail**, command exit 1. `autoGeneratesRequestIdWhenMissingInPayload` còn đòi request ID trên `push_received`, nơi contract mới giữ null | Fail tại revision đã kiểm ban đầu; xem follow-up bên dưới |
| Cài đúng APK | Installed APK khớp hash file build | App SHA-256 `bde050c084d655c66f9f1497c57900a7f0efc39e12a9da55110771926c3f2e23`, hash thiết bị khớp. Test APK `6d38f794e7df9225926941394ae63db0afce9d365080ab3e69899d402992b4d8` | Pass — development |
| Migration Room | Giữ dữ liệu v1 khi lên v2 | Schema 1→2, 30 event trước/sau, mọi cột cũ giữ đúng giá trị, cache trước/sau 3 | Pass — development |
| Cấu hình qua UI | Nhận run ID/device alias/mode đúng thao tác | Nhập run `run-sem41-v2-smoke-20261115`, alias `emulator-main`, chọn PUSH qua giao diện. Periodic không active | Pass — development |
| Shared core và export v2 mới | Capture từ client/server thật, kiểm schema | Bấm manual sync, cache 3→4. Có work_enqueued/start/fetch_start/fetch_complete/applied, 5 event ANDROID source MANUAL được validator SEM-24 chấp nhận | Pass — development control |
| Omission report | Giữ lý do event chưa xuất được | Run smoke có 1 `periodic_cancelled` bị loại khỏi canonical và được ghi rõ trong report, raw Room giữ đủ 6 row | Pass — partial export được ghi rõ |
| Legacy sau migration | Các row thiếu provenance giữ format cũ | Lượt SEM-29 r2 xuất 0 canonical, báo 15 omitted do thiếu captured mode hoặc periodic_cancelled chưa hỗ trợ | Pass — legacy không được nâng nhãn |
| Firebase | Có project/config/token trước các ca PUSH | App báo `FIREBASE_NOT_CONFIGURED`; người dùng đã xác nhận chưa có cấu hình trong SEM-34 | Blocker |
| Candidate gate | Manifest đã freeze cùng APK/config/pilot | Nguồn SEM-37 vẫn NOT_READY; chưa freeze APK/checksum/profile. Unit suite follow-up đã đạt 32/32 | Blocker — bàn giao candidate |
| Main E01–E06 | Đủ số lượt/window trên candidate | 27 slot PLANNED/NOT_RUN, chưa tạo run main | Not run |
| Cleanup | Thiết bị/server không còn work chạy của control | Home resumed, stopped=false, mạng connected, idle ACTIVE, 0 active sync work. Server riêng đã dừng và gỡ lock | Pass — development |

Lần build đầu trong OneDrive còn lỗi ghi Gradle cache `Operation timed out`. Đã kiểm lại cùng revision trong worktree local, không còn lỗi I/O; ở lần kiểm ban đầu còn 1 lỗi unit test (follow-up bên dưới đã đạt 32/32). Lệnh build tổng trả exit 1 do test, các APK assemble đã được tạo. APK này phục vụ kiểm development, gate candidate tiếp tục false.

## Evidence và phạm vi dữ liệu

- [PREFLIGHT.json](PREFLIGHT.json) giữ build/hash, unit test failure, migration, export/omission, thiết bị và cleanup. Capture DB, build log và mapping giữ private trong `.local/sem41/`.
- [CONTROL manifest](../../../experiments/development/run-sem41-v2-smoke-20261115/manifest.json), [events](../../../experiments/development/run-sem41-v2-smoke-20261115/events.jsonl) và [export report](../../../experiments/development/run-sem41-v2-smoke-20261115/export_report.json) thuộc `run_phase=development`, `case_id=CONTROL`, `candidate_gate_passed=false`.
- Bộ control gồm 4 server update setup đưa store riêng từ 0 tới 4 và 5 event Android MANUAL. Các bản update có cùng run ID, target cuối 4. Server source không đổi giữa `decdef6` và `c77772e`, runtime dùng server v2 đã build từ source đó.
- [Raw Android](../../../experiments/development/run-sem41-v2-smoke-20261115/android-events-raw.jsonl), [omission report](../../../experiments/development/run-sem41-v2-smoke-20261115/canonical-export-report.json) và [state sau export](../../../experiments/development/run-sem41-v2-smoke-20261115/state-after.json) giữ provenance của kiểm serializer. `boot_session_id` của event vẫn null như producer đã xuất. Clock controlled=false, chưa tính latency giữa hai máy.
- [EMULATOR_PLAN.json](../../../experiments/plans/SEM-41/EMULATOR_PLAN.json) có 27 slot dự kiến, 34920 giây = **582 phút = 9 giờ 42 phút** quan sát. Setup, pilot, export, cleanup và buffer được tính thêm. Slot ID dùng `planned-slot-*`, run ID/app commit/APK cho main để null.

Sau control development lúc 03:00 UTC, emulator giữ APK development của revision candidate nêu trên, mode PUSH, cache 4, 0 work active. Lịch periodic cũ đã được hủy từ các task trước, smoke không đăng ký lại. Các lượt pilot ở phần dưới dùng run/alias/mode mới qua UI và cập nhật cache theo kết quả từng lượt.

## Phần cần nhận để chạy main

1. **SEM-37 của Trung** bàn giao revision cuối và chốt APK/checksum/gate cùng pilot liên quan. Follow-up `1f79ee9` đã sửa assertion theo review PR #28, kiểm thực tế trên máy Vinh đạt 32/32 unit tests. Hash của kiểm development này là artifact đầu vào để đối chiếu, không tự thay thế freeze của SEM-37.
2. **Pilot theo từng loại ca** trên revision sẽ đo. SEM-29 là kết quả lịch sử trước thay đổi mode/provenance. Đã có pilot cho 8 slot không cần Firebase trong profile bên dưới; E01 còn phải đánh giá mục tiêu ≥3 cycle theo kết quả thật. Ca PUSH/profile Firebase chưa kiểm, và phải requalify ca bị ảnh hưởng khi candidate cuối đổi code/config.
3. **Firebase** cho 19 slot PUSH thuộc E02/E03/E04/E05, gồm google-services.json, credential project, token emulator hiện hành. Tám slot PERIODIC/HYBRID skip vẫn cần candidate/pilot đúng ca.
4. **E05 race** cần hook/barrier và bằng chứng worker đang chạy khi tín hiệu mới tới. Đặt INJECTED cho nhóm đó và nhận test logic SEM-38/39. B1 còn thiếu thì giữ các slot push/race NOT_RUN.
5. **Export v2** được kiểm lại theo revision cuối, ghi raw/omission nếu có, giữ các event ngoài window. Main valid yêu cầu đúng candidate và metadata, các run sai điều kiện/timeout vẫn được giữ riêng theo kết quả thật.

Đầu vào thứ tự được ghi trong [REPRODUCE](REPRODUCE.md). Các ca main hiện Not run. Task SEM-41 tiếp tục Todo trên Project trong lần bàn giao này.

## Kiểm artifact bàn giao

50 tests công cụ và 32/32 Android unit tests follow-up đạt. Đã kiểm 27 slot main/582 phút còn NOT_RUN, 8 slot pilot hợp lệ và 4 lần thử INVALID giữ riêng, control development với 9 canonical event và raw accounting đầy đủ. Mọi pilot tái xuất manifest/events/export report giống từng byte; 56 link nội bộ, JSON/JSONL và scan định danh/secret đạt. Hai candidate worktree giữ sạch tại revision đã kiểm. `git diff --check` đạt.

Sau phiên đã fetch origin: main vẫn `6e87411b60e8504d431cd06e577be94b7bb2244f` và là ancestor của nhánh SEM-41. PR #29 không có issue comment, inline review comment hoặc review mới; không có CI check được cấu hình trên PR. Trạng thái draft được giữ vì main chưa chạy.

## Pilot thật không cần Firebase — đã đóng các cửa sổ khả thi

Đã thu đủ **8 slot pilot hợp lệ**: E01×1, E03 PERIODIC×2, E04 PERIODIC×3 và E06×2, giữ nguyên cả SUCCESS/TIMEOUT. Bốn lần thử sai điều kiện được giữ riêng dưới INVALID; tổng 12 lần thử, không chọn lại mẫu theo kết quả. Đây là `run_phase=pilot`, `candidate_gate_passed=false`; **27 slot main vẫn NOT_RUN**. [PILOT_RESULTS.json](PILOT_RESULTS.json) là index đầy đủ. Raw DB/OS dump, mapping và retained store gốc giữ private.

Tổng window danh định của 8 slot hợp lệ là **346 phút (5 giờ 46 phút)**. Setup/cleanup và các lần thử INVALID làm thời gian thực dài hơn. Thời gian bị thiếu của run cũ không được nối vào run thay thế.

| Slot hợp lệ | Window thực tế UTC+7; Android elapsed | Cache trước → sau; target | Cycle nền mới | Outcome |
|---|---|---|---:|---|
| [E01:1](../../../experiments/pilots/run-sem41-pilot-e01-1-20261115-9a8b41/manifest.json) | 17:30:37–19:00:37; 5,400,630 ms | 13→13; V=14 | 0 | **TIMEOUT** |
| [E03:1](../../../experiments/pilots/run-sem41-pilot-e03-1-20261115-5db4eb/manifest.json) | 11:54:58–12:30:02; 2,103,340 ms | 5→6; V=6 | 1 | **SUCCESS** |
| [E03:2](../../../experiments/pilots/run-sem41-pilot-e03-2-20261115-33a460/manifest.json) | 16:54:44–17:29:47; 2,103,500 ms | 12→13; V=13 | 1 | **SUCCESS** |
| [E04:1](../../../experiments/pilots/run-sem41-pilot-e04-1-20261115-a52b51/manifest.json) | 13:34:15–14:06:24; 1,929,360 ms | 7→8; V=8 | 1 | **SUCCESS** |
| [E04:2](../../../experiments/pilots/run-sem41-pilot-e04-2-20261115-b5e415/manifest.json) | 14:06:41–14:38:50; 1,928,740 ms | 8→8; V=9 | 0 | **TIMEOUT** |
| [E04:3](../../../experiments/pilots/run-sem41-pilot-e04-3-20261115-f9f6a0/manifest.json) | 14:39:06–15:11:15; 1,928,830 ms | 9→10; V=10 | 1 | **SUCCESS** |
| [E06:1](../../../experiments/pilots/run-sem41-pilot-e06-1-20261115-18fec8/manifest.json) | 15:11:28–15:56:29; 2,700,780 ms | 10→10; V=11 | 0 | **TIMEOUT** |
| [E06:2](../../../experiments/pilots/run-sem41-pilot-e06-2-20261115-f56fc9/manifest.json) | 15:56:41–16:41:42; 2,701,060 ms | 11→11; V=12 | 0 | **TIMEOUT** |

Không có snapshot_applied target sau window trong các log đã xuất; mọi work_started sau clock vẫn được giữ và tách khỏi cycle tự nhiên.

E01 ghi **0 cycle tự nhiên mới trong 90 phút**; chu kỳ setup trước Home và event sau đóng window được giữ nhưng không cộng vào số này. Chưa đạt mục tiêu ≥3 cycle của protocol. Giữ phiên hợp lệ cùng outcome thật; cần phiên bổ sung riêng 90 phút trên candidate/profile đã chốt sau khi rà điều kiện scheduler. Không force-run hoặc lặp lại chỉ để thay TIMEOUT bằng kết quả đẹp.

E03 tách đủ 5 phút baseline, 20 phút **confirmed IDLE**, 10 phút sau thoát; ADB force-idle mang nhãn INJECTED. Đọc `phase_event_counts` trong audit từng run để phân biệt event trước/trong/sau idle. E04 có proof guest không còn default network và HTTP tới server thất bại, giữ đủ 2 phút offline và 30 phút sau reconnect, rồi khôi phục từng transport baseline. Cả ba lần lặp và timeout được giữ trong mẫu hợp lệ.

E06 có `push_send_skipped`, reason `FAULT_INJECTION_SKIP`, không tạo message/send-attempt giả; mỗi lượt đủ 45 phút sau update. Profile này có **FIREBASE_NOT_CONFIGURED**, chỉ kiểm deliberate skip và quan sát periodic trong mode HYBRID. Chưa kiểm callback/token hoặc hybrid trên APK đã cấu hình Firebase; không diễn giải skip thành FCM mất tin. Main E06 vẫn phải nhận đúng candidate/profile cuối.

### Các lần thử INVALID được giữ nguyên

| Lần thử | Outcome quan sát được | Lý do loại khỏi mẫu hợp lệ |
|---|---|---|
| [E01:1 / 89b884](../../../experiments/pilots/run-sem41-pilot-e01-1-20261115-89b884/manifest.json) | ABORTED / FAILURE | Chưa bắt đầu clock: Ctrl+A không clear Compose text, run ID bị nối. Guard chặn; giữ setup diagnostic/raw của run ID thực tế. |
| [E01:1 / 760217](../../../experiments/pilots/run-sem41-pilot-e01-1-20261115-760217/manifest.json) | COMPLETED / TIMEOUT | Đủ 90 phút nhưng baseline version 4 có payload khác store r2; audit toàn nội dung phát hiện sau đo. |
| [E03:2 / 0d277e](../../../experiments/pilots/run-sem41-pilot-e03-2-20261115-0d277e/manifest.json) | ABORTED / FAILURE | Đã baseline/20 phút IDLE nhưng đọc ACTIVE quá sớm sau wakeup, abort trước đủ 10 phút post-idle; cleanup retry phục hồi đạt. |
| [E03:2 / c12a28](../../../experiments/pilots/run-sem41-pilot-e03-2-20261115-c12a28/manifest.json) | COMPLETED / SUCCESS | Đủ 35 phút, observed SUCCESS nhưng baseline version 6 có payload khác store r3; audit phát hiện sau đo. |

Runner cũ tạo store mới rồi seed tới cached version, khiến cùng version/ETag trỏ tới nội dung khác. Hai run `760217` và `c12a28` được hạ validity thành INVALID; **timestamps, versions, outcomes, raw/canonical events không đổi**. `baseline-content-proof.json` so capture SQLite với response lịch sử trong retained ledger, không suy baseline từ version hoặc snapshot hiện tại. Các run còn lại đều qua cùng phép so sánh toàn payload.

Commit `ffecae09411ce6113e6dc2c4259fb846cc1b54b1` bỏ seed theo số version; client có cache phải nhận retained store, từ chối server lùi dưới cache, kiểm version và hash toàn bộ item payload trước clock. R2/r3 là hai epoch server riêng, không ghép timeline chỉ bằng version. Các lượt E04/E06 r3 có baseline khớp snapshot r3. R4/r5 giữ chính ledger/store r3 liên tục; MANUAL control ngoài window đưa cache về snapshot hiện hành, kiểm payload khớp và WorkManager đã drain trước đo. Không xóa cache/store hoặc sửa ledger lịch sử.

### Provenance, export và giới hạn

Mỗi run có `runner-identity.json` ghi full observer commit/SHA-256; bản mới còn ghi hash module baseline. Observer r2 là `0808b6fe98d6eb924785d9a3d78114ddaf58c802`; r3 là `056e7896fdd87d71fdd753f96736ae87e06ac378`; r4/r5 ghi identity thực tế trong artifact, dùng code đã sửa baseline. Clear text đã đổi sang MOVE_END/DEL và kiểm UI text trước chọn mode; thoát Doze chờ ACTIVE có giới hạn và lưu transition. Code/app/server không đổi trong từng window.

Audit kiểm raw/canonical/omitted ID accounting, single registration/work identity, request/fetch/applied provenance, full window, OS checkpoints, baseline payload và cleanup. Các event ngoài window vẫn được xuất; instrumentation cancel/export chỉ chạy sau khi clock đóng. `periodic_cancelled` chưa hỗ trợ canonical được report omitted, raw giữ nguyên. Không dùng work_started trong giai đoạn đóng run/control làm cycle tự nhiên.

Manifest giữ boot alias collector từ hash kernel boot ID thực tế, cùng boot được observer kiểm tại checkpoint. Event `boot_session_id=null` giữ đúng producer; không bổ sung ID hoặc tính event latency từ nó. Clock controlled=false, không tính latency liên máy. Không trộn pilot/main hoặc build/epoch/config khác nhau; không rút kết luận lỗi OS/app từ việc một job ready mà chưa chạy.

**50 tests công cụ đạt**: 36 exporter, 9 review/baseline, 5 control. Test tổng hợp không phải số liệu thực nghiệm. [FINAL_VERIFICATION.json](FINAL_VERIFICATION.json) ghi đối chiếu lại mọi audit/provenance/metadata, scan privacy, link và tái xuất manifest/events/export report giống từng byte; [DEVICE_CLEANUP.json](DEVICE_CLEANUP.json) ghi kiểm app/test APK, toàn bộ sync work và trạng thái thiết bị/server sau phiên.

### Candidate follow-up đã nhận

Đã kiểm lại PR #28 và fetch head `1f79ee93e9a52af2b21c82372f23a6ac684d3ceb`, cập nhật lúc 06:14 UTC. Android diff so với source APK đã đo chỉ có `PushSyncEnqueueAdapterTest.kt`; app runtime/AndroidTest source không đổi. Assertion được chuyển sang enqueued input theo contract. **Đã chạy `:app:testDebugUnitTest` trên source follow-up: 32 tests, 0 failure/error/skip, exit 0**, kết thúc 09:42:30 UTC, sau cleanup batch r3 và trước replacement r4. [UNIT_FOLLOWUP.json](UNIT_FOLLOWUP.json) ghi source, diff và hash XML/build log. Lỗi 31/32 trong PREFLIGHT là kết quả lịch sử ở source cũ, đã được follow-up giải quyết.

Manifest upstream vẫn NOT_READY/gate false, chưa có APK/checksum freeze. Không cài APK mới; các lượt đo giữ app/source `9e7e55b` và hash đã kiểm, không đổi provenance theo head tài liệu mới. Build chạy trong worktree riêng ngoài cửa sổ quan sát.
