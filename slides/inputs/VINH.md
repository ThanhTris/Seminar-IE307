# SEM-48 — Nội dung phần kết quả của Vinh

**Bàn giao cho SEM-51, ngày 16/11/2026 (UTC+7).** Phần nói **11:00–12:45, tổng 105 giây**, theo [PRESENTATION_PLAN](../../docs/PRESENTATION_PLAN.md). Nội dung hiện dựa trên [SUMMARY SEM-43](../../experiments/SUMMARY.md) ở commit **`fce39b0df8086ede8d91d26171bf00436b83da31`**, PR [#31](https://github.com/ThanhTris/Seminar-IE307/pull/31) đang chờ merge khi nhận đầu vào. Main gốc `007a1aa`. Đây là input nội dung/ảnh/data, không phải deck cuối SEM-51.

## 1. Thông điệp và hình dùng trên slide 7

**Tiêu đề:** Pilot emulator: 8 hợp lệ, 12 INVALID.

Dùng [pilot_inventory.png](results/pilot_inventory.png) hoặc [SVG có text chỉnh được](results/pilot_inventory.svg) làm hình chính. Hình có tiêu đề, chú giải và giới hạn; không đặt thêm tiêu đề trùng. Giữ nhãn pilot, VALID/INVALID, build/profile và dòng “main n_complete/n_total=0/0”. Không cắt chú thích để người xem tưởng đây là tỷ lệ thành công main.

Những điểm Vinh chỉ trên hình:

- Tám pilot mới được producer ghi VALID/SUCCESS. E01 có 5 cycle mới trong một phiên 90 phút; cycle không phải các trial độc lập.
- Mười hai lần thử cũ vẫn hiện: 5 SUCCESS, 5 TIMEOUT, 2 ABORTED/FAILURE. Chúng INVALID do điều kiện đo/collector/baseline; không quy timeout bị nhiễu thành hành vi scheduler tự nhiên.
- Main chưa có run. Không có so sánh độ trễ, pin hoặc kết luận OEM từ biểu đồ này.

Không thêm slide thứ hai trong khung 105 giây. [main_coverage.png](results/main_coverage.png) / [SVG](results/main_coverage.svg) dành cho phụ lục hoặc thay hình chính khi cần nhấn mạnh phần NOT_RUN; hình chỉ đếm **slot kế hoạch**, không phải số run thất bại.

### Bảng nguồn cho notes và biểu đồ native

Đây là inventory theo **outcome gốc và validity**, không phải thống kê hiệu năng gộp các collector/epoch. Chi tiết 20 run, build/config/epoch/observer và link log nằm trong [pilot_inventory.csv](results/pilot_inventory.csv); script chỉ làm input đồ họa, không thay parser SEM-45.

| Case / emulator / mode | VALID/SUCCESS mới | INVALID/SUCCESS cũ | INVALID/TIMEOUT cũ | INVALID/ABORTED cũ | n_input |
|---|---:|---:|---:|---:|---:|
| E01 / PERIODIC | 1 | 0 | 2 | 1 | 4 |
| E03 / PERIODIC | 2 | 3 | 0 | 1 | 6 |
| E04 / PERIODIC | 3 | 2 | 1 | 0 | 6 |
| E06 / HYBRID | 2 | 0 | 2 | 0 | 4 |
| **Inventory SEM-41** | **8** | **5** | **5** | **2** | **20** |

| Main / thiết bị | Slot kế hoạch | Run main nhận được | n_complete/n_total main | Median/rate | Trạng thái |
|---|---:|---:|---|---|---|
| Emulator | 27 | 0 | 0/0 | N/A | NOT_RUN |
| OPPO | 6 | 0 | 0/0 | N/A | NOT_RUN |

Nguồn kế hoạch: [EMULATOR_PLAN](../../experiments/plans/SEM-41/EMULATOR_PLAN.json), [RUN_SCHEDULE](../../experiments/RUN_SCHEDULE.md). [main_coverage.csv](results/main_coverage.csv) là dữ liệu vẽ độ phủ; ô rate/median rỗng, không phải 0. `n_input=20` gồm mọi lần thử pilot; **khác mẫu số main**. Không gọi 8/20 là tỷ lệ thành công hoặc 0/33 là tỷ lệ thất bại.

`n_total` của main là số run main hợp lệ trong cùng case/device/build/config, gồm timeout hợp lệ; `n_complete` là số run áp dụng target đúng cửa sổ với provenance đủ. INVALID/missing được báo riêng. Ở snapshot này cả hai đều bằng 0; không lấy số slot kế hoạch hoặc số cycle thay mẫu số.

## 2. Lời dẫn chính — mục tiêu 1 phút 45 giây

Thời lượng dưới đây là **ngân sách nói**, chưa đo diễn tập. Mốc tính từ 11:00 của bài; có cả chuyển vai trong 105 giây. Chỉ giữ hình chính, không mở log/CLI trong phần này.

### 00:00–00:05 — nhận vai từ Trang

> Cảm ơn Trang. Mình tóm tắt kết quả và giới hạn của bộ dữ liệu.

### 00:05–00:25 — phạm vi dữ liệu

> Biểu đồ này là pilot trên một máy ảo Android, chưa phải tập main. Tám lượt mới được kiểm hợp lệ và ghi nhận thành công. Mười hai lần thử cũ vẫn giữ trên hình, gồm cả thành công, timeout và lượt bị dừng; chúng bị loại khỏi mẫu hợp lệ vì điều kiện đo không bảo đảm.

### 00:25–00:50 — quan sát periodic, Doze và mất mạng

> Ở phiên periodic chín mươi phút, có năm chu kỳ nền mới. Hai lượt Doze được điều khiển đều ghi nhận cập nhật sau khi thoát idle. Ba lượt mất mạng đều áp dụng phiên bản đích sau khi nối lại. Các quan sát này cho thấy đường đồng bộ phục hồi được trong những tình huống đã thử; không bảo đảm lịch chạy chính xác mỗi mười lăm phút.

### 00:50–01:10 — giới hạn của HYBRID

> Hai lượt hybrid chủ đích bỏ gửi push vẫn cập nhật nhờ periodic trong cửa sổ bốn mươi lăm phút. Đây là phép thử bỏ gửi có kiểm soát. APK chưa có Firebase, nên kết quả này không chứng minh FCM làm mất tin hoặc hai trigger thật đã hoạt động cùng nhau.

### 01:10–01:40 — phần chưa đo và điều chưa thể kết luận

> Tập main hiện chưa có run trên cả máy ảo và OPPO; các ô này là chưa chạy, không phải thất bại. Chúng mình chưa có kiểm độc lập cho bộ mới, và clock chưa đủ căn cứ để báo trung vị độ trễ. Vì vậy, phần này không xếp hạng periodic với push, không suy mức tiêu thụ pin từ số request, và không khái quát kết quả máy ảo cho mọi Android.

### 01:40–01:45 — bàn giao cho Tuấn

> Tiếp theo, Tuấn đối chiếu các quan sát này với nghiên cứu và giới hạn chung.

## 3. Bản rút còn 75 giây

Dùng khi chọn phương án 13 phút nói + 2 phút hỏi đáp; giữ nguyên hình và giới hạn chính. Các mốc vẫn là kế hoạch, chưa phải thời lượng diễn tập.

| Mốc | Lời nói |
|---|---|
| 00:00–00:05 | “Cảm ơn Trang. Mình tóm tắt evidence hiện có.” |
| 00:05–00:25 | “Tám pilot mới trên một máy ảo được kiểm hợp lệ và ghi thành công. Mười hai lần thử cũ vẫn giữ cùng outcome gốc nhưng INVALID do điều kiện đo. Đây chưa phải thống kê main.” |
| 00:25–00:50 | “E01 có năm chu kỳ nền mới trong chín mươi phút. Hai lượt Doze cập nhật sau thoát idle; ba lượt mất mạng cập nhật sau nối lại. Hai lượt hybrid bỏ gửi push phục hồi nhờ periodic, nhưng APK chưa có Firebase nên chưa kiểm hai trigger thật cùng hoạt động.” |
| 00:50–01:10 | “Main máy ảo và OPPO đều chưa chạy. Chưa có cơ sở báo median latency, so tốc độ hay pin, hoặc khái quát mọi Android. Các kết luận hiện chỉ thuộc build và điều kiện pilot đã ghi.” |
| 01:10–01:15 | “Tuấn sẽ đối chiếu các quan sát này với nghiên cứu.” |

## 4. Evidence dùng để trả lời và chú thích

Tám pilot mới dùng app **`9e7e55b76c646ff113a152022cc23317a202e533`**, server **`c77772e426c00ae464240f00942f8368c638aaa8`**, APK SHA-256 **`bde050c084d655c66f9f1497c57900a7f0efc39e12a9da55110771926c3f2e23`**. Emulator Google `sdk_gphone16k_arm64`, Android 17/API 37, Play services 26.43.30; `FIREBASE_NOT_CONFIGURED`, candidate gate false. Không thay source APK bằng commit của slide.

| Nhận xét nói ra | Run / nguồn có thể mở từ notes | Giới hạn cần giữ |
|---|---|---|
| E01 có 5 cycle mới/90 phút | [575a7a manifest](../../experiments/pilots/run-sem41-pilot-e01-1-20261115-575a7a/manifest.json) · [events](../../experiments/pilots/run-sem41-pilot-e01-1-20261115-575a7a/events.jsonl) | Một phiên pilot; không xem 5 cycle là 5 run |
| E03 apply sau thoát idle | [dc9cc9 audit](../../experiments/pilots/run-sem41-pilot-e03-1-20261115-dc9cc9/audit.json) · [7f63e0 audit](../../experiments/pilots/run-sem41-pilot-e03-2-20261115-7f63e0/audit.json) | Force-idle INJECTED; chưa kiểm PUSH hoặc mọi Doze tự nhiên |
| E04 apply sau reconnect | [PR_REVIEW_FIXES](../../docs/evidence/SEM-41/PR_REVIEW_FIXES.json), nối cả ba run và mốc apply | Không suy retry/backoff từ thời gian không có event |
| E06 deliberate skip, apply nguồn PERIODIC | [aa16ca events](../../experiments/pilots/run-sem41-pilot-e06-1-20261116-aa16ca/events.jsonl) · [8f734c events](../../experiments/pilots/run-sem41-pilot-e06-2-20261116-8f734c/events.jsonl) | Không gửi push, không kiểm FCM delivery hoặc vượt force-stop |
| Vì sao giữ 12 INVALID | [PILOT_RESULTS](../../docs/evidence/SEM-41/PILOT_RESULTS.json) · [audit collector](../../docs/evidence/SEM-41/SCHEDULER_OBSERVER_AUDIT.json) | Cả SUCCESS cũ cũng bị loại; không kết luận timeout bị nhiễu là hành vi app/OS tự nhiên |
| Vì sao không có median/rate main | [SUMMARY](../../experiments/SUMMARY.md) · [AUDIT](../../experiments/AUDIT.md) | 0 main; event boot_session_id null, clock controlled=false; chưa có CSV/audit đủ bộ |

### Câu hỏi dự kiến

- **Tám trên tám có nghĩa là đảm bảo thành công không?** Không. Đây là tám outcome của các pilot được producer review trên một build/emulator; không phải độ tin cậy thống kê hoặc kết quả main.
- **Main 0/33 có nghĩa thất bại hết không?** Không. 33 là slot kế hoạch; main n_complete/n_total=0/0, rate/median N/A. Không có run để kết luận thất bại.
- **Tại sao loại cả lượt SUCCESS cũ?** Collector dump scheduler có thể đổi timer trên image đã thử; qualification của mọi window bị ảnh hưởng được thu hồi, không chỉ timeout.
- **Có thể nói hybrid xử lý mất push không?** Chỉ nói periodic phục hồi khi chủ đích không gửi push trên profile không có Firebase. Chưa chứng minh FCM làm mất tin hoặc hybrid vượt Doze/force-stop.
- **CSV đã audit chưa?** Chưa nhận CSV/audit độc lập cho bộ mới. Draft SEM-45 #30 head `1a0c667` có 12 pilot cũ INVALID, không có tám pilot mới. Hai CSV trong thư mục results của SEM-48 chỉ là input mô tả/vẽ hình.
- **Có pin hoặc so sánh OPPO không?** Chưa. Không quy đổi request count thành pin; chưa nhận evidence OPPO để đối chiếu.

## 5. Handoff và cập nhật

[README results](results/README.md) ghi lệnh tái sinh PNG/SVG/CSV, đơn vị và giới hạn; [INPUTS](results/INPUTS.json) ghim hash nguồn, [CHECKS SEM-48](../../docs/evidence/SEM-48/CHECKS.md) ghi kiểm chứng. SEM-51 có thể dùng SVG/PNG hoặc dựng chart native từ CSV, giữ nhãn và thứ tự legend. Không lấy những ảnh này thay biểu đồ main từ CSV đã audit.

Biểu đồ completion/latency main hiện **NOT_RUN**. Khi nhận đúng main/CSV SEM-45 và audit SEM-44, cập nhật revision/hash/plots/lời dẫn; từng metric phải có device/build, n_complete/n_total, missing/timeout và căn cứ clock. Không sửa kết quả/phase cũ để làm đẹp slide. SEM-48 không tự sửa deck, report, SUMMARY hoặc dữ liệu của các owner khác.
