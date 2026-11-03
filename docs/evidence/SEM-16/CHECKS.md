# SEM-16 — Kiểm tra protocol và bàn giao

## Nhận dạng lần kiểm

- **Ngày thực hiện:** 03/11/2026 (UTC+7), Vinh (`Vinh5905`), hỗ trợ thao tác bằng Codex. Hạn gốc 30/10/2026 18:00 được giữ nguyên; không ghi lùi ngày hoàn thành.
- **Nhánh:** `codex/SEM-16-lifecycle-protocol`, kế thừa `codex/SEM-12-device-profile` theo yêu cầu Vinh; parent artifact `6767b704021a87b3234005f49f611b71f54553a7`. PR SEM-12 [#7](https://github.com/ThanhTris/Seminar-IE307/pull/7) còn mở khi bắt đầu; base `main` lúc fetch là `8f8d39e31b50fae946da050094eb3d3432fe540a`. Không sửa lại đầu ra SEM-12 trong SEM-16.
- **Đầu vào:** [task SEM-16](../../../tasks/backlog/SEM-16.md), [PLAN](../../PLAN.md), [EXPERIMENT_PROTOCOL](../../EXPERIMENT_PROTOCOL.md), [SCOPE](../../SCOPE.md), [API](../../API.md) và [EVENT_SCHEMA](../../EVENT_SCHEMA.md) contract 2.0.0, [deadline](../../../tasks/DEADLINES.md), yêu cầu các task nhận bàn giao. SEM-16 không có gate bắt đầu/hoàn tất từ task khác.
- **Tham khảo bổ sung:** [DEVICES SEM-12](../../environment/DEVICES.md) và [CHECKS SEM-12](../SEM-12/CHECKS.md); đây là thông tin máy và blocker, không phải gate mới của SEM-16.
- **Đầu ra:** [PROTOCOL 1.0.0](../../../experiments/PROTOCOL.md), [RUN_SCHEDULE 1.0.0](../../../experiments/RUN_SCHEDULE.md), CHECKS này và checklist trong task SEM-16. Commit chứa các file này là bản artifact tài liệu; parent ở trên là code được đọc, không phải code đã đo.
- **Build/config:** không sửa hoặc build/cài APK, không chạy server/sender, không đổi idle/mạng/force-stop trong lần này. Thông số emulator trước đó thuộc SEM-12; không trình bày lại thành đo mới. Mọi ca E01–E06 và ca lifecycle trong bộ tài liệu này hiện **Not run**.

## Đối chiếu expected/actual

| Kiểm tra / thao tác đã làm | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| Đọc yêu cầu và phạm vi | Đủ 3 đầu ra, không lấn sang exporter/runtime/thống kê | Protocol/lịch/CHECKS có thật; exporter/manifest thực thuộc SEM-24, test logic thuộc SEM-38/39, chạy thật thuộc SEM-29/34/41/42 | Pass — tài liệu |
| Lifecycle matrix | Phân biệt foreground/background/process death/recent-swipe/force-stop/Doze và giả thuyết | Protocol mục 2 có cách tạo/xác nhận/trả trạng thái; màn hình tắt riêng; kiểm PID/task/stopped thay vì suy từ một thao tác | Pass — thiết kế |
| E01/E02 | 90 phút/máy, mục tiêu ≥3 cycle; 5 × 120 giây/máy | Protocol mục 4 giữ nguyên định mức emulator + OPPO, không force-run/re-register; E01 thiếu cycle không bị xóa | Pass — đối chiếu nguồn |
| E03 | 2 lượt/trigger, 20 phút Doze + 10 phút sau thoát | 4 run × 35 phút; thêm 5 phút baseline, không rút 20+10; có deep idle trước/giữa/sau, unforce/battery reset | Pass — đối chiếu nguồn và quy trình |
| E04 | 3 lượt/trigger, offline 2 phút, sau nối lại 30/5 phút; TTL cố định | 3 × 32 + 3 × 7 = 117 phút; guest offline, server host vẫn chạy; TTL 86400000 ms, tách reconnect và cleanup | Pass — thiết kế |
| E05 | 3 lượt/kịch bản + test logic; version không giảm, không ghi trùng/bỏ bản mới | 3 kịch bản × 3 = 9 run, window bổ sung 15 phút/lượt ghi rõ không có trong nguồn; race cần barrier/overlap evidence và nhãn INJECTED, nhận test logic thật | Pass — thiết kế; logic/runtime Not run |
| E06 | 2 × 45 phút, hybrid bỏ gửi có kiểm soát | Có `push_send_skipped`/`FAULT_INJECTION_SKIP`, cần chứng minh PERIODIC áp dụng target; không gọi FCM làm mất tin | Pass — thiết kế |
| Force-stop | Có mốc người dùng mở lại và cleanup; không tuyên bố hybrid vượt stopped | Protocol mục 7 có `t_force_stop`, `t_user_reopen`, `t_background_after_reopen`, kiểm stopped false, signal mới sau mở lại; ca mô tả tách E02 | Pass — thiết kế |
| Reset/run hợp lệ | Cô lập work/run/mode, giữ timeout/lỗi; không MANUAL/UI tạo kết quả nền | Có cancel/drain, run ID mới, reject pending push cũ, version monotonic, cleanup, valid/invalid/NOT_RUN, late completion và grouping/clock | Pass — thiết kế |
| Tính giờ và độc quyền | Ít nhất 10–12 giờ quan sát, pilot/main tách riêng, không chồng run | 33 run main: emulator 27/582 phút, OPPO 6/100 phút; tổng 682 phút = 11h22. Đã cộng slot, kiểm đủ capacity và không overlap từng ngày; khóa cả singleton snapshot store | Pass — kiểm phép tính/lịch |
| Pilot/main/deadline | Pilot 02–05/11, main 06–07/11, candidate cuối 05/11 | Lịch có catch-up 03/11, không nhận đã chạy 02/11; buffer, giờ export SEM-41 13:00/SEM-42 15:00 ngày 07/11; tràn giờ phải báo, không rút window | Pass — kế hoạch có điều kiện |
| Đối chiếu nguồn Android/Firebase | Quy trình idle/lifecycle/normal priority có cơ sở hiện hành | Đã mở tài liệu chính thức liên kết trong protocol ngày 03/11; dùng AndroidConfig v1 đúng phạm vi, không tự chuyển sang V2/BackgroundSync | Pass — tra tài liệu, không phải kiểm device |
| Cấu trúc file/link/shell/whitespace | Link relative đọc được, fence cân, snippet shell parse được, không secret/serial thật | Kiểm tĩnh 4 file SEM-16: 45 link nội bộ tồn tại, 4 block shell qua `sh -n`; bảng định mức/slot cộng đúng; scan credential/serial patterns và `git diff --check` đạt | Pass — kiểm file |
| Runtime E01–E06, FCM/Doze/network/race/OEM | Chỉ ghi Pass khi có manifest/log đo thật | Không tạo run/event/result giả, không chạy app hoặc thay trạng thái thiết bị trong SEM-16 | **Not run** |

Kiểm tĩnh chỉ xác nhận thiết kế và tính nhất quán của tài liệu, không chứng nhận khả năng scheduler/callback/cache đang chạy đúng. Các checkbox acceptance trong task phản ánh đầu ra SEM-16 đã được soát, không thay Status Project hoặc nghiệm thu các task thực nghiệm.

## Khác biệt source và blocker để task nhận chuẩn bị

Đối chiếu tĩnh tại parent `6767b70`, chưa tái hiện runtime, không sửa code của task khác:

| Mã | Phát hiện / evidence | Task xử lý và điều kiện gỡ |
|---|---|---|
| B1 | Vinh chưa có OPPO; hồ sơ SEM-12 giữ Not run cho máy thật | SEM-42/SEM-12 follow-up: có máy, người giữ/lịch độc quyền, OS/ColorOS/nguồn/mạng thật, pilot và candidate trước đo. Chặn run OPPO, không chặn bàn giao protocol SEM-16 |
| B2 | Chưa có template/exporter SEM-24 hoặc candidate SEM-37 trong cây source; chưa có offset clock được đo | SEM-24/37: nhận artifact/CHECKS, checksum APK, schema v2 và công cụ ghi metadata/clock; chưa đủ điều kiện gọi run main |
| B3 | [PeriodicSyncScheduler](../../../android/app/src/main/java/com/thanhtris/seminarie307/sync/PeriodicSyncScheduler.kt) ghi `periodic_scheduled`, tạo event async với ID của PeriodicWorkRequest mới trước xác nhận Operation; schema yêu cầu `periodic_registered` và ID lịch thật. [RealBulletinUiGateway](../../../android/app/src/main/java/com/thanhtris/seminarie307/integration/RealBulletinUiGateway.kt) dùng active run cố định, `setMode` chỉ ghi metadata, không thực hiện drain/cancel trigger | SEM-25/30/31/36/37: xác minh config/run isolation, đăng ký/cancel hoàn tất, work IDs/event v2. Protocol không đưa lệnh CLI app chưa tồn tại thành thao tác đã chạy |
| B4 | [FCM service](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/BulletinFirebaseMessagingService.kt) fallback run/mode và ghi token vào Logcat; [sender](../../../server/bin/fcm-sender.js) thiếu source/signal ID, có nhánh simulation/mock accepted. TTL source hiện 24 giờ nhưng payload/correlation chưa đạt v2 | SEM-32/33/35/38: run/mode validation, token local, sender thật và schema v2, từ chối pending signal sai run. Không công bố raw logcat, không lấy simulation làm accepted/delivery |
| B5 | Chưa có barrier/hook E05, test logic được nhận, hoặc fault injection SEM-40 đã kiểm nhận | SEM-38/39/40/36/37: công cụ race và skip có provenance, test logic output và config candidate. Không đủ overlap thì không báo E05-C Pass |

B2–B5 là điều kiện cần kiểm lại khi các module bàn giao, không dùng snapshot source ngày 03/11 để suy Status hiện hành của người khác. Quyền Firebase/token/send test thật còn phải xác minh ở setup theo SEM-13/33/35; SEM-16 không thử gửi.

## Cách soát lại và bàn giao

Từ root repo, đọc song song [bảng định mức gốc](../../EXPERIMENT_PROTOCOL.md#tập-ca-cốt-lõi-và-số-lượt) với mục 4 PROTOCOL và mục 2 RUN_SCHEDULE. Phép tính tái lập (không chạy experiment):

```sh
python3 -c 'emu=90+5*2+2*2*(5+20+10)+3*(2+30)+3*(2+5)+3*3*15+2*45; oppo=90+5*2; assert (emu,oppo,emu+oppo)==(582,100,682); print("emulator=582 min; OPPO=100 min; total=682 min (11h22)")'
git diff --check
```

Đọc lại bảng slot theo thứ tự giờ, kiểm mỗi slot ≥ window cần thiết, setup/drain/export có phần riêng và buffer không bị tính thành quan sát đã thực hiện. Snippet shell chỉ được kiểm cú pháp trong lần này; các lệnh ADB thay đổi idle/process/force-stop **chưa chạy**. Khi task thực nghiệm thực hiện mới lưu output/exit code và mốc thật theo run.

- **SEM-19:** ma trận lifecycle, giả thuyết/giới hạn OEM/force-stop và nguồn chính thức.
- **SEM-29:** E01 pilot, đăng ký ổn định, 90 phút và mục tiêu pilot ≥2 cycle theo task; không force-run.
- **SEM-34:** E02 pilot, 5 lượt/120 giây, xác nhận cache trước mở UI và các mốc tách biệt.
- **SEM-41:** checklist E01–E06, full windows, reset/cleanup, lịch emulator/candidate, valid/timeout/clock.
- **SEM-42:** E01/E02 OPPO, cấu hình thực và slot có điều kiện, ca lifecycle bổ sung khi khả thi; hiện blocker thiếu máy.
- **SEM-24/45/44:** yêu cầu manifest/event/clock, grouping, mẫu số, timeout/late và INJECTED; không sửa đầu ra do các task đó sở hữu trong SEM-16.

Đầu ra tài liệu SEM-16 đủ để đề nghị **Review**; chưa cập nhật Status Project, không tự đánh dấu Done. Các task nhận vẫn phải kiểm nhận artifact/version/CHECKS và gate riêng. Nhánh kế thừa SEM-12 để hỗ trợ thứ tự merge PR #7 trước, rồi PR SEM-16 vào `main`; không merge thay người duyệt.
