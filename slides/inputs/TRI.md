# SEM-46 — Mở bài và thao tác demo

Tuấn (`mtuan2491`) soạn ngày 09/11, chốt tài liệu ngày 12/11/2026 trên nhánh `codex/SEM-46-opening-demo`. Người trình bày mở bài và thao tác thiết bị là Trí theo PRESENTATION_PLAN. Tên file TRI.md giữ đúng đầu ra của task.

**Đầu ra tài liệu SEM-46 đã hoàn tất để review và bàn giao SEM-51.** Áp dụng quy tắc nhóm ngày 12/11 tại `cc2bd1c`, các đầu vào còn thiếu được ghi Not run/giới hạn trong CHECKS. Baseline đối chiếu là main `cc2bd1cbaecbd8e2e235af7985bbe720a6e8f1ff`. [Yêu cầu SEM-46](../../tasks/backlog/SEM-46.md), [quy tắc task](../../tasks/README.md), [CHECKS](../../docs/evidence/SEM-46/CHECKS.md)

## 1. Mở bài dự kiến trong 45 giây

| Mốc toàn bài | Nội dung | Người phụ trách |
|---|---|---|
| 00:00–00:40 | Đặt câu hỏi trigger-to-cache | Trí nói |
| 00:40–00:45 | Chuyển sang phần hai trigger | Trí bàn giao Trung |

Lời dẫn

> Khi ứng dụng bảng tin đang ở nền, tin mới trên server sẽ đến bộ nhớ đệm của điện thoại bằng cách nào? Nhóm xem xét hai cách kích hoạt đồng bộ. Một cách là kiểm tra định kỳ, cách còn lại là server gửi tín hiệu yêu cầu kiểm tra. Cả hai đi qua worker và cập nhật cùng cache. Trong phần demo, chúng ta sẽ theo dõi từ lúc có tín hiệu đến lúc dữ liệu được áp dụng. Các mốc thời gian và version giúp giải thích hành vi trên từng thiết bị.

Câu chuyển người

> Trung sẽ trình bày hai cách kích hoạt và vai trò của bộ lập lịch Android.

Thời lượng trên là ngân sách biên tập. Bấm giờ lời nói thực tế thuộc lần diễn tập sau khi ghép deck. Lượt mở bài giữ 5 giây chuyển người trong khung 45 giây. [PRESENTATION_PLAN](../../docs/PRESENTATION_PLAN.md)

## 2. Nội dung hình chiếu mở đầu

- Tiêu đề slide dùng câu hỏi “Khi app ở nền, dữ liệu mới đến cache lúc nào?”.
- Hình chính là chuỗi server → trigger → Android/worker → Room cache → UI đọc cache.
- Chân slide ghi case, device alias, run ID và nhãn LIVE hoặc PLAYBACK khi chuyển tới bằng chứng demo.

Hình dùng chung sơ đồ đã nhận trong SHARED_SYNC để giữ cách gọi component nhất quán. Bản deck cuối thuộc SEM-51. [Shared sync flow](../../docs/mechanisms/SHARED_SYNC.md)

## 3. Các mốc cần phân biệt khi dẫn demo

| Mốc | Câu diễn đạt dùng trong bài |
|---|---|
| `server_updated` | “Server đã lưu snapshot version mới.” |
| `push_send_accepted` | “FCM đã trả về kết quả chấp nhận yêu cầu gửi.” |
| `push_received` | “Callback trên Android đã ghi nhận tín hiệu.” |
| `work_enqueued` | “Yêu cầu work đã được hệ thống chấp nhận xếp lịch.” |
| `work_started` | “Worker đã bắt đầu thực hiện.” |
| `snapshot_applied` | “Snapshot version này đã commit vào Room.” |
| UI mở lại | “Màn hình đang hiển thị version đã lưu trong cache.” |

Mode PERIODIC dùng trigger định kỳ, PUSH dùng tín hiệu data-only normal priority, HYBRID nhận cả hai. Source MANUAL được ghi riêng khi chuẩn bị hoặc chẩn đoán. Cơ chế ứng dụng phải kiểm version hiện hành khi áp dụng snapshot. Những câu dẫn ở đây diễn giải contract và chỉ dùng thì quá khứ khi có event thật tương ứng trên màn hình. [SHARED_SYNC](../../docs/mechanisms/SHARED_SYNC.md), [EVENT_SCHEMA](../../docs/EVENT_SCHEMA.md)

Trong code tại baseline, UI và adapter lấy mode mặc định HYBRID khi thiếu key mode. Hàm `setMode` hiện được khai báo ở gateway, bộ điều khiển chọn mode thuộc SEM-36. Khi minh họa từ trạng thái mặc định, ghi mode HYBRID và source PUSH trên nhãn, đọc lại mode thực ở UI trước thao tác. Tên `work_enqueued` dùng ở phần mô tả contract, source hiện ghi dòng Logcat enqueue với work/request/run IDs và event Room. [Gateway](../../android/app/src/main/java/com/thanhtris/seminarie307/integration/RealBulletinUiGateway.kt), [adapter](../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushSyncEnqueueAdapter.kt), [SEM-47](../DEMO_SCRIPT.md)

## 4. Nguồn đã nhận và giới hạn vận hành

| Nguồn | Đã nhận / cần bổ sung |
|---|---|
| SEM-14 | Đã nhận shared flow và CHECKS, đủ để soạn phần cơ chế |
| Scope và kế hoạch nói | Đã nhận phạm vi bảng tin, khung 15 phút và demo 4 phút |
| SEM-47, Done | Đã nhận TRANG.md, DEMO_SCRIPT và CHECKS để phối hợp phần dẫn của Trang |
| SEM-28, Done | Đã nhận M1.md mô tả evidence manual sync vào Room |
| SEM-29, Done | Đã nhận manifest/events/analysis của pilot periodic r2, có thể dùng làm playback có metadata |
| SEM-37 | Candidate manifest/gate/CHECKS còn thiếu, kiểm candidate mới ghi Not run |
| SEM-34/53 | Run push/video chưa bàn giao, playback push ghi Not run |

Các giới hạn được bàn giao cùng tài liệu cho người ghép slide và người thao tác. [CHECKS SEM-46](../../docs/evidence/SEM-46/CHECKS.md), [TRANG.md](TRANG.md), [M1](../../docs/evidence/SEM-28/M1.md), [SEM-29](../../docs/evidence/SEM-29/CHECKS.md)

## 5. Phiếu cấu hình và bằng chứng cho lần trình diễn

| Thông tin cần pin | Trạng thái hiện tại | Nguồn cần nhận |
|---|---|---|
| App/server commit và APK của lần live | Not run, candidate SEM-37 chưa nhận | Candidate manifest và CHECKS khi có |
| Package | `com.thanhtris.seminarie307` | SCOPE và source |
| Mode của baseline source | HYBRID mặc định, đối chiếu giá trị UI tại setup | Gateway/adapter và bộ điều khiển mode khi nhận SEM-36 |
| Entry point update/send | `server/bin/update-cli.js`, `server/bin/fcm-sender.js` | FCM_SENDER và lệnh CONTRACT ở mục 6 |
| Run live, alias và version baseline/target | Ghi từ lần setup và response update, live hiện Not run | Manifest và log của lần thực hiện |
| Playback periodic có sẵn | `run-sem29-periodic-emulator-20261107-r2`, `emulator-main`, pilot, validity NOT_ASSESSED | Manifest/events/analysis SEM-29 |
| APK/source của playback periodic | App `95eeecb6bfa1a0963a95e581b5322c15443711e4`, server `a26646d`, APK SHA-256 trong manifest | Manifest và CHECKS của owner SEM-29 |
| M1 | Luồng MANUAL đã bàn giao, dùng cho phần commit/cache | Hồ sơ M1 SEM-28 |
| Playback push, Doze/E06 trên Android và video | Not run trong bộ evidence đã nhận | Bổ sung run/video có metadata khi bàn giao |

Metadata playback được giữ theo run gốc. Phiếu live được điền ở lần chuẩn bị thực tế. Những dòng Not run tiếp tục đi cùng CHECKS để người ghép deck chọn đúng nhãn trình diễn. [Manifest playback](../../experiments/runs/run-sem29-periodic-emulator-20261107-r2/manifest.json), [FCM_SENDER](../../docs/setup/FCM_SENDER.md)

## 6. Trình tự thao tác và lựa chọn đường trình diễn

Trạng thái chạy thiết bị/candidate mới trong SEM-46 là **Not run**. Trí chọn đường LIVE khi setup xác nhận được cấu hình thật, hoặc dùng CONTRACT và các evidence đã nhận trong cùng khung thời gian.

1. Ghi nhãn màn hình cho đường đang dùng, build/alias/run và bằng chứng tương ứng vào phiếu trên. Với LIVE, đối chiếu build/config thật trước khi ghi live-ready. Mở sẵn log theo run và che thông tin local trước khi chia sẻ màn hình.
2. Chọn run mới, đóng trigger của run trước, hủy lịch và drain work qua cơ chế được candidate bàn giao. Ghi work cũ còn active hoặc việc drain chưa xác nhận vào phiếu blocker trước khi tiếp tục chuẩn bị.
3. Chuẩn bị cache version N bằng thao tác MANUAL có nhãn ở ngoài cửa sổ live, chờ work hoàn tất. Đọc lại version server/cache và ghi baseline. Giữ server version tăng đơn điệu giữa các lượt.
4. Đọc mode thực tại setup. Baseline mặc định dùng HYBRID, source của tín hiệu là PUSH, payload/update cùng mode được chọn. Kiểm trạng thái lịch qua công cụ đã bàn giao, ghi mọi periodic còn active và nguồn của từng apply, đưa app về Home và ghi mốc quan sát. Ca E02 chuẩn dùng PUSH sau khi cơ chế mode/reset được kiểm trên build thực.
5. Chuẩn bị update N+1 và tín hiệu data-only normal priority qua entry point được bàn giao. Token và credential giữ trong cấu hình local. Trang dẫn nội dung, Trí thực hiện thao tác và ghi mốc gửi.
6. Chuẩn bị playback periodic r2 và evidence M1 đã nhận. Phần push thiếu cấu hình dùng CONTRACT. Phần Doze/E06 thiếu run dùng PROTOCOL và source/test đã bàn giao. Chốt đoạn trích phù hợp 1 phút mỗi phần cùng nhãn hiển thị.

Mode/source, run isolation, drain và version guard được đối chiếu theo SHARED_SYNC. Cách reset/cửa sổ/cleanup chi tiết dùng protocol. [SHARED_SYNC](../../docs/mechanisms/SHARED_SYNC.md), [PROTOCOL](../../experiments/PROTOCOL.md)

### CONTRACT khi thiếu Firebase hoặc playback push

Từ root repo, sau khi cài dependency `server/` theo SETUP, chạy lệnh sau. Các ID là giá trị minh họa có nhãn CONTRACT.

```powershell
node server/bin/fcm-sender.js --validate-only --run run-sem46-contract --mode HYBRID --device emulator-01 --update-id update-sem46-contract --signal-id signal-sem46-contract --version 1
```

Kết quả `status=validated_locally` xác nhận cấu trúc payload với `source=PUSH`, `mode=HYBRID`, `priority=normal`, TTL 86400000 ms. Tiếp theo mở M1.md và chỉ vào MANUAL, giao dịch Room và cache, giữ nhãn MANUAL M1 trên màn hình. Khi thiết lập được LIVE, dùng update/send cùng run/mode/device/update ID, lấy version thực từ response update, giữ log sender riêng với log store và lấy token từ file local theo hướng dẫn của owner. [M1](../../docs/evidence/SEM-28/M1.md), [SETUP](../../docs/SETUP.md), [FCM_SENDER](../../docs/setup/FCM_SENDER.md), [PUSH](../../docs/PUSH.md)

### PLAYBACK periodic đã nhận

Mở `analysis.json`, `manifest.json` và `events.jsonl` của r2 với nhãn `PLAYBACK — PILOT E01 — emulator-main — legacy-room-v1 — validity NOT_ASSESSED`. Run có 6 lần start trong window, gồm 1 recovery của request setup áp dụng v3 và **5 cycle periodic mới**. Trí đặt con trỏ ở request ID để phân biệt recovery với cycle mới. Clock của run uncontrolled, phần trình bày dùng mốc và counts owner đã ghi. [Analysis r2](../../experiments/runs/run-sem29-periodic-emulator-20261107-r2/analysis.json), [events r2](../../experiments/runs/run-sem29-periodic-emulator-20261107-r2/events.jsonl), [CHECKS SEM-29](../../docs/evidence/SEM-29/CHECKS.md)

## 7. Kịch bản phối hợp trong demo 4 phút

Trang giữ lời dẫn suốt phần demo. Trí thao tác thiết bị, log và playback theo tín hiệu của Trang. DEMO_SCRIPT của SEM-47 đã được nhận, các câu dưới dùng cùng năm phân đoạn và bổ sung lựa chọn phù hợp bộ evidence hiện có. [PRESENTATION_PLAN](../../docs/PRESENTATION_PLAN.md), [DEMO_SCRIPT](../DEMO_SCRIPT.md)

| Mốc trong demo | Việc Trí thực hiện | Câu dẫn hoặc tín hiệu phối hợp |
|---|---|---|
| 00:00–00:30 | Hiển thị LIVE khi setup đủ hoặc CONTRACT khi dùng kiểm payload. Với LIVE, chỉ run/device/mode thực và cache N, đưa app về Home | “Mình xác nhận cấu hình và version cache cho đường trình diễn đang chọn.” |
| 00:30–01:00 | LIVE dùng update/send theo cấu hình thật, ghi mốc và theo dõi event. CONTRACT chạy validate-only | “Mình đối chiếu kết quả của thao tác vừa thực hiện.” |
| 01:00–01:30 | Có applied thì mở lại UI sau mốc đó. Tới ngưỡng chuyển bản ghi thì dùng playback push đã nhận hoặc CONTRACT + MANUAL M1 | Dùng câu phù hợp trong bảng xử lý bên dưới |
| 01:30–02:30 | Mở timeline/log hoặc clip periodic đã chọn, đặt con trỏ ở đăng ký lịch, worker start và version | “Đây là PLAYBACK của run periodic trên thiết bị và build đang ghi ở màn hình.” |
| 02:30–03:30 | Hiện PROTOCOL E03/E06 và source/test skip-push ở bộ evidence hiện có. Chọn PLAYBACK khi nhận run có OS/source/target tương ứng | “Đây là phần quy trình và cơ chế đã bàn giao. Lần chạy Doze/E06 trên Android đang ghi Not run.” |
| 03:30–04:00 | Trở lại sơ đồ trigger-to-cache, sẵn sàng chuyển Vinh ở mốc 04:00 | “Các mốc trigger, worker và cache đã được đặt cạnh nhau để đối chiếu.” |

Ngưỡng biên tập chuyển playback là **30 giây kể từ lúc gửi** trong phần live. Người dẫn giữ mốc gửi thật khi nhận định ngưỡng đã tới. Khung 4 phút được giữ trong mốc 07:00–11:00 của toàn bài. [PRESENTATION_PLAN](../../docs/PRESENTATION_PLAN.md)

| Tình huống nhìn thấy | Câu dùng khi chuyển | Bằng chứng cần hiển thị |
|---|---|---|
| Applied có trước UI reopen | “Cache đã commit version N+1 ở mốc này. Bây giờ mở UI để đọc lại.” | Applied đúng source/run/version và mốc mở UI |
| Chưa có applied sau ngưỡng 30 giây, có playback push | “Trong cửa sổ live vừa rồi chưa ghi nhận cập nhật. Mình chuyển sang bản ghi đã chuẩn bị.” | Mốc gửi/live hiện tại, nhãn PLAYBACK và metadata run phát lại |
| Thiếu Firebase hoặc playback push | “Mình chuyển sang kiểm cấu trúc payload và hồ sơ giao dịch Room M1 đã bàn giao.” | `validated_locally`, nhãn CONTRACT và MANUAL M1 |
| Có accepted nhưng thiếu receipt/start | “Ở đây đã thấy kết quả gửi. Các mốc phía Android được xem riêng trong timeline.” | Mỗi event đang thực sự có trong log |
| Phần Doze/E06 chưa có run Android | “Mình trình bày quy trình và cơ chế skip đã bàn giao. Phần chạy thiết bị được ghi Not run.” | Nhãn PROTOCOL, source/test SEM-40 và trạng thái Not run |

Sau phần live, lưu log và outcome trong cửa sổ đã khai, giữ event tới muộn để phân tích. Cleanup theo cơ chế cancel/drain và khôi phục môi trường trong protocol, ghi người thao tác và kết quả vào phiếu run. [PROTOCOL](../../experiments/PROTOCOL.md)

## 8. Bàn giao SEM-51 và các cập nhật khi có run mới

- [x] Chốt mở bài 45 giây, phân vai và nội dung slide mở đầu.
- [x] Ghép thao tác cùng năm phân đoạn của SEM-47 và giữ ngân sách demo 240 giây.
- [x] Đối chiếu mode mặc định HYBRID, CLI và log token theo source hiện hành.
- [x] Chọn playback periodic/M1 có nguồn, bổ sung CONTRACT/PROTOCOL cho phần thiếu evidence.
- [x] Ghi candidate/live/video/diễn tập Not run và nguồn kiểm trong CHECKS.

SEM-51 nhận lời mở bài, phiếu thao tác, nhãn màn hình và các câu chuyển của tài liệu này. Khi candidate/run/video được bàn giao, điền phiếu cấu hình theo artifact đó và cập nhật phần Not run cùng CHECKS. [CHECKS SEM-46](../../docs/evidence/SEM-46/CHECKS.md), [SEM-40](../../docs/evidence/SEM-40/FAULT_INJECTION.md)
