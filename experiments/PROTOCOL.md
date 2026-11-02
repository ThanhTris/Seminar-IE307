# Protocol thực hiện E01–E06 — SEM-16

Phiên bản **1.0.0**, soạn ngày **03/11/2026 (UTC+7)**, Vinh (`Vinh5905`). Đây là thiết kế thao tác và nghiệm thu run; **chưa có kết quả thực nghiệm SEM-16**. Nguồn định mức là [EXPERIMENT_PROTOCOL](../docs/EXPERIMENT_PROTOCOL.md), [PLAN](../docs/PLAN.md) và [yêu cầu SEM-16](../tasks/backlog/SEM-16.md). Bản này cụ thể hóa cách chạy, không thay số lượt/cửa sổ cốt lõi. [Lịch độc quyền](RUN_SCHEDULE.md) và [CHECKS](../docs/evidence/SEM-16/CHECKS.md) đi cùng phiên bản này.

## 1. Điều kiện trước khi chạy

- [ ] Nhận artifact/commit/CHECKS của các gate trong task thực hiện: [SEM-29](../tasks/backlog/SEM-29.md), [SEM-34](../tasks/backlog/SEM-34.md), [SEM-41](../tasks/backlog/SEM-41.md), [SEM-42](../tasks/backlog/SEM-42.md). Lịch dự kiến không thay thế gate.
- [ ] SEM-24 bàn giao exporter và manifest; API và event dùng cùng major **2.0.0** theo [API](../docs/API.md), [EVENT_SCHEMA](../docs/EVENT_SCHEMA.md). Không đổi tên event v1 thành v2 để tạo evidence.
- [ ] Với main, nhận candidate SEM-37: `app_commit`, `server_commit`, APK và `apk_sha256`, cấu hình scheduler/callback/retry/version guard/logging. Xác nhận APK đã cài chính là APK đó; ghi package/version/SDK thực tế. Chưa nhận candidate thì chỉ pilot/development.
- [ ] Cập nhật [hồ sơ thiết bị SEM-12](../docs/environment/DEVICES.md) tại setup: alias, Android/API/ColorOS nếu có, build, Google Play services, pin/nguồn, Battery Saver, tối ưu pin, mạng và tài nguyên host. Ngày 03/11 Vinh chưa có OPPO; ca OPPO giữ **NOT_RUN**, không suy cấu hình từ model hoặc dùng emulator thay mẫu OPPO.
- [ ] Kiểm riêng GET server từ thiết bị và Internet/FCM thật. ADB reverse, Google Play services hay TCP thông không chứng minh token/callback. Xác nhận token hiện hành bằng cơ chế local của SEM-33; không lưu token vào evidence public.
- [ ] Ghi baseline pin mặc định; cấu hình tối ưu pin thay đổi là nhóm riêng. Ngoài E03, kiểm idle thực tế và không để Doze ngoài ý muốn trở thành điều kiện nền không được ghi nhận.
- [ ] Giữ máy host hoạt động, không suspend emulator, không chạy build/tác vụ nặng đồng thời. Tránh telemetry liên tục; lưu log cục bộ, export sau run.

Đối chiếu source tại `6767b70` cho thấy callback/scheduler/server chưa đủ hợp đồng v2, chưa có exporter/candidate và cơ chế test race được kiểm nhận. Các lệnh cấu hình app/sender bên dưới là thao tác cần module cung cấp, **không phải CLI đã tồn tại**. Khi thiếu khả năng cấu hình run, cancel/drain, logging hay fault injection: ghi blocker cho task sở hữu, không giả lập thành run chính. Chi tiết ở CHECKS.

## 2. Ma trận lifecycle và giả thuyết cần đo

Mỗi hàng là một tình huống riêng; trạng thái process, task recent, package stopped, màn hình và idle là các trục khác nhau. Cột giả thuyết chỉ định điều cần kiểm, không cam kết thời điểm Android chạy.

| Trạng thái | Tạo tình huống và chứng cứ cần giữ | Periodic / push / hybrid: giả thuyết cần đo | Phạm vi và kết thúc |
|---|---|---|---|
| Foreground | Người dùng mở app; ghi activity resumed, PID và mốc mở | Quan sát riêng trigger → worker → cache; UI chỉ đọc Room, không tự GET | Control/setup; không tính là kết quả background; về Home trước run nền |
| Background bằng Home | Bấm Home, ghi app không còn resumed; ghi PID nếu còn và `stopped=false` | WorkManager có thể chạy khi đủ điều kiện; data-only có thể gọi callback rồi enqueue. Hybrid dùng chung engine | E01/E02/E04/E05/E06; không suy process chết chỉ vì app bị che |
| Process death | Home trước, ghi PID; nếu mô phỏng dùng `am kill`, kiểm PID biến mất và `stopped=false`; ghi rõ simulated, khác OS tự thu hồi RAM | Đo khả năng hệ thống tạo lại process, worker/receipt/applied, thời điểm và cache bền vững; không suy mọi process death đều giống nhau | Ca mô tả PUSH trên OPPO nếu khả thi, 5 phút; nếu PID không mất thì chưa tạo được tình huống |
| Vuốt recent | Người dùng mở Recents, vuốt đúng task; lưu hành động/video và kiểm task/PID/stopped sau vuốt | Đo hành vi thực trên OEM; xóa task không đủ bằng chứng force-stop hay process death. Nếu stopped thay đổi, báo đúng trạng thái quan sát | Ca mô tả PUSH trên OPPO nếu khả thi, 5 phút; không gộp với process death |
| Force-stop | Settings → Force stop hoặc `am force-stop`; ghi UTC, PID và package `stopped=true` | Không kỳ vọng periodic/push/hybrid vượt stopped state. Mọi phục hồi sau mở lại phải tách khỏi cập nhật khi app còn stopped | Ca bổ sung: ghi mốc người dùng mở lại, kiểm `stopped=false`, rồi mới quan sát phục hồi 5 phút; quy trình mục 7 |
| Màn hình tắt, chưa xác nhận Doze | Tắt màn hình, đọc trạng thái idle riêng | Chỉ kết luận theo idle đã đọc; không gọi màn hình tắt là Doze | Nhãn điều kiện phụ; không thay E03 |
| Doze được xác nhận | Dùng quy trình mục 6; lưu deep idle trước/trong/sau, mốc vào/ra và nguồn điện | Đo periodic và normal-priority push riêng trước/trong/sau idle; có thể bị trì hoãn; không suy luôn trễ từ mẫu nhỏ | E03: 2 lượt/trigger; giữ 20 phút và sau thoát thêm 10 phút |

Cơ sở: Android quản lý [vòng đời process](https://developer.android.com/guide/components/activities/process-lifecycle); API có hành vi riêng khi [task bị xóa](https://developer.android.com/reference/android/app/Service#onTaskRemoved(android.content.Intent)). Firebase ghi điều kiện Android phải [mở lại sau force-quit trong Settings](https://firebase.google.com/docs/cloud-messaging/flutter/receive-messages) (dùng mô tả nền tảng, không dùng callback Flutter cho app Kotlin). [Normal priority có thể trễ khi Doze](https://firebase.google.com/docs/cloud-messaging/android-message-priority). Tất cả hành vi OEM cụ thể phải kiểm trên máy thật.

## 3. Cấu hình cố định và reset giữa run

Baseline dự kiến của protocol này; candidate/pilot phải xác nhận thực hiện được trước main:

| Mục | Giá trị / quy tắc |
|---|---|
| Periodic | Interval **15 phút**, constraint `CONNECTED`; ghi flex thực tế, initial delay, unique work policy/name và WorkInfo ID từ candidate. Đăng ký một lần mỗi run có periodic; không re-register theo tick, không force-run job |
| Push | AndroidConfig v1, **data-only**, **normal** priority, không `notification`, không expedited/high priority |
| TTL | **86400000 ms = 24 giờ**, cố định mọi ca gửi push, nhất là E04; Admin SDK dùng milliseconds, HTTP v1 tương ứng `86400s`. Ghi giá trị thật ở manifest và send event; TTL không phải cửa sổ quan sát |
| Collapse | Không đặt `collapse_key` trong baseline; ghi rõ trường bị bỏ, kiểm payload sender thật. Không dùng collapse làm cơ chế tạo duplicate hoặc giả định mọi send đều đến |
| Retry | Dùng chính sách hữu hạn từ candidate SEM-39; ghi timeout, backoff, số attempt tối đa thật. Không tự đặt giá trị chưa được module thực thi |
| Mode | PERIODIC: không gửi push. PUSH: không còn periodic hoạt động. HYBRID: hai trigger được bật; E06 cố ý bỏ gửi push |
| Endpoint | Ghi base URL/transport thực tế; emulator có thể dùng `10.0.2.2`, OPPO cần LAN hoặc reverse đúng host. Không coi PC localhost là địa chỉ trực tiếp của OPPO |

[WorkManager không cam kết lịch chính xác](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work); interval tối thiểu 15 phút không phải chu kỳ đồng hồ chính xác. [TTL và collapse](https://firebase.google.com/docs/cloud-messaging/customize-messages/setting-message-lifespan) ảnh hưởng message pending; accepted không chứng minh delivered. Các lựa chọn TTL/collapse ở đây là cấu hình đo của SEM-16, không sửa contract hoặc source sender trong task này.

Checklist trước **mỗi** run:

1. [ ] Giữ quyền sử dụng độc quyền `(device_alias, package)` và snapshot server/store theo lịch. Không để người khác update snapshot hoặc gửi token của cùng app trong cửa sổ.
2. [ ] Export/đóng run trước; tắt trigger cũ, hủy unique periodic/one-time work của app demo bằng cơ chế module, đợi Operation hoàn tất và WorkInfo không còn RUNNING/ENQUEUED/BLOCKED cũ. Nếu không drain được, giữ run bị nhiễu và không bắt đầu mẫu mới.
3. [ ] Khôi phục idle/nguồn/mạng/pin về baseline; xác nhận package không stopped. Sau force-stop phải để **người dùng mở lại**, ghi mốc; không dùng force-stop làm cách reset thông thường.
4. [ ] Cấp `run_id` mới hợp lệ, phase, case/subscenario, alias, mode; mọi trigger chụp đúng run/config. Pending push cũ có thể còn tới 24 giờ: callback không được gán nó vào run hiện hành; phải từ chối trigger cũ. Không thể xác minh việc cô lập này thì chưa đủ điều kiện đo.
5. [ ] Đọc server version S và cache C. Setup MANUAL ngoài cửa sổ để đưa cache về S, xác nhận equal; sau đó drain MANUAL. Giữ version server tăng đơn điệu giữa run, dùng `update_id` mới cho từng update. Không hạ server version dưới cache, không xóa ledger/store giữa run. Nếu store gần đầy (giới hạn 100 items), export hết rồi tạo epoch môi trường riêng, reset cả store/cache và ghi nhận trước bộ run mới.
6. [ ] Lưu manifest baseline và clock offset, xác nhận exporter chạy/đọc được và không làm phát sinh sync. Ghi hash APK/commit/config; bật đúng mode, kiểm lịch thật và background bằng Home.
7. [ ] Ghi các mốc theo từng ca bên dưới. Setup không được tính vào cửa sổ; không mở app/bấm MANUAL để tạo thành công trong cửa sổ background. Mọi thao tác không dự kiến phải ghi vào manifest.

Sau mỗi run:

- [ ] Hết **đủ cửa sổ**, kể cả đã applied sớm; ghi end UTC/monotonic, version cuối và kết quả từng phase. Không xóa run timeout/lỗi.
- [ ] Đóng nhận trigger của run, drain/cancel đúng work của app; export log trước khi reset/xóa dữ liệu. Push muộn giữ run gốc, không tính vào run sau hay sửa kết quả trong cửa sổ đã đóng.
- [ ] E03: `unforce`, `battery reset`, khôi phục màn hình/nguồn; E04: khôi phục từng transport; force-stop: người dùng mở lại. Kiểm lại trạng thái, không chỉ dựa exit code.
- [ ] Thu clock offset cuối, evidence OS/work/cache và logs; lọc token/key/serial/thông tin cá nhân. Chỉ gỡ reverse/rule do run tạo; trả quyền dùng thiết bị/server sau khi cleanup xác nhận xong.
- [ ] Ghi cleanup Pass/Fail. Cleanup lỗi giữ thiết bị bị khóa và ghi blocker, không chuyển lịch sang run tiếp.

## 4. Checklist từng ca cốt lõi

Các cửa sổ dưới đây được giữ cả khi không thấy event; outcome thực tế do task chạy ghi. Mỗi lượt có manifest/events riêng; E01 là **một run 90 phút**, các cycle không phải các run độc lập.

### E01 — PERIODIC, emulator và OPPO

- [ ] **1 phiên 90 phút/máy**, mục tiêu **ít nhất 3 lần worker chạy tự nhiên**. Không gửi push.
- [ ] Sau baseline, đăng ký unique periodic một lần, lưu `periodic_registered` và WorkInfo thật; đưa app về Home. Bắt đầu phiên 90 phút khi **cả đăng ký và trạng thái background đã được xác nhận**; ghi mốc update server ngay sau đó và version target V. Chu kỳ chạy trước khi về Home giữ là setup, không tính thành lần chạy nền. Không điều chỉnh lịch để ép update nằm ngay trước tick.
- [ ] Giữ mạng/baseline trong đủ 90 phút. Thu từng `work_started` với `source=PERIODIC`, request ID riêng mỗi cycle và work ID thật; đối chiếu fetch/applied/unchanged với V/cache.
- [ ] Báo số cycle, lần cập nhật đầu, version cuối và trạng thái lịch. Thiếu 3 lần sau 90 phút: vẫn giữ run, ghi chưa đạt mục tiêu quan sát, lên run bổ sung riêng; không force-run bù. Không so latency E01/E02 như thử nghiệm cùng phase lịch.

### E02 — PUSH, emulator và OPPO

- [ ] **5 lượt/máy, 120 giây/lượt**. Mỗi lượt reset/drain, tắt periodic và xác nhận không còn lịch cũ; background bằng Home.
- [ ] Cửa sổ bắt đầu tại `server_updated` commit target V. Gửi một tín hiệu ngay sau update; giữ UTC update/send, `signal_id`, send attempt, TTL, kết quả thật. Nếu gửi lỗi hoặc unknown, giữ kết quả gửi đó; không đổi thành accepted.
- [ ] Trong đủ 120 giây, đối chiếu accepted/rejected/unknown → received → enqueued → started → applied. Ghi việc có/không notification do demo tạo. Không mở app tới khi cửa sổ đóng; chứng minh `snapshot_applied` trước mốc mở lại, UI chỉ kiểm cache sau đó.
- [ ] Report cập nhật đúng V trong cửa sổ, lỗi hoặc timeout; accepted một mình không thành công. Lỗi sender/config đã biết trước là blocker setup; lỗi phát sinh trong run giữ nguyên và phân loại, không lặng bỏ khỏi dữ liệu.

### E03 — Doze, PERIODIC và PUSH riêng trên emulator

- [ ] **2 lượt/trigger**, tổng 4 run. Mỗi run dự trù **5 phút baseline trước idle + 20 phút Doze đã xác nhận + 10 phút sau thoát**. Năm phút baseline là bổ sung thao tác, không rút 20+10 phút.
- [ ] Bật đúng một trigger; periodic đăng ký một lần trước baseline. Ghi event/idle trước thử. Vào Doze theo mục 6, chỉ đặt `t_idle_start` khi OS xác nhận deep IDLE.
- [ ] Ngay sau xác nhận idle: update server target V; với PUSH gửi data-only normal một lần, với PERIODIC không gửi push. Giữ idle **20 phút** từ `t_idle_start`, lưu kiểm trạng thái ở đầu/giữa/cuối (không polling liên tục).
- [ ] Thoát idle, xác nhận trạng thái đã thoát và đặt `t_idle_exit`; quan sát **thêm 10 phút** không mở app. Nếu không thoát đúng, ghi thời gian thực và sai lệch; không cắt cửa sổ để kịp lịch.
- [ ] Tách event trước/trong/sau idle. Nếu không xác nhận vào hoặc không giữ được điều kiện idle, ghi sai protocol, không gọi run đó là Doze hợp lệ; giữ log và chạy lại. Đây là Doze điều khiển bằng ADB, không phải đo thời gian hệ thống tự vào Doze.

### E04 — mất mạng, PERIODIC và PUSH riêng trên emulator

- [ ] **3 lượt/trigger**. Trước mỗi lượt xác nhận mạng hoạt động; sau đó ngắt tất cả transport có thể cấp đường tới server/FCM trên **guest** (Wi-Fi, cellular, Ethernet nếu có). Ghi cách ngắt và evidence guest không tới server/Internet. Không chỉ tắt Wi-Fi khi còn đường khác; không dừng server host.
- [ ] Tại `t_offline` đã xác nhận: giữ mất mạng **2 phút**. Host update server V trong khoảng này; PUSH gửi một tín hiệu normal TTL **86400000 ms**, lưu response thật; PERIODIC giữ lịch cũ và không push.
- [ ] Khôi phục đúng transport baseline ở `t_reconnect`, kiểm guest kết nối lại; quan sát **30 phút sau nối lại cho PERIODIC**, **5 phút cho PUSH**. Nếu nối lại muộn/kiểm kết nối mất thời gian, lấy mốc kết nối thực và giữ đủ thời gian sau đó.
- [ ] Thu work pending/constraints, fetch retry/failure nếu có, received/applied/version cuối. Offline có thể làm worker chưa bắt đầu nên không bắt buộc phải có retry; không có retry không đủ kết luận lỗi instrumentation.
- [ ] Tổng tối thiểu mỗi lượt: **32 phút PERIODIC**, **7 phút PUSH**. Không kết luận push hết TTL sau 2 phút hoặc accepted là đã delivered; không force-run periodic khi nối lại.

### E05 — PUSH + sync engine, emulator

**3 lượt cho từng kịch bản dưới đây + test logic của SEM-38/39**; tổng **9 run thiết bị**. Protocol gốc không ấn định window E05; SEM-16 chọn **15 phút/lượt**, từ send đầu tiên (A/B) hoặc lúc phát tín hiệu mới trong race đã thiết lập (C). Lưu cả setup race trước mốc này. Nếu pilot cần window dài hơn, sửa phiên bản trước main và dự trù lại lịch, không cắt thời gian ca khác.

| Kịch bản | Thao tác trong mỗi lượt | Tiêu chí cần kiểm |
|---|---|---|
| A — duplicate | Server commit V, cache < V. Gửi hai lần cùng tín hiệu logic (`signal_id` giữ nguyên, send attempt khác); nếu cần xác định client thực sự nhận trùng, dùng hook/test logic có nhãn | Phân biệt đã gửi 2 lần với callback nhận 2 lần. Không item trùng/không commit lại snapshot V; không buộc số GET bằng 1 khi cơ chế chưa hứa coalesce |
| B — hint cũ | Đưa cache tới V ở setup, tạo server V+1; gửi signal có hint V hoặc thấp hơn, ghi rõ version ba phía | Worker phải GET hiện hành, không áp dụng hint như data; cache cuối V+1, không giảm version. Stale **hint** không nhất thiết tạo `snapshot_stale` vì response có thể mới |
| C — bản mới khi worker chạy | Commit V+1 và kích hoạt worker; barrier/hook kiểm soát sau fetch V+1, trước worker kết thúc. Khi xác nhận work đang chạy, commit V+2 và gửi signal mới; lưu mốc barrier/signal/release và giữ đủ signal IDs | Sau release, cache phải tới V+2 trong cửa sổ, kể cả signal tới gần lúc work kết thúc; không giảm version/ghi trùng/bỏ mất tín hiệu mới |

- [ ] Tắt periodic; không có MANUAL trong cửa sổ. Với A/B chờ đủ 15 phút; với C không có barrier/hook hoặc không chứng minh overlap thì ghi **NOT_RUN** hoặc run sai điều kiện, không gọi là race đã kiểm.
- [ ] Hook/barrier để tạo race mang nhãn `INJECTED` và cấu hình cụ thể, tách khỏi số liệu timing tự nhiên E01–E04/E06. Không force-run job để tạo kết luận scheduler tự nhiên.
- [ ] Nhận kết quả test logic thật (commit/lệnh/output) cho duplicate, version guard/equal/stale và race từ SEM-38/39. Tín hiệu có thể coalesce/mất trước callback; giữ số send/receipt thật và chạy bổ sung nếu chưa tạo được duplicate. Không khẳng định DB write count nếu chỉ có event mà thiếu instrumentation tương ứng.

### E06 — HYBRID bỏ gửi push có kiểm soát, emulator

- [ ] **2 lượt, 45 phút/lượt**. Bật hybrid với một lịch periodic thật, drain push cũ; không force-run/re-register.
- [ ] Commit server target V ở `t_update`; dùng cơ chế SEM-40 cố ý bỏ gửi cho update này. Lưu `push_send_skipped`, reason `FAULT_INJECTION_SKIP`, không message/attempt FCM giả. Bắt đầu **45 phút** từ commit update.
- [ ] Giữ app background/mạng/baseline. Chứng minh applied target V có `source=PERIODIC` và nối được về work/fetch; không MANUAL hoặc push khác tạo thành công.
- [ ] Đóng đủ cửa sổ, report applied/timeout/lỗi thật. Đây là **không gửi có chủ đích**, không phải bằng chứng FCM mất tin và không chứng minh hybrid vượt force-stop.

## 5. Manifest, tính hợp lệ và phân tích

SEM-24 sở hữu template/exporter; phần này là yêu cầu bàn giao cho template, không tự tạo manifest đo giả. Mỗi run cần lưu tối thiểu:

- Nhận dạng: case/subscenario/repetition, `run_id`, `run_phase=pilot/development/main`, alias, mode, protocol version, người thao tác, điều khiển `INJECTED` nếu có.
- Build/config: OS/API/ColorOS thực tế; app/server commit, package/version/SDK, APK SHA-256, API/event schema version, interval/flex/unique policy, timeout/backoff/attempt limit, TTL/collapse thực, base URL/transport, pin/nguồn/Battery Saver/optimization, trạng thái màn hình/idle/process/stopped.
- Mốc: setup, start/end, update/send/offline/reconnect/idle enter/exit/user reopen theo ca; UTC và Android elapsed realtime cùng boot session khi có. Lưu planned window lẫn actual duration, version trước/target/cuối, update/signal/request/work IDs và send attempts.
- Kết quả: trạng thái thực hiện, hợp lệ/sai điều kiện và lý do, outcome trong cửa sổ, event muộn, cleanup, file manifest/events/OS evidence/logs, test logic E05; clock samples trước/sau và độ bất định.

| Tình huống | Xử lý dữ liệu |
|---|---|
| Chưa bắt đầu, thiếu OPPO/candidate/exporter/quyền gửi | **NOT_RUN** kèm blocker; không tạo events giả và không tính như run đã chạy |
| Đủ setup/điều kiện và full window, có applied đúng target | Run hợp lệ; success trong cửa sổ khi provenance đúng source và cache commit đã được xác nhận |
| Đủ điều kiện/full window nhưng không applied, hoặc lỗi sync/send trong run | Giữ run hợp lệ với timeout/failure/unknown tương ứng; giữ trong mẫu số, không gán latency 0; ghi riêng phân tầng lỗi gửi nếu có |
| MANUAL/UI auto-sync, trigger run khác, đổi build/config giữa run, host suspend, log mất, window bị cắt hoặc idle/network không tạo được | Giữ artifact, ghi run sai protocol/không đủ evidence và lý do; loại khỏi thống kê hợp lệ một cách công khai, lên lượt thay thế. Không loại chỉ vì kết quả không đẹp |
| Applied sau cửa sổ | Giữ timeout trong cửa sổ và báo late completion riêng; không kéo dài window hồi tố |
| E01 < 3 cycle sau 90 phút | Giữ dữ liệu hợp lệ nếu điều kiện đúng, ghi chưa đạt mục tiêu số lần quan sát; mở phiên bổ sung riêng |

Join event theo schema v2: `run_id + device_alias + signal_id` nối sender/callback; `request_id` nối logical sync và retry; work ID có thể lặp qua periodic cycles, mỗi GET có `network_call_id`. Không bắt message ID hai nguồn phải cùng chuỗi, không join chỉ bằng version/timestamp. `server_updated`, send accepted, received, enqueue, started và applied là các mốc khác nhau; missing event không tự thành một event/outcome mới.

Clock: trước/sau phiên thu ít nhất 3 mẫu request tới cùng clock server, lưu UTC gửi/nhận và UTC server tại response. Ước offset bằng server time trừ midpoint client, uncertainty ít nhất nửa RTT cộng độ phân giải đồng hồ; ghi thêm cách đồng bộ UTC host/guest. Health hiện không có server timestamp thì chưa có phép đo offset chỉ từ health; cần công cụ SEM-24 hoặc phép đo clock được ghi nhận riêng. Chưa kiểm soát offset/drift thì báo latency liên máy không đủ cơ sở, vẫn báo event/version/outcome. Chỉ trừ elapsed realtime trên cùng device và cùng `boot_session_id` khác null; không trừ qua reboot. Không lấy accepted làm receipt hoặc áp thứ tự tuyệt đối giữa clock hai máy.

Tỷ lệ cập nhật trong window = số run applied target / tổng run hợp lệ cùng case/subscenario/device/mode/build/config/phase. E01 báo riêng cycle/session, không chia giả thành 3 mẫu; E03 chia phase idle, E05 chia từng kịch bản. Median/min–max chỉ trên complete, đi kèm n_complete/n_total, timeout/failure/unknown và số run sai protocol/NOT_RUN riêng. Không trộn pilot/main, build khác hoặc timing INJECTED/tự nhiên. Đếm GET/retry/DB writes khi instrument đủ; không quy đổi mAh hoặc suy rộng mọi Android từ hai máy.

## 6. Quy trình Doze và hoàn tác

Theo [Android: Test your app with Doze](https://developer.android.com/training/monitoring-device-state/doze-standby). Đây là hướng dẫn cho task chạy, **chưa thực thi các lệnh thay đổi idle trong SEM-16**. Chọn serial local đúng alias; output thô giữ private. Đọc trạng thái nguồn/màn hình/idle trước thao tác và kiểm cú pháp `deviceidle help` trên image nếu khác phiên bản.

```sh
SEM16_ADB="$HOME/Library/Android/sdk/platform-tools/adb"
SEM16_DEVICE='<SERIAL_LOCAL>'
SEM16_PACKAGE='com.thanhtris.seminarie307'

# Thu trạng thái trước; lưu output riêng theo run, không công bố raw dump.
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys battery
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys deviceidle
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys deviceidle get deep

# App đã cấu hình, về Home, tắt màn hình; mô phỏng unplug để thử có kiểm soát.
"$SEM16_ADB" -s "$SEM16_DEVICE" shell input keyevent KEYCODE_HOME
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys battery unplug
"$SEM16_ADB" -s "$SEM16_DEVICE" shell input keyevent KEYCODE_SLEEP
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys deviceidle force-idle
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys deviceidle get deep
# Chỉ khi output xác nhận IDLE mới ghi t_idle_start và giữ đủ 20 phút.
# Update/gửi tín hiệu đúng trigger từ host theo checklist E03.

# Sau 20 phút, thu trạng thái trước thoát và hoàn tác ngay cả khi ca lỗi.
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys deviceidle get deep
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys deviceidle unforce
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys battery reset
"$SEM16_ADB" -s "$SEM16_DEVICE" shell input keyevent KEYCODE_WAKEUP
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys deviceidle get deep
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys battery
# Xác nhận đã thoát idle, ghi t_idle_exit, quan sát tiếp đủ 10 phút không mở app.
```

Giữ idle 20 phút và đọc trạng thái đầu/giữa/cuối bằng lệnh read-only trên; nếu bất ngờ ra idle, ghi sai điều kiện. ADB ép idle được ghi `idle_method=adb_force_idle`; khác `jobscheduler run -f` ép worker. Restore trạng thái màn hình/nguồn thực sau quan sát, kiểm battery simulation đã gỡ; không thay whitelist/idle constants để tạo kết quả dễ hơn. Nếu thao tác bị ngắt, ưu tiên `unforce`/`battery reset`, ghi cleanup và không để run kế tiếp nhận môi trường bẩn.

## 7. Ca mô tả lifecycle bổ sung và force-stop

Không tăng ma trận thành mọi tổ hợp mode × máy. Nếu có OPPO, dự trù **1 ca PUSH/5 phút cho mỗi process death, recent-swipe và phục hồi sau force-stop**; không gộp vào E02/main rate. Hiện tất cả **NOT_RUN — chưa có OPPO**. Battery Saver/reboot/TTL hết hạn/collapse là mở rộng sau cốt lõi.

Process death mô phỏng: app background, ghi PID, `am kill` và kiểm PID biến mất, package vẫn `stopped=false`. Recent-swipe phải thao tác người dùng, lưu task đã xóa và kiểm OS/PID/stopped; không dùng force-stop thay vuốt.

```sh
# Dùng các biến local đã chọn ở mục 6; chạy riêng từng ca, không chạy nối cả bộ.
"$SEM16_ADB" -s "$SEM16_DEVICE" shell pidof "$SEM16_PACKAGE"
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys package "$SEM16_PACKAGE"
# Chỉ cho ca process death mô phỏng, sau Home:
"$SEM16_ADB" -s "$SEM16_DEVICE" shell am kill "$SEM16_PACKAGE"
"$SEM16_ADB" -s "$SEM16_DEVICE" shell pidof "$SEM16_PACKAGE"
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys package "$SEM16_PACKAGE"
```

Force-stop là ca riêng:

1. [ ] Setup PUSH, tắt/drain periodic, lưu run/cache/version/token config local; ghi `t_force_stop` khi người dùng bấm Force stop hoặc lệnh dưới. Kiểm user/package `stopped=true`, PID mất. Không gọi thao tác này là process death thông thường.
2. [ ] Khi package đang stopped, chỉ ghi nhận trạng thái/thao tác; chưa bắt đầu cửa sổ quan sát phục hồi hoặc gửi tín hiệu thử mới. Theo protocol gốc, **chỉ quan sát tiếp sau khi người dùng mở app**; không thử dùng hybrid/ADB để vượt stopped state.
3. [ ] **Người dùng mở app qua launcher**, ghi `t_user_reopen` và xác nhận `stopped=false`. UI chỉ đọc cache; nếu startup có MANUAL/GET phải phân loại rõ và không gọi đó là phục hồi nền. Không suy tín hiệu pending từ trước chắc chắn được phát lại.
4. [ ] Về Home, ghi `t_background_after_reopen`; update mới + signal mới để kiểm hệ thống hoạt động lại, quan sát **5 phút** từ update mới. Phân biệt callback pending cũ, signal mới, worker và source; không dùng kết quả sau mở lại chứng minh sync lúc stopped.
5. [ ] Export cả mốc stopped/reopen/background, cache trước/sau và toàn bộ event; hủy/drain work thử, kiểm stopped false, trả nguồn/idle/mạng/pin baseline. Không để app stopped làm nhiễu E01 sau đó. Hybrid không phải cách vượt force-stop.

```sh
# Chỉ cho ca force-stop; đọc lại package state sau thao tác.
"$SEM16_ADB" -s "$SEM16_DEVICE" shell am force-stop "$SEM16_PACKAGE"
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys package "$SEM16_PACKAGE"
# Người dùng mở lại bằng launcher, ghi mốc thật rồi kiểm stopped=false.
"$SEM16_ADB" -s "$SEM16_DEVICE" shell dumpsys package "$SEM16_PACKAGE"
```

## 8. Bàn giao và thay đổi protocol

SEM-19 nhận ma trận/giới hạn; SEM-29 nhận E01 pilot; SEM-34 nhận E02 pilot; SEM-41 nhận E01–E06 emulator; SEM-42 nhận E01/E02 OPPO và ca mô tả nếu khả thi. SEM-24 nhận yêu cầu metadata, SEM-45/44 nhận quy tắc valid/window/clock/grouping. Những task này vẫn phải kiểm gate riêng trước dùng artifact.

Nếu pilot phát hiện cần đổi interval/TTL/window E05/hook/config, ghi version/ngày/delta và cập nhật lịch trước main; số lượt/cửa sổ cốt lõi vẫn theo nguồn. Sửa scheduler/callback/core/retry/version guard/logging sau đo phải chạy lại ca ảnh hưởng, nhóm build riêng. Đầu ra SEM-16 là protocol đã soát; thực nghiệm vẫn NOT_RUN đến khi các task thực hiện ghi evidence thật, không tự chuyển Project Done.
