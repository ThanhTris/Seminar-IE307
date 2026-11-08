# SEM-29 — Pilot periodic E01

## Nhận dạng và đầu vào

- Người thực hiện Vinh (`Vinh5905`), ngày 07/11/2026 (UTC+7). Hạn gốc 02/11/2026 22 giờ được giữ trong task.
- Nhánh `codex/SEM-29-periodic-pilot` được tạo sau khi pull main đến `a26646d72e8ee93f9e46a03b16d66f81be0552e0`.
- Đã nhận [SEM-16](../SEM-16/CHECKS.md), [SEM-24](../SEM-24/CHECKS.md), [SEM-30](../SEM-30/CHECKS.md), [SEM-31](../SEM-31/CHECKS.md), [PERIODIC](../../PERIODIC.md) và [ma trận chẩn đoán](../SEM-31/SCHEDULER_CHECKS.md). Project ghi các task nguồn Done. Ma trận runtime SEM-31 còn ghi Not run tại lúc nhận.
- App cho lượt r2 dùng source `95eeecb6bfa1a0963a95e581b5322c15443711e4`, gồm bản sửa quyền `9b636ca` và harness `95eeecb`. Server dùng `a26646d`. Candidate SEM-37 chưa bàn giao, phase là `pilot`.
- Emulator `emulator-main`, Android 17/API 37, Google `sdk_gphone16k_arm64`, ARM64, page size 16384, security patch 2026-07-05, Google Play services 26.33.32. Host macOS với JDK 21.0.11, Gradle 9.6.0, SDK/build tools theo source đã pin. Emulator dùng software rendering do host có áp lực bộ nhớ khi khởi động.
- APK r2 SHA-256 `ef60cd644f99e6da3c9c40648915606a753cf68908111f10f35a60a704e44cfd`. Đã đọc APK cài trên thiết bị và xác nhận hash khớp. Test APK SHA-256 `fae19edcee30ed18777f5d3982381486cffcc1e7f0d392413c5019eab931a4c3`.

## Phạm vi sửa và tái lập

Harness [PeriodicPilotControl](../../../android/app/src/androidTest/java/com/thanhtris/seminarie307/experiments/PeriodicPilotControl.kt) gọi `PeriodicSyncScheduler`, WorkManager và HTTP client thật. Các action `probe`, `diagnose`, `register`, `snapshot`, `cancel` được gọi ngoài cửa sổ quan sát. Source scheduler/worker/repository dùng code đã bàn giao. [REPRODUCE](REPRODUCE.md) ghi trình tự và lệnh chạy.

[PREFLIGHT.json](PREFLIGHT.json) lưu checksum hai build, kết quả nhánh quyền, state chẩn đoán, cấu hình WorkSpec và hash output instrumentation private.

Lượt đầu phát hiện client timeout trong khi shell emulator gọi `/health` thành công. App target 37 thiếu `ACCESS_LOCAL_NETWORK`. Bản sửa mở rộng phạm vi setup bằng ba file manifest, MainActivity và strings để xin quyền qua entrypoint bình thường. Android 17 áp dụng quyền runtime này cho kết nối LAN của app target 37. [Nguồn Android](https://developer.android.com/privacy-and-security/local-network-permission)

Nhánh từ chối đã được thao tác qua hộp thoại quyền và tái hiện probe thất bại. Sau khi cấp quyền qua hộp thoại của app, probe dùng `SnapshotRemoteDataSource` thật đạt. Cấu hình permission đã được thiết lập xong trước lượt r2.

## Expected và actual

| Hạng mục | Expected | Actual | Kết quả |
|---|---|---|---|
| Build app/test APK | Biên dịch trên toolchain đã pin | `assembleDebug`, `assembleDebugAndroidTest` đạt. Build đầu 6 phút 45 giây, build sau bản sửa đạt | Pass |
| Unit tests Android | Kiểm bộ test hiện có | 2 tests, 0 failure/error | Pass |
| Server | API v2 và kho riêng hoạt động | 9 tests đạt. Server loopback cổng 3000 với kho private riêng SEM-29 | Pass |
| APK cài thực tế | Hash APK thiết bị khớp file build | Đã so SHA-256 trước cửa sổ r2 | Pass |
| Quyền mạng Android 17 | Grant cho phép client gọi API v2 | Denied tái hiện lỗi. Granted qua UI, probe đạt | Pass trên API 37 |
| Đăng ký lại và cancel | Một ID active sau hai đăng ký, hủy hết active | `diagnose` dùng WorkManager thật đạt ở cả hai lượt setup | Pass |
| Cấu hình WorkSpec | Interval/flex 900000 ms, CONNECTED, UPDATE | Đã đọc WorkSpec thật. Initial delay 0, exponential backoff 30000 ms | Pass |
| Run đầu | Giữ lỗi và ghi đúng outcome | Quan sát 113100 ms rồi ABORTED vì NETWORK_ERROR, giữ 2 retry cùng request setup | Fail — đã lưu |
| Pilot r2 | Đủ 90 phút, ít nhất hai chu kỳ mới trong background | Từ 17 giờ 07 phút 30 giây đến 18 giờ 37 phút 30 giây. Android elapsed 5400050 ms, host monotonic 5400013 ms. Có 5 chu kỳ mới và 1 recovery của setup | Pass — emulator |
| Cleanup | Cancel/drain và giữ baseline | WorkInfo CANCELLED, 4 WorkSpec lưu trữ đều terminal, 0 active. Cache 3, Home resumed, stopped=false, mạng connected, idle ACTIVE. Server riêng đã dừng và gỡ lock | Pass |
| Bàn giao log pilot | Raw Room và manifest dùng được cho SEM-36 | `legacy-room-v1` được Trí chấp nhận ngày 08/11. Validator v2 trả `EVENT_FIELDS_MISSING`, producer v2 được bàn giao cho phần tích hợp SEM-36 | Accepted — legacy pilot |
| OPPO | Thực hiện theo phân công SEM-42 của Trí | Chưa có lượt OPPO trong bộ evidence SEM-29 | Not run — SEM-42 |
| Android API thấp hơn 37 | Kiểm nhánh quyền được bỏ qua theo guard SDK | Chưa có lượt runtime trên API thấp hơn 37 | Not run |

## Run và cách đọc dữ liệu

- [Lượt đầu](../../../experiments/runs/run-sem29-periodic-emulator-20261107/manifest.json) chạy từ 17 giờ 01 phút 46 giây đến 17 giờ 03 phút 39 giây, target 2, ABORTED/FAILURE. Hai `work_started` trong cửa sổ thuộc retry cùng request đã bắt đầu ở setup, số chu kỳ periodic mới bằng 0. [Phân tích](../../../experiments/runs/run-sem29-periodic-emulator-20261107/analysis.json)
- [Lượt r2](../../../experiments/runs/run-sem29-periodic-emulator-20261107-r2/manifest.json) từ 17 giờ 07 phút 30 giây đến 18 giờ 37 phút 30 giây, target 3, COMPLETED/SUCCESS cho phần quan sát emulator. Có 15 event Android gồm 2 setup, 12 trong cửa sổ và 1 cancel sau cửa sổ. Trong cửa sổ có 6 `work_started`, 1 `snapshot_applied`, 5 `snapshot_unchanged`. Event applied lúc 17 giờ 08 phút 35 giây thuộc recovery của request setup, tách khỏi **5 chu kỳ periodic mới**. [Phân tích](../../../experiments/runs/run-sem29-periodic-emulator-20261107-r2/analysis.json)

Các chu kỳ mới bắt đầu lúc 17 giờ 23 phút 58 giây, 17 giờ 39 phút 08 giây, 17 giờ 58 phút 22 giây, 18 giờ 14 phút 22 giây và 18 giờ 34 phút 23 giây. Khoảng cách thực tế có trì hoãn so với interval cấu hình 15 phút.

Lưu toàn bộ event cùng run, gồm setup và cleanup, giữ đúng tên cột/null/giá trị của Room. Android được khai báo `legacy-room-v1`, server giữ `2.0.0` trong file riêng. Script [validate_pilot.py](validate_pilot.py) tái tính từ elapsed time và request ID, kiểm hash, target, một work ID, cleanup và nguồn PERIODIC. UTC Android dùng để mô tả mốc, clock offset chưa được đo nên manifest ghi `controlled=false`.

[OS_CHECKS.json](OS_CHECKS.json) giữ dữ liệu đã lọc từ các mốc trước đăng ký, phút 30, phút 60, sau cửa sổ và sau cleanup. Các mốc đều ghi Home resumed, stopped=false, network connected và idle ACTIVE. Boot session trước/sau khớp. Dữ liệu WorkSpec được đọc để xác nhận 0 lịch active sau cancel. Test instrumentation chỉ dùng ngoài cửa sổ, các lần đọc DB/dump trong cửa sổ là thao tác quan sát.

Run ID thực tế chứa đoạn `emulator-20261107`, được regex serial của SEM-24 đánh dấu. Đây là nhãn ngày trong run ID đã chọn. Đã rà riêng chính xác giá trị run ID, giữ nguyên dữ liệu và kiểm định danh serial thật từ mapping private trên các trường còn lại. Dump OS, DB, mapping và output thô được giữ private.

## Nghiệm thu và bàn giao cập nhật ngày 08/11/2026

Trí đã xác nhận pilot emulator đủ nghiệm thu SEM-29, phần OPPO được chuyển hẳn sang SEM-42 của Trí. Bộ log SQLite raw và manifest pilot được chấp nhận bàn giao SEM-36 của Trung. Phản hồi đề nghị chuyển PR #19 sang Ready for review, sau merge nhóm sẽ cập nhật Project sang Done. [Phản hồi trên PR #19](https://github.com/ThanhTris/Seminar-IE307/pull/19#issuecomment-6721019303)

Producer Android còn thiếu mode/origin/device alias/boot/work attempt/network-call ID và cặp fetch events theo schema v2. Trung tiếp nhận dữ liệu pilot để nâng cấp producer trong SEM-36. Giá trị `canonical_v2_handoff_ready=false` trong analysis mô tả khả năng đọc bằng consumer canonical v2. Bộ dữ liệu hiện tại được nghiệm thu theo format `legacy-room-v1` cho handoff pilot.

Phần emulator đã đạt mục tiêu pilot và cleanup. Bàn giao SEM-36 gồm log legacy, manifest, lỗi quyền đã sửa và các trường producer v2 cần bổ sung. Tập chính cần candidate và producer logging hoàn thiện. SEM-29 đã đủ điều kiện nghiệm thu theo phạm vi được xác nhận.

## Giữ nguyên byte JSONL khi checkout

`.gitattributes` pin `*.jsonl text eol=lf` để giữ đúng SHA-256 của log Android và server trên Windows. Đã kiểm checkout với `core.autocrlf=true`, `core.eol=crlf`, đối chiếu từng file JSONL với blob Git và chạy lại audit hai run trong checkout đó.

## Lệnh kiểm artifact đã chạy

```sh
python3 docs/evidence/SEM-29/validate_pilot.py \
  experiments/runs/run-sem29-periodic-emulator-20261107
python3 docs/evidence/SEM-29/validate_pilot.py \
  experiments/runs/run-sem29-periodic-emulator-20261107-r2
git diff --check
```

Hai file `analysis.json` tái tạo giống từng byte từ script kiểm. JSON/JSONL, cú pháp Python/shell và link nội bộ được kiểm trước bàn giao. Serial/token/credential thực tế được rà trước khi đưa artifact vào Git. APK build và các capture thô giữ local.
