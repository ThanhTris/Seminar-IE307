# SEM-41 — Emulator main readiness và kiểm candidate

## Nhận dạng và đầu vào

- Vinh (`Vinh5905`) thực hiện ngày **15/11/2026, UTC+7**. Nhánh `codex/SEM-41-emulator-main` từ main `6e87411b60e8504d431cd06e577be94b7bb2244f`, sau merge SEM-34 PR #26. Hạn gốc 07/11/2026 13 giờ được giữ trong task.
- [SEM-16](../SEM-16/CHECKS.md) và [SEM-24](../SEM-24/CHECKS.md) đã nhận. Task SEM-41 hiện cho phép bắt đầu trước SEM-37, còn [protocol](../../../experiments/PROTOCOL.md) yêu cầu candidate trước khi ghi phase `main`.
- SEM-41 dùng **emulator**. Máy OPPO do Trí thực hiện tại [SEM-42](../../../tasks/backlog/SEM-42.md).
- Candidate đang ở [PR #28](https://github.com/ThanhTris/Seminar-IE307/pull/28), draft, branch `codex/SEM-36-37-52-trung-final`, head đã kiểm `051f6b04ae37f04cccf18d9c69f49ce4e26818d7`. Manifest nguồn ghim app `9e7e55b76c646ff113a152022cc23317a202e533`, server `c77772e426c00ae464240f00942f8368c638aaa8`, `candidate_status=NOT_READY`, `release_gate.passed=false`, APK/hash để null.
- Đã build đúng app revision ghim trong worktree detached, kiểm app/server source không đổi so với head PR #28. File nguồn của task Trung được giữ trong worktree riêng để kiểm, phần thay đổi SEM-41 gồm plan và evidence.

## Kiểm thực tế ngày 15/11

| Hạng mục | Expected | Actual | Kết quả |
|---|---|---|---|
| Toolchain máy Vinh | Có SDK/license để build revision candidate | JDK 21.0.11, Gradle 9.6.0, SDK 37, Build Tools 36.0.0 và license có sẵn | Pass |
| Assemble app/test APK | Có artifact từ source ghim | `assembleDebug` và `assembleDebugAndroidTest` tạo APK trên local | Pass — build artifact |
| Unit tests candidate | Toàn bộ suite đạt trước freeze | 32 tests, **31 pass / 1 fail**, command exit 1. `autoGeneratesRequestIdWhenMissingInPayload` còn đòi request ID trên `push_received`, nơi contract mới giữ null | Fail — trùng review lần 2 PR #28 |
| Cài đúng APK | Installed APK khớp hash file build | App SHA-256 `bde050c084d655c66f9f1497c57900a7f0efc39e12a9da55110771926c3f2e23`, hash thiết bị khớp. Test APK `6d38f794e7df9225926941394ae63db0afce9d365080ab3e69899d402992b4d8` | Pass — development |
| Migration Room | Giữ dữ liệu v1 khi lên v2 | Schema 1→2, 30 event trước/sau, mọi cột cũ giữ đúng giá trị, cache trước/sau 3 | Pass — development |
| Cấu hình qua UI | Nhận run ID/device alias/mode đúng thao tác | Nhập run `run-sem41-v2-smoke-20261115`, alias `emulator-main`, chọn PUSH qua giao diện. Periodic không active | Pass — development |
| Shared core và export v2 mới | Capture từ client/server thật, kiểm schema | Bấm manual sync, cache 3→4. Có work_enqueued/start/fetch_start/fetch_complete/applied, 5 event ANDROID source MANUAL được validator SEM-24 chấp nhận | Pass — development control |
| Omission report | Giữ lý do event chưa xuất được | Run smoke có 1 `periodic_cancelled` bị loại khỏi canonical và được ghi rõ trong report, raw Room giữ đủ 6 row | Pass — partial export được ghi rõ |
| Legacy sau migration | Các row thiếu provenance giữ format cũ | Lượt SEM-29 r2 xuất 0 canonical, báo 15 omitted do thiếu captured mode hoặc periodic_cancelled chưa hỗ trợ | Pass — legacy không được nâng nhãn |
| Firebase | Có project/config/token trước các ca PUSH | App báo `FIREBASE_NOT_CONFIGURED`; người dùng đã xác nhận chưa có cấu hình trong SEM-34 | Blocker |
| Candidate gate | Manifest đã freeze cùng APK/config/pilot | Nguồn SEM-37 vẫn NOT_READY, pilot theo revision này chưa đủ, 1 unit test còn fail | Blocker |
| Main E01–E06 | Đủ số lượt/window trên candidate | 27 slot PLANNED/NOT_RUN, chưa tạo run main | Not run |
| Cleanup | Thiết bị/server không còn work chạy của control | Home resumed, stopped=false, mạng connected, idle ACTIVE, 0 active sync work. Server riêng đã dừng và gỡ lock | Pass — development |

Lần build đầu trong OneDrive còn lỗi ghi Gradle cache `Operation timed out`. Đã kiểm lại cùng revision trong worktree local, không còn lỗi I/O; vẫn tái hiện 1 lỗi unit test. Lệnh build tổng trả exit 1 do test, các APK assemble đã được tạo. APK này phục vụ kiểm development, gate candidate tiếp tục false.

## Evidence và phạm vi dữ liệu

- [PREFLIGHT.json](PREFLIGHT.json) giữ build/hash, unit test failure, migration, export/omission, thiết bị và cleanup. Capture DB, build log và mapping giữ private trong `.local/sem41/`.
- [CONTROL manifest](../../../experiments/development/run-sem41-v2-smoke-20261115/manifest.json), [events](../../../experiments/development/run-sem41-v2-smoke-20261115/events.jsonl) và [export report](../../../experiments/development/run-sem41-v2-smoke-20261115/export_report.json) thuộc `run_phase=development`, `case_id=CONTROL`, `candidate_gate_passed=false`.
- Bộ control gồm 4 server update setup đưa store riêng từ 0 tới 4 và 5 event Android MANUAL. Các bản update có cùng run ID, target cuối 4. Server source không đổi giữa `decdef6` và `c77772e`, runtime dùng server v2 đã build từ source đó.
- [Raw Android](../../../experiments/development/run-sem41-v2-smoke-20261115/android-events-raw.jsonl), [omission report](../../../experiments/development/run-sem41-v2-smoke-20261115/canonical-export-report.json) và [state sau export](../../../experiments/development/run-sem41-v2-smoke-20261115/state-after.json) giữ provenance của kiểm serializer. `boot_session_id` của event vẫn null như producer đã xuất. Clock controlled=false, chưa tính latency giữa hai máy.
- [EMULATOR_PLAN.json](../../../experiments/plans/SEM-41/EMULATOR_PLAN.json) có 27 slot dự kiến, 34920 giây = **582 phút = 9 giờ 42 phút** quan sát. Setup, pilot, export, cleanup và buffer được tính thêm. Slot ID dùng `planned-slot-*`, run ID/app commit/APK cho main để null.

Sau control development lúc 03:00 UTC, emulator giữ APK development của revision candidate nêu trên, mode PUSH, cache 4, 0 work active. Lịch periodic cũ đã được hủy từ các task trước, smoke không đăng ký lại. Các lượt pilot ở phần dưới dùng run/alias/mode mới qua UI và cập nhật cache theo kết quả từng lượt.

## Phần cần nhận để chạy main

1. **SEM-37 của Trung** sửa assertion còn fail theo review PR #28, build/test lại revision cuối, chốt APK/checksum và gate cùng pilot liên quan. Hash của kiểm development này là artifact đầu vào để đối chiếu, không tự thay thế freeze của SEM-37.
2. **Pilot theo từng loại ca** trên revision sẽ đo. SEM-29 là kết quả lịch sử trước thay đổi mode/provenance; E03–E06 trên revision hiện tại chưa có pilot đủ evidence. Requalify ca bị ảnh hưởng trước main theo protocol.
3. **Firebase** cho 19 slot PUSH thuộc E02/E03/E04/E05, gồm google-services.json, credential project, token emulator hiện hành. Tám slot PERIODIC/HYBRID skip vẫn cần candidate/pilot đúng ca.
4. **E05 race** cần hook/barrier và bằng chứng worker đang chạy khi tín hiệu mới tới. Đặt INJECTED cho nhóm đó và nhận test logic SEM-38/39. B1 còn thiếu thì giữ các slot push/race NOT_RUN.
5. **Export v2** được kiểm lại theo revision cuối, ghi raw/omission nếu có, giữ các event ngoài window. Main valid yêu cầu đúng candidate và metadata, các run sai điều kiện/timeout vẫn được giữ riêng theo kết quả thật.

Đầu vào thứ tự được ghi trong [REPRODUCE](REPRODUCE.md). Các ca main hiện Not run. Task SEM-41 tiếp tục Todo trên Project trong lần bàn giao này.

## Kiểm artifact bàn giao

36 tests exporter hiện có đạt. Đã kiểm 27 slot/582 phút, số lượt từng nhóm, 9 canonical event của control, 6 raw row đối chiếu 5 exported + 1 omitted, tái xuất ba file manifest/events/report giống từng byte. Có 36 link nội bộ và 4 block shell hợp lệ, JSON/JSONL và scan định danh/secret đạt. Candidate worktree giữ sạch tại revision đã build. `git diff --check` đạt.

## Pilot thật không cần Firebase — đang thực hiện

Theo yêu cầu tiếp tục phần khả thi, đã bắt đầu batch tuần tự E01×1, E03 PERIODIC×2, E04 PERIODIC×3 và E06×2 trên APK development đã kiểm. Tổng cửa sổ dự trù **346 phút**, không tính setup/cleanup. Main vẫn 27 slot NOT_RUN. [PILOT_RESULTS.json](PILOT_RESULTS.json) là snapshot các lượt đã đóng; raw DB/OS dump gốc và mapping tiếp tục giữ private.

| Lượt đã đóng | Điều kiện/window | Kết quả thật | Đánh giá |
|---|---|---|---|
| [Setup lần đầu](../../../experiments/pilots/run-sem41-pilot-e01-1-20261115-89b884/manifest.json) | Chưa bắt đầu window; thao tác Ctrl+A không chọn hết text Compose, run ID bị nối vào giá trị cũ | Guard phát hiện metadata khác run ID mong đợi, ABORTED/FAILURE, cleanup đạt | INVALID; giữ [diagnostic và raw của run ID thực tế](../../../experiments/pilots/run-sem41-pilot-e01-1-20261115-89b884/setup-diagnostic.json). Runner đã sửa clear text bằng MOVE_END/DEL và kiểm UI text trước khi chọn mode |
| [E01 chạy lại](../../../experiments/pilots/run-sem41-pilot-e01-1-20261115-760217/manifest.json) | 10:24:39–11:54:39 UTC+7, Android elapsed **5.400.420 ms**, mạng connected, idle ACTIVE, app background, stopped=false | **0 cycle mới**, target 5 chưa applied, cache 4→4, **TIMEOUT**; 1 cycle trước Home được giữ ở setup | **INVALID sau audit baseline**: cùng version 4 nhưng cache/store mới có payload khác nhau. Giữ outcome/log thật và lên lượt thay thế |
| [E03 lượt 1](../../../experiments/pilots/run-sem41-pilot-e03-1-20261115-5db4eb/manifest.json) | 11:54:58–12:30:02 UTC+7, **2.103.340 ms**, đủ 5 phút baseline + 20 phút confirmed IDLE + 10 phút sau thoát | **SUCCESS**, target 6 applied bởi PERIODIC sau idle, cache 5→6, 1 cycle nền mới; không có event trong pha idle | VALID, cleanup đạt; 10 raw row = 9 canonical Android + 1 omitted cancel |
| [E03 lượt 2 bị dừng](../../../experiments/pilots/run-sem41-pilot-e03-2-20261115-0d277e/manifest.json) | 12:30:19–12:55:21 UTC+7, **1.502.720 ms**; đã giữ 20 phút IDLE nhưng chưa có đủ 10 phút sau thoát | ABORTED/FAILURE, `IDLE_RESTORE_NOT_CONFIRMED` tại lần đọc ngay sau wakeup; cleanup gọi lại khôi phục ACTIVE thành công | INVALID, giữ đủ log; không đổi thành run 35 phút. Có lượt thay thế mới bên dưới |
| [E03 lượt 2 thay thế lần đầu](../../../experiments/pilots/run-sem41-pilot-e03-2-20261115-c12a28/manifest.json) | 12:58:56–13:33:59 UTC+7, **2.103.370 ms**, đủ baseline/confirmed IDLE/post-idle | **SUCCESS** quan sát được, target 7 applied bởi PERIODIC sau idle, cache 6→7, 1 cycle nền mới | **INVALID sau audit baseline**: cache/store khác payload ở cùng version 6 trước window. Giữ 10 raw row = 9 canonical + 1 omitted; [transition](../../../experiments/pilots/run-sem41-pilot-e03-2-20261115-c12a28/idle-restore-1-transition.json) và outcome không bị sửa |
| [E04 lượt 1](../../../experiments/pilots/run-sem41-pilot-e04-1-20261115-a52b51/manifest.json) | 13:34:15–14:06:24 UTC+7, **1.929.360 ms**; offline **122.900 ms**, sau reconnect **1.801.250 ms** | **SUCCESS**, target 8 applied bởi PERIODIC sau nối lại, cache 7→8, 1 cycle nền mới | VALID, cleanup đạt; [offline proof](../../../experiments/pilots/run-sem41-pilot-e04-1-20261115-a52b51/offline-proof.json) xác nhận không có default network và guest HTTP không tới server |
| [E04 lượt 2](../../../experiments/pilots/run-sem41-pilot-e04-2-20261115-b5e415/manifest.json) | 14:06:41–14:38:50 UTC+7, **1.928.740 ms**; offline **123.010 ms**, sau reconnect **1.800.520 ms** | **TIMEOUT**, target 9 chưa applied, cache 8→8, 0 cycle nền mới | VALID, baseline payload khớp, offline/reconnect/cleanup đạt; giữ timeout trong mẫu hợp lệ |

E01 có 7 raw row: 5 canonical Android event thuộc setup/registration, 1 work_started sau window trong giai đoạn đóng run/control và 1 cancel sau window được report omitted; thêm 1 server update target. Work_started sau window được giữ trong log, không tính thành cycle trong 90 phút hoặc success của E01. [Audit](../../../experiments/pilots/run-sem41-pilot-e01-1-20261115-760217/audit.json) đối chiếu ID/count/source/work, đủ window, checkpoint và cleanup. Không có MANUAL/PUSH sync trong run. Ba file manifest/events/export report tái xuất giống từng byte. Clock controlled=false; không tính latency liên máy. Đã bổ sung boot alias collector từ hash kernel boot ID thực tế trong baseline private vào manifest, để hai mốc duration có cùng boot được observer xác minh tại từng checkpoint; [collector-boot](../../../experiments/pilots/run-sem41-pilot-e01-1-20261115-760217/collector-boot.json) ghi nguồn này. Event boot_session_id null được giữ nguyên, không tính event latency từ nó. Khi bổ sung metadata này, đã đối chiếu events/raw/omission/observation giữ nguyên từng byte.

Trong kiểm read-only giữa phiên E01, JobScheduler trả `ready` nhưng chưa có work_started nền. Đây là mô tả của một lượt đã được đánh dấu INVALID do baseline, chưa đủ kết luận lỗi OS/app; [Android JobScheduler](https://developer.android.com/reference/android/app/job/JobScheduler) có thể gom và trì hoãn job. E01 cần lượt bổ sung trên baseline đúng và requalify candidate cuối; không dùng kết quả SEM-29 lịch sử thay cho revision này. E03 hiện có một lượt hợp lệ phục hồi sau idle; lượt SUCCESS thứ hai bị loại khỏi mẫu hợp lệ vì baseline, giữ riêng outcome quan sát được.

### Sửa lỗi liên tục của store và audit lại baseline

Audit theo protocol mục 3.5 phát hiện runner cũ tạo store mới rồi seed đến cached version, nhưng giữ cache cũ. Cùng version/ETag chưa bảo đảm cùng nội dung: E01 cache version 4 có SHA-256 khác snapshot 4 của store r2; E03 thay thế version 6 có SHA-256 khác snapshot 6 của store r3. Đã hạ validity của **hai lượt này thành INVALID**, không sửa timestamps/version/outcome/events. [Proof E01](../../../experiments/pilots/run-sem41-pilot-e01-1-20261115-760217/baseline-content-proof.json) và [proof E03](../../../experiments/pilots/run-sem41-pilot-e03-2-20261115-c12a28/baseline-content-proof.json) đối chiếu capture SQLite với response lịch sử trong ledger. Các lượt còn lại được kiểm bằng cùng phép so sánh, không suy baseline chỉ từ version. E03 lượt 1 và E04 lượt 1/2 có payload/version baseline khớp; E04 lượt 2 đóng đủ window với TIMEOUT và vẫn giữ trong mẫu hợp lệ.

Commit `ffecae09411ce6113e6dc2c4259fb846cc1b54b1` bỏ seed store theo số version, yêu cầu retained store khi client có cache, từ chối server lùi dưới cache, và kiểm version **lẫn toàn bộ item payload** trước khi bắt đầu clock. Khi restart, `--store-dir` dùng lại chính ledger/snapshot đã đo; không xóa store/cache. Hash payload chuẩn hóa theo id và key JSON, không công bố nội dung cache. R2/r3 được ghi là hai epoch server riêng, không ghép timeline bằng version giữa chúng. Sau bootstrap không hợp lệ, E04 trở đi trong r3 có cache khớp snapshot của epoch r3 trước window và store được giữ liên tục.

Sau batch r3 sẽ giữ nguyên store r3 để chạy E03:2 và E01:1 thay thế, mỗi lượt đủ window mới (35 + 90 phút); không nối thêm thời gian vào run cũ. Đây là thêm 125 phút quan sát ngoài lịch ban đầu. Main vẫn 27 slot NOT_RUN.

Batch r2 dùng observer commit `0808b6fe98d6eb924785d9a3d78114ddaf58c802`, SHA-256 source ghi trong từng artifact; setup lỗi dùng observer cũ `9e38c0b`. Runner giữ nguyên code đã load trong quá trình đo. Sau khi r2 đã dừng và server/idle/work cleanup đạt, commit `056e7896fdd87d71fdd753f96736ae87e06ac378` sửa restore-idle thành chờ xác nhận ACTIVE tối đa 10 giây, ghi các mẫu transition, hỗ trợ chọn những lượt còn lại và tự ghi observer identity/offline proof. Batch r3 bắt đầu 12:58 UTC+7, E03:2 thay thế đã đóng SUCCESS rồi tiếp tục E04×3/E06×2 trên cùng app/test APK, kiểm cả hai hash và build lại nguồn server ghim trước batch. Run ID thay thế là `run-sem41-pilot-e03-2-20261115-c12a28`; đây là một run 35 phút mới, không nối thêm thời gian vào run bị dừng. E04 lượt đầu đã giữ đủ offline/post-reconnect và đóng SUCCESS; đang thực hiện các lượt lặp tiếp theo.

Review/export và baseline có 9 test tổng hợp; control có 5 test gồm transition và bảo toàn store/ledger. Cùng 36 test exporter hiện có, **50 tests đạt**. Các test mới chặn cùng-version/khác-payload, đọc đúng baseline lịch sử khi snapshot đã tiến, từ chối store mới khi có cache và không sửa ledger lúc resume. Test tổng hợp không phải kết quả thực nghiệm.
