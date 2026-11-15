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

Emulator sau kiểm đang cài APK development của revision candidate nêu trên, mode PUSH, cache 4, 0 work active. Lịch periodic cũ đã được hủy từ các task trước, smoke không đăng ký lại. Chọn run/alias/mode mới từ UI khi thực hiện lượt tiếp theo.

## Phần cần nhận để chạy main

1. **SEM-37 của Trung** sửa assertion còn fail theo review PR #28, build/test lại revision cuối, chốt APK/checksum và gate cùng pilot liên quan. Hash của kiểm development này là artifact đầu vào để đối chiếu, không tự thay thế freeze của SEM-37.
2. **Pilot theo từng loại ca** trên revision sẽ đo. SEM-29 là kết quả lịch sử trước thay đổi mode/provenance; E03–E06 trên revision hiện tại chưa có pilot đủ evidence. Requalify ca bị ảnh hưởng trước main theo protocol.
3. **Firebase** cho 19 slot PUSH thuộc E02/E03/E04/E05, gồm google-services.json, credential project, token emulator hiện hành. Tám slot PERIODIC/HYBRID skip vẫn cần candidate/pilot đúng ca.
4. **E05 race** cần hook/barrier và bằng chứng worker đang chạy khi tín hiệu mới tới. Đặt INJECTED cho nhóm đó và nhận test logic SEM-38/39. B1 còn thiếu thì giữ các slot push/race NOT_RUN.
5. **Export v2** được kiểm lại theo revision cuối, ghi raw/omission nếu có, giữ các event ngoài window. Main valid yêu cầu đúng candidate và metadata, các run sai điều kiện/timeout vẫn được giữ riêng theo kết quả thật.

Đầu vào thứ tự được ghi trong [REPRODUCE](REPRODUCE.md). Các ca main hiện Not run. Task SEM-41 tiếp tục Todo trên Project trong lần bàn giao này.

## Kiểm artifact bàn giao

36 tests exporter hiện có đạt. Đã kiểm 27 slot/582 phút, số lượt từng nhóm, 9 canonical event của control, 6 raw row đối chiếu 5 exported + 1 omitted, tái xuất ba file manifest/events/report giống từng byte. Có 36 link nội bộ và 4 block shell hợp lệ, JSON/JSONL và scan định danh/secret đạt. Candidate worktree giữ sạch tại revision đã build. `git diff --check` đạt.
