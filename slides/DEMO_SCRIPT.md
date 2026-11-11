# Kịch bản Lời dẫn và Điều phối Demo 4 phút — SEM-47

- **Người thực hiện:** Trang (`rosy179`).
- **Nhiệm vụ:** [SEM-47](../tasks/backlog/SEM-47.md) — Viết phần silent push và lời dẫn demo 4 phút.
- **Ngày cập nhật:** 11/11/2026 (UTC+7).
- **Đối chiếu base source:** `3fa78ac9ca00230253bb60008bedc16a7480b1fd` (`origin/main`).
- **Khung thời gian:** **Slide 6 (`07:00–11:00`, tổng 240 giây)** theo [PRESENTATION_PLAN.md](../docs/PRESENTATION_PLAN.md).
- **Phân vai cố định:**
  - **Trang (`rosy179`):** Dẫn lời liên tục cả 3 phần (Push, Periodic, Doze/Hybrid) để không ngắt quãng buổi nói.
  - **Trí (`ThanhTris`):** Thao tác thiết bị, chạy lệnh CLI và chuyển màn hình log/playback theo nhịp dẫn.

> [!IMPORTANT]
> **Nguyên tắc demo:**
> 1. Chỉ nói câu ở thì hoàn thành (*"đã nhận"*, *"đã áp dụng"*) khi dòng sự kiện hiển thị thật trên màn hình live hoặc trên bản ghi playback.
> 2. **Ngưỡng 30 giây** là quy tắc quản trị thời lượng thuyết trình (timebox 4 phút), **không phải cam kết kỹ thuật (SLA) của FCM**.
> 3. Hiện trạng dữ liệu tại base `3fa78ac`: Repo đã có dữ liệu thật của Manual M1 ([`M1.md`](../docs/evidence/SEM-28/M1.md)) và 2 lượt chạy Pilot Periodic E01 ([`SEM-29 CHECKS`](../docs/evidence/SEM-29/CHECKS.md)). Pilot Push E02 ([SEM-34](../tasks/backlog/SEM-34.md)) và video demo ([SEM-53](../tasks/backlog/SEM-53.md)) đang `Todo` (`Not run`) do Blocker B1 (chưa có Firebase credential/token thật). Khi chưa có run push bàn giao, phương án dự phòng là dùng `--validate-only` (TH5); chỉ dùng `[PLAYBACK]` push khi SEM-34/SEM-53 bàn giao.

---

## 1. Phân bổ 240 giây và Ngân sách Lời nói

*Tốc độ nói chuẩn: 130–140 từ/phút; để dành khoảng lặng cho thao tác máy và hiển thị log.*

| Phân đoạn | Mốc demo | Mốc toàn bài | Thời lượng | Chế độ | Ngân sách lời nói |
|---|---|---|---:|---|---:|
| **1. Baseline & Background** | `0:00–0:30` | `07:00–07:30` | 30s | **`[LIVE]`** | ~45 từ |
| **2. Push Trigger & Ngưỡng 30s** | `0:30–1:30` | `07:30–08:30` | 60s | **`[LIVE]`** (quá 30s chuyển **`[PLAYBACK]`** / **`[TH5]`**) | ~85 từ |
| **3. Periodic Tự nhiên** | `1:30–2:30` | `08:30–09:30` | 60s | **`[PLAYBACK — Pilot E01]`** | ~85 từ |
| **4. Doze / Hybrid Bỏ gửi Push** | `2:30–3:30` | `09:30–10:30` | 60s | **`[PLAYBACK — Skip-Push & Policy]`** | ~85 từ |
| **5. Kết nối & Chuyển vai** | `3:30–4:00` | `10:30–11:00` | 30s | **`[TỔNG KẾT]`** | ~45 từ |
| **Tổng cộng** | | | **240s** | | **~345 từ** |

*Biến thể 13 phút (rút demo còn 210s):* Giữ nguyên P1 (30s), P2 (60s), P5 (30s); rút P3 còn 45s (~65 từ) và P4 còn 45s (~65 từ).

---

## 2. Kịch bản Thao tác và Lời dẫn Chi tiết

### Phân đoạn 1 (`0:00–0:30`) — `[LIVE]` Baseline và Đưa App về Nền

- **Nhãn màn hình:** `[LIVE — emulator-01 — run-demo-01]`
- **Thao tác của Trí:**
  1. Chiếu màn hình app: chỉ vào thẻ trạng thái `Version cache: v1` và `Mode: PUSH` (chế độ ban đầu được cấu hình qua database metadata; bộ chọn mode UI là phần phụ thuộc SEM-36 đang Todo).
  2. Đối chiếu trạng thái token trên terminal qua logcat: `adb logcat -d -s FcmTokenManager` hiển thị `fcmTokenStatus = READY` kèm fingerprint 16 hex (giao diện `BulletinScreen` không in token để bảo mật).
  3. Bấm **Home** đưa app về nền (`stopped=false`); mở sẵn hai khung log Server và Android đã lọc theo `run-demo-01`.
- **Lời dẫn của Trang (45 từ, ~20 giây):**
  > “Bây giờ là 4 phút demo luồng dữ liệu từ trigger đến Room cache. Trên màn hình là app ở chế độ **PUSH**, cache ban đầu là **version 1**. Trí vừa bấm nút **Home** đưa app về nền; logcat xác nhận token ở trạng thái `READY`, lịch định kỳ đã tắt.”

---

### Phân đoạn 2 (`0:30–1:30`) — `[LIVE]` Push Trigger và Ngưỡng 30 Giây

- **Thao tác của Trí:**
  1. Tại `0:30`, chạy lệnh cập nhật snapshot lên version 2 trên terminal server:
     ```sh
     npm run update -- --update-id update-demo-01 --run run-demo-01 --mode PUSH --device emulator-01 --title "Demo v2" --body "Bản tin cập nhật qua silent push"
     ```
  2. Tiếp tục chạy lệnh gửi push (đầy đủ tham số):
     ```sh
     # Chạy live khi có Firebase credential và token:
     npm run send-push -- --send --run run-demo-01 --mode PUSH --device emulator-01 --update-id update-demo-01 --signal-id signal-demo-01 --version 2
     ```
  3. Tô sáng `server_updated` và `push_send_accepted` trên log server. Đếm đồng hồ 30 giây:
     - **Nhánh A (Live hoàn tất $\le 30$s):** Tô sáng `push_received` $\to$ `work_enqueued` $\to$ `work_started` $\to$ `snapshot_applied` (v2) trên log Android; sau đó mở lại app đọc cache v2.
     - **Nhánh B (Live quá 30s):** Dừng chờ live ở giây thứ 30. *Nếu SEM-34/53 đã bàn giao:* mở tab `[PLAYBACK]` của run push. *Nếu chưa có run push (hiện trạng Blocker B1):* chuyển sang **TH5** chạy lệnh kiểm hợp đồng `--validate-only` và đối chiếu bằng chứng Room M1.

- **Lời dẫn của Trang:**
  - *Mở đầu (`0:30–0:45`, 25 từ):*
    > “Trí vừa cập nhật bản tin lên version 2 và phát silent push qua FCM. Log server đã ghi `server_updated` và `push_send_accepted` kèm `message_id`.”
  - *Nhánh A — Live hoàn tất trong 30s (`0:45–1:30`, 60 từ):*
    > “Phía Android nhận callback ở nền: log ghi `push_received`, adapter enqueue `SyncWorker` thành công (`work_enqueued`). Khi worker chạy, dữ liệu vượt qua Version Guard và commit `snapshot_applied` version 2. Chỉ sau khi cache đã đổi ở nền, Trí mới mở lại app: giao diện hiển thị ngay version 2 đọc từ Room mà không gọi mạng.”
  - *Nhánh B — Quá 30s chưa hoàn tất (`0:45–1:30`, 70 từ):*
    > “Đã qua 30 giây kể từ lúc gửi, live chưa có `snapshot_applied`. Xin lưu ý: **30 giây là ngưỡng điều phối thời lượng thuyết trình, không phải cam kết của FCM**. Do repo đang chờ SEM-34 nghiệm thu run push thiết bị vì vướng blocker credential B1, nhóm chuyển sang lệnh kiểm tra hợp đồng `--validate-only` và đối chiếu bằng chứng giao dịch Room M1 để quan sát luồng commit.”

---

### Phân đoạn 3 (`1:30–2:30`) — `[PLAYBACK]` Periodic WorkManager Tự nhiên

- **Nhãn màn hình:** `[PLAYBACK — Pilot periodic E01: run-sem29-periodic-emulator-20261107-r2 — Android 17 API 37 — run_phase: pilot, validity: NOT_ASSESSED]`
- **Thao tác của Trí:**
  1. Mở file `analysis.json` và `events.jsonl` của run pilot SEM-29 r2.
  2. Chỉ vào mốc đăng ký `periodic_registered` (`10:07:21Z`), lượt recovery của setup (`snapshot_applied` v3 lúc `10:08:35Z`), và quét qua **5 chu kỳ periodic tự nhiên mới** (`10:23:58Z`, `10:39:08Z`, `10:58:22Z`, `11:14:22Z`, `11:34:23Z`).
- **Lời dẫn của Trang (80 từ, ~35 giây):**
  > “Sang phút thứ hai là bản ghi **pilot Periodic E01** 90 phút trên máy ảo Android 17. Nhóm không ép chạy worker mà để WorkManager kích hoạt tự nhiên.
  > Bản ghi cho thấy: `periodic_registered` chỉ là mốc nhận lịch. Trong 90 phút có 6 lần worker chạy: lần đầu là recovery của setup áp dụng version 3, tiếp theo là **5 chu kỳ tự nhiên mới** cách nhau từ 15 đến 20 phút. Khi server không đổi, Version Guard giữ cache và ghi `snapshot_unchanged`, chứng minh chi phí chu kỳ rỗng.”

---

### Phân đoạn 4 (`2:30–3:30`) — `[PLAYBACK]` Giới hạn Doze và Hybrid Bỏ gửi Push

- **Nhãn màn hình:** `[PLAYBACK — Doze Mode (E03) & Fault Injection Skip-Push (E06) — SEM-40 / SEM-38]`
- **Thao tác của Trí:**
  1. Chiếu lệnh Doze `dumpsys deviceidle get deep` = `IDLE`, chỉ rõ trigger bị hoãn tới khi thoát idle.
  2. Chiếu lệnh CLI fault injection:
     ```sh
     npm run update -- --update-id update-e06-01 --run run-e06-01 --mode HYBRID --device emulator-01 --title "E06" --body "Skip push" --skip-push
     ```
     Tô sáng sự kiện `server_updated` đi kèm `push_send_skipped` (`reason: FAULT_INJECTION_SKIP`, `message_id: null`) và bảng ca kiểm `DUPLICATE_SIGNAL` của `PushInputPolicy`.
- **Lời dẫn của Trang (80 từ, ~35 giây):**
  > “Ở phút thứ ba, chúng ta quan sát giới hạn nền và cơ chế tự bảo vệ. Trong Doze Mode, hệ điều hành hoãn tác vụ ngầm cho tới cửa sổ bảo trì hoặc mốc thoát idle; nếu app bị Force-stop (`stopped=true`), broadcast bị chặn hoàn toàn.
  > Với kịch bản Hybrid bỏ gửi push, lệnh `--skip-push` tạo lỗi có kiểm soát: server tăng version nhưng ghi `push_send_skipped`. Nhờ chế độ **HYBRID**, chu kỳ Periodic tự nhiên tiếp theo sẽ bù đắp kéo dữ liệu. Nếu tín hiệu bị gửi lặp, `PushInputPolicy` chặn bằng `DUPLICATE_SIGNAL`.”

---

### Phân đoạn 5 (`3:30–4:00`) — `[TỔNG KẾT]` Kết nối lại 3 Câu hỏi và Chuyển vai

- **Thao tác của Trí:** Thu log, chiếu lại sơ đồ kiến trúc tổng kết trên Slide 6.
- **Lời dẫn của Trang (45 từ, ~20 giây):**
  > “Tóm lại, demo trả lời 3 câu hỏi:
  > - **Ai kích hoạt?** Periodic, Push data-only, hoặc Hybrid kết hợp cả hai.
  > - **Ai quyết định thời điểm chạy?** Hệ điều hành Android và WorkManager dựa vào Doze, mạng và quota nền.
  > - **Khi nào dữ liệu đổi?** Khi worker hoàn tất HTTP và giao dịch Room commit `snapshot_applied`.
  >
  > Tiếp theo, Vinh sẽ trình bày kết quả thực nghiệm.”

---

## 3. Ma trận Xử lý Tình huống Trực tiếp tại Bàn Demo

| Tình huống | Thao tác | Câu dẫn |
|---|---|---|
| **TH1: Live xong $\le 30$s** | Tô sáng từ `server_updated` đến `snapshot_applied`; sau đó mới mở app. | *“Trong cửa sổ live, app đã nhận tín hiệu và commit `snapshot_applied` ở nền. Giờ Trí mở lại UI đọc cache mới.”* |
| **TH2: Quá 30s chưa xong** | Dừng live ở 30s. Nếu có run push: mở `[PLAYBACK]`. Nếu chưa có: dùng TH5. | *“Đã hết 30 giây live; đây là ngưỡng thời lượng trình bày, không phải SLA của FCM. Nhóm chuyển sang bản ghi dự phòng có metadata.”* |
| **TH3: Trigger bị từ chối** | Tô sáng `push_received` + `trigger_rejected` (`MODE_DISABLED` / `DUPLICATE_SIGNAL`). | *“Callback đã nhận nhưng adapter từ chối xếp lịch đúng theo chính sách bảo vệ đầu vào.”* |
| **TH4: Sender báo lỗi** | Giữ log lỗi CLI (`push_send_rejected` / `push_send_failed_local`), mở playback. | *“Sender ghi nhận trạng thái từ chối rõ ràng, không báo thành công giả. Nhóm chuyển sang bản ghi playback.”* |
| **TH5: Chưa có Firebase thật (Blocker B1)** | Chạy `npm run send-push -- --validate-only ...`, đối chiếu test suite và Room M1. | *“Do credential thật đang ở blocker B1, nhóm trình diễn kiểm tra hợp đồng `--validate-only`, bộ test adapter đã pass và bản ghi đồng bộ M1.”* |

---

## 4. Giải thích 20 giây: Vì sao `Accepted` khác `Delivered` và `Applied`?

> “`push_send_accepted` kèm `message_id` chỉ chứng minh **máy chủ Google FCM đã tiếp nhận yêu cầu gửi**.
> - Từ FCM đến app (`push_received`): có thể bị hoãn bởi Doze, mạng rớt, Force-stop hoặc ROM OEM.
> - Từ callback vào hàng đợi (`work_enqueued`): có thể bị chặn nếu sai mode hoặc trùng tín hiệu.
> - Từ hàng đợi vào Room cache (`snapshot_applied`): worker phải có mạng, gọi HTTP thành công và vượt qua Version Guard trong giao dịch Room.
> Vì vậy, accepted không đồng nghĩa với delivered, và delivered chưa đồng nghĩa với dữ liệu đã được áp dụng.”
