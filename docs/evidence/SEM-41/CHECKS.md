# SEM-41 — Emulator main readiness và kiểm candidate

## Nhận dạng và đầu vào

- Vinh (`Vinh5905`) thực hiện ngày **15/11/2026, UTC+7**. Nhánh `codex/SEM-41-emulator-main` từ main `6e87411b60e8504d431cd06e577be94b7bb2244f`, sau merge SEM-34 PR #26. Hạn gốc 07/11/2026 13 giờ được giữ trong task.
- [SEM-16](../SEM-16/CHECKS.md) và [SEM-24](../SEM-24/CHECKS.md) đã nhận. Task SEM-41 hiện cho phép bắt đầu trước SEM-37, còn [protocol](../../../experiments/PROTOCOL.md) yêu cầu candidate trước khi ghi phase `main`.
- SEM-41 dùng **emulator**. Máy OPPO do Trí thực hiện tại [SEM-42](../../../tasks/backlog/SEM-42.md).
- Source ứng viên ở [PR #28](https://github.com/ThanhTris/Seminar-IE307/pull/28), head đã kiểm `1f79ee93e9a52af2b21c82372f23a6ac684d3ceb`, đã merge lúc 12:21 UTC. SEM-37 được ghi Done trên Project ở snapshot main `bcc7c58853fb5de59bb9bd599cd12fe41e5ee0eb` (12:27 UTC), **không kèm APK freeze**. Manifest nguồn ghim app `9e7e55b76c646ff113a152022cc23317a202e533`, server `c77772e426c00ae464240f00942f8368c638aaa8`, `candidate_status=NOT_READY`, `release_gate.passed=false`, APK/hash để null.
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
| Candidate gate | Manifest đã freeze cùng APK/config/pilot | Task SEM-37 Done, release manifest vẫn NOT_READY; chưa freeze APK/checksum/profile. Unit suite follow-up đã đạt 32/32 | Blocker — bàn giao candidate |
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

1. **Chốt artifact/gate trước main.** SEM-37 đã Done/merge về source, nhưng release manifest vẫn NOT_READY/gate false, chưa freeze APK/checksum/profile. Follow-up `1f79ee9` đã sửa assertion theo review PR #28, kiểm thực tế trên máy Vinh đạt 32/32 unit tests. Hash của kiểm development này là artifact đầu vào để đối chiếu, không tự thay thế freeze của SEM-37.
2. **Pilot theo từng loại ca** trên revision/profile sẽ đo. Hiện có 4/8 slot được qualify lại bằng collector đã sửa; E01 đã đạt 5 cycle tự nhiên/90phút. Ca PUSH/profile Firebase chưa kiểm; requalify ca bị ảnh hưởng nếu candidate cuối đổi code/config.
3. **Firebase** cho 19 slot PUSH thuộc E02/E03/E04/E05, gồm google-services.json, credential project, token emulator hiện hành. Tám slot PERIODIC/HYBRID skip vẫn cần candidate/pilot đúng ca.
4. **E05 race** cần hook/barrier và bằng chứng worker đang chạy khi tín hiệu mới tới. Đặt INJECTED cho nhóm đó và nhận test logic SEM-38/39. B1 còn thiếu thì giữ các slot push/race NOT_RUN.
5. **Export v2** được kiểm lại theo revision cuối, ghi raw/omission nếu có, giữ các event ngoài window. Main valid yêu cầu đúng candidate và metadata, các run sai điều kiện/timeout vẫn được giữ riêng theo kết quả thật.

Đầu vào thứ tự được ghi trong [REPRODUCE](REPRODUCE.md). Các ca main hiện Not run. Task SEM-41 tiếp tục Todo trên Project trong lần bàn giao này.

## Thu hồi qualification do collector và đo lại

Snapshot `FINAL_VERIFICATION.json` lúc 12:00 UTC là lịch sử ở commit `0e293c1`, trước khi phát hiện tác động của collector. **Không dùng số 8 valid trong snapshot đó làm trạng thái hiện hành.** [PILOT_RESULTS.json](PILOT_RESULTS.json) và [SCHEDULER_OBSERVER_AUDIT.json](SCHEDULER_OBSERVER_AUDIT.json) là index/audit mới. Giữ nguyên mọi raw event, timestamp, version, SUCCESS/TIMEOUT; chỉ sửa validity/reason và evidence review.

### Phát hiện từ control thật

[Control dispatch](../../../experiments/development/run-sem41-dispatch-diagnostic-1715327d9b29/manifest.json) dùng đúng APK đã đo, mode PERIODIC, phase **development/CONTROL/INJECTED**. Trong 1.200.440 ms trước direct dispatch không có cycle mới, target 15 chưa applied (cache 14). Sau một lệnh `jobscheduler run --satisfied` cho đúng namespace/job/work ID, worker fetch và apply target 15, cache 14→15. Không dùng `--force`; command accepted được đối chiếu với event apply thật. Đây là kiểm đường dispatch/worker/core, **không phải thành công tự nhiên của E01**. Raw 10 row = 9 canonical Android + 1 omitted cancel; thêm một server update. [DISPATCH_DIAGNOSTIC.json](DISPATCH_DIAGNOSTIC.json) ghi hash/provenance và phân vùng trước/sau điều khiển.

Các API pending-reason không thống nhất sau mốc 15 phút: current reason vẫn MINIMUM_LATENCY, history có APP, trong khi dump in READY và không còn entry timer. Không diễn giải APP thành lỗi ứng dụng hoặc cộng các duration thành latency. Probe không đổi PID app trong mọi truy vấn; không mở app/instrumentation trong pha 20 phút. [JobScheduler API](https://developer.android.com/reference/android/app/job/JobScheduler) giải thích phạm vi của reasons/history/stats.

### Collector có thể thay đổi trạng thái đang đo

Trong mã [JobSchedulerService của AOSP](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/apex/jobscheduler/service/java/com/android/server/job/JobSchedulerService.java), readiness evaluation từ dump có thể gọi controller evaluation. [TimeController](https://android.googlesource.com/platform/frameworks/base/+/main/apex/jobscheduler/service/java/com/android/server/job/controllers/TimeController.java) có đường satisfy timing delay rồi bỏ entry theo dõi mà không phát callback chạy job trong đường evaluate này. Trên image đã đo, các dump trong window in TIMING_DELAY chưa thỏa ở đầu dump nhưng sau evaluation timer không còn trong danh sách theo dõi. Đây là bằng chứng collector có side effect, phù hợp với source AOSP; không coi READY trong dump là một phép quan sát thuần túy.

Cả 10 phiên cũ đã đóng và phiên Doze aborted có dấu vết chuyển timer như vậy. Tám qualification từng được ghi VALID được thu hồi thận trọng về INVALID; hai run lỗi baseline và hai lần abort vốn đã INVALID giữ mọi lý do cũ. Không chọn loại chỉ các timeout: cả SUCCESS cũ cũng bị loại khỏi mẫu scheduler hợp lệ. Mỗi run có `scheduler-observation-proof.json` với tên/hash capture và mốc clock; capture OS đầy đủ giữ private, không công bố raw UID/định danh.

Observer commit **`db98fa8d275c3ca2d10895daa61f00bf53f59cd7`** bỏ mọi `dumpsys jobscheduler` trong window, checkpoint chỉ đọc idle/activity/package/battery. Guard từ chối dump scheduler khi clock chưa đóng. Snapshot scheduler chỉ ở setup hoặc sau end. Regression tests kiểm guard trước ADB và review từ chối artifact có dump trong window, kể cả label tự xưng read-only. App/test APK, interval, source server và dữ liệu không đổi. Không điều chỉnh quota/policy để ép chạy.

### Batch đo lại với collector đã sửa

[Đối chứng collector](COLLECTOR_COMPARISON.json): ở phút20 của E01 mới đã có 1 cycle tự chạy/apply target16, xảy ra trước lần copyRoom; không directdispatch/instrumentation/jobdump. Đây là capture giữa phiên, không thay cho window90phút.

Đã có **4/8 slot hợp lệ** trong batch r6; còn 4 slot. Trạng thái: `RUNNING`. Toàn bộ 8 cửa sổ là 346 phút, không tính setup/cleanup. Main vẫn 27 slot NOT_RUN.

| Slot hợp lệ mới | Window UTC+7; duration | Cache trước→sau; target | Cycle mới | Outcome |
|---|---|---|---:|---|
| [E01:1](../../../experiments/pilots/run-sem41-pilot-e01-1-20261115-575a7a/manifest.json) | 15/11 20:03:29–15/11 21:33:30; 5,400,720 ms | 15→16; V=16 | 5 | SUCCESS |
| [E03:1](../../../experiments/pilots/run-sem41-pilot-e03-1-20261115-dc9cc9/manifest.json) | 15/11 21:33:43–15/11 22:08:47; 2,103,830 ms | 16→17; V=17 | 1 | SUCCESS |
| [E03:2](../../../experiments/pilots/run-sem41-pilot-e03-2-20261115-7f63e0/manifest.json) | 15/11 22:09:04–15/11 22:44:07; 2,103,090 ms | 17→18; V=18 | 1 | SUCCESS |
| [E04:1](../../../experiments/pilots/run-sem41-pilot-e04-1-20261115-cda576/manifest.json) | 15/11 22:44:24–15/11 23:16:36; 1,931,840 ms | 18→19; V=19 | 2 | SUCCESS |

Không có snapshot_applied target sau window trong các slot mới đã đóng; event setup/post-window vẫn được giữ và tách khỏi cycle nền.

### Các lần thử cũ được giữ dưới INVALID

| Lượt | Outcome thật | Lý do qualification bị loại |
|---|---|---|
| [E01:1 / 89b884](../../../experiments/pilots/run-sem41-pilot-e01-1-20261115-89b884/manifest.json) | ABORTED/FAILURE | aborted; giữ lý do gốc trong manifest |
| [E01:1 / 760217](../../../experiments/pilots/run-sem41-pilot-e01-1-20261115-760217/manifest.json) | COMPLETED/TIMEOUT | collector dump trong window; BASELINE_PAYLOAD_MISMATCH |
| [E03:1 / 5db4eb](../../../experiments/pilots/run-sem41-pilot-e03-1-20261115-5db4eb/manifest.json) | COMPLETED/SUCCESS | collector dump trong window |
| [E03:2 / 0d277e](../../../experiments/pilots/run-sem41-pilot-e03-2-20261115-0d277e/manifest.json) | ABORTED/FAILURE | collector dump trong window; aborted; giữ lý do gốc trong manifest |
| [E03:2 / c12a28](../../../experiments/pilots/run-sem41-pilot-e03-2-20261115-c12a28/manifest.json) | COMPLETED/SUCCESS | collector dump trong window; BASELINE_PAYLOAD_MISMATCH |
| [E04:1 / a52b51](../../../experiments/pilots/run-sem41-pilot-e04-1-20261115-a52b51/manifest.json) | COMPLETED/SUCCESS | collector dump trong window |
| [E04:2 / b5e415](../../../experiments/pilots/run-sem41-pilot-e04-2-20261115-b5e415/manifest.json) | COMPLETED/TIMEOUT | collector dump trong window |
| [E04:3 / f9f6a0](../../../experiments/pilots/run-sem41-pilot-e04-3-20261115-f9f6a0/manifest.json) | COMPLETED/SUCCESS | collector dump trong window |
| [E06:1 / 18fec8](../../../experiments/pilots/run-sem41-pilot-e06-1-20261115-18fec8/manifest.json) | COMPLETED/TIMEOUT | collector dump trong window |
| [E06:2 / f56fc9](../../../experiments/pilots/run-sem41-pilot-e06-2-20261115-f56fc9/manifest.json) | COMPLETED/TIMEOUT | collector dump trong window |
| [E03:2 / 33a460](../../../experiments/pilots/run-sem41-pilot-e03-2-20261115-33a460/manifest.json) | COMPLETED/SUCCESS | collector dump trong window |
| [E01:1 / 9a8b41](../../../experiments/pilots/run-sem41-pilot-e01-1-20261115-9a8b41/manifest.json) | COMPLETED/TIMEOUT | collector dump trong window |

Baseline vẫn phải khớp **cả version lẫn toàn payload**. Hai lỗi cùng-version/khác-payload từ các epoch r2/r3 giữ nguyên proof/INVALID; runner dùng retained store r3 liên tục, không seed/xóa ledger/cache. Hash payload chỉ để đối chiếu; cache items/DB gốc giữ private. Control MANUAL ngoài window đưa cache về snapshot hiện hành khi cần.

Review đối chiếu raw/canonical/omitted ID, source/work/fetch provenance, full window/phases, baseline và collector side effect. Event trước/sau window và cancel omitted được giữ, không biến thành cycle tự nhiên. Boot alias collector cùng boot được xác minh; event boot_session_id null giữ nguyên. Clock controlled=false, không tính latency liên máy.

E06 chỉ kiểm deliberate skip thật `FAULT_INJECTION_SKIP` và periodic trong mode HYBRID trên profile **FIREBASE_NOT_CONFIGURED**. Không tạo send/message giả, không kiểm callback/token hoặc diễn giải skip thành FCM mất tin. Main/profile Firebase vẫn chờ candidate và requalification riêng.

**67 tests công cụ đạt** sau sửa collector; 32/32 Android unit tests follow-up là phép kiểm source runtime không đổi trước đó. `DISPATCH_DEVICE_CLEANUP.json` ghi cleanup sau control; `DEVICE_CLEANUP.json` lúc 12:00 là snapshot cũ. Batch r6 đang giữ thiết bị/server độc quyền; cleanup cuối sẽ ghi riêng khi batch đóng. Kết quả tổng hợp test không phải số liệu thực nghiệm.

### Candidate follow-up đã nhận

Đã kiểm lại PR #28 và fetch head `1f79ee93e9a52af2b21c82372f23a6ac684d3ceb`, cập nhật lúc 06:14 UTC. Android diff so với source APK đã đo chỉ có `PushSyncEnqueueAdapterTest.kt`; app runtime/AndroidTest source không đổi. Assertion được chuyển sang enqueued input theo contract. **Đã chạy `:app:testDebugUnitTest` trên source follow-up: 32 tests, 0 failure/error/skip, exit 0**, kết thúc 09:42:30 UTC, sau cleanup batch r3 và trước replacement r4. [UNIT_FOLLOWUP.json](UNIT_FOLLOWUP.json) ghi source, diff và hash XML/build log. Lỗi 31/32 trong PREFLIGHT là kết quả lịch sử ở source cũ, đã được follow-up giải quyết.

Manifest upstream vẫn NOT_READY/gate false, chưa có APK/checksum freeze. Không cài APK mới; các lượt đo giữ app/source `9e7e55b` và hash đã kiểm, không đổi provenance theo head tài liệu mới. Build chạy trong worktree riêng ngoài cửa sổ quan sát.
