# SEM-47 — CHECKS Nội dung Silent Push và Lời dẫn Demo 4 phút

## 1. Nhận dạng lần kiểm

- **Người thực hiện duy nhất:** Trang (`rosy179`).
- **Nhiệm vụ:** [SEM-47](../../../tasks/backlog/SEM-47.md) — Viết phần silent push và lời dẫn demo 4 phút.
- **Ngày lập và kiểm tra:** **11/11/2026 (UTC+7)**; hạn gốc trên bảng task là `08/11/2026 16:00 (UTC+7)`.
- **Base commit đối chiếu:** `3fa78ac9ca00230253bb60008bedc16a7480b1fd` (`origin/main`, đã bao gồm PR #20 SEM-32, PR #21 SEM-40, PR #22 SEM-33, PR #23 SEM-38 và PR #24 SEM-49).
- **Nhánh làm việc:** `codex/SEM-47-silent-push-demo`.
- **Phạm vi và bản chất kiểm chứng:**
  - Đây là task biên soạn nội dung thuyết trình và kịch bản điều phối demo (không sửa mã nguồn Android/server, không tạo APK mới và không giả lập kết quả chạy thực nghiệm).
  - Build/cài APK mới và chạy thực nghiệm E02/E03/E05/E06 trên thiết bị trong phạm vi task này: **`Not run` / không áp dụng**. Mọi mã nguồn, unit test và dữ liệu pilot dẫn trong tài liệu đều trỏ về đúng artifact/CHECKS của task sở hữu đã bàn giao trên `main`.
- **Đầu ra bắt buộc đã bàn giao:**
  - [`slides/inputs/TRANG.md`](../../../slides/inputs/TRANG.md): Nội dung Slide 4 (`04:00–06:00`, 120 giây, lời nói ~250 từ), sơ đồ cơ chế, bảng phân biệt payload `data-only` v1 vs `notification` tắt tiếng, cấu trúc payload/TTL 24h/token fingerprint, chính sách lọc `PushInputPolicy`, ranh giới sự kiện `accepted != delivered != applied`, 8 nguyên nhân trễ/mất tin và bộ câu hỏi phản biện.
  - [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md): Kịch bản điều phối và lời dẫn chi tiết 4 phút (`07:00–11:00`, 240 giây, lời nói ~345 từ) cho cả **Push**, **Periodic** và **Doze / Hybrid**, đóng nhãn rõ **`[LIVE]`** và **`[PLAYBACK]`**, lệnh CLI đầy đủ tham số, quy tắc **ngưỡng 30 giây đổi sang bản ghi dự phòng** (kèm phương án TH5 `--validate-only` khi chưa có run push), ma trận xử lý tình huống trực tiếp và câu trả lời chuẩn vì sao `push_send_accepted` khác `delivered`/`snapshot_applied`.
  - [`docs/evidence/SEM-47/CHECKS.md`](CHECKS.md): Hồ sơ kiểm chứng và bàn giao này.

---

## 2. Đối chiếu các đầu vào (Inputs & Dependencies)

Theo [bảng đầu vào SEM-47](../../../tasks/backlog/SEM-47.md), trạng thái thực tế của các task nguồn tại commit `3fa78ac` như sau:

| Loại cổng | Task nguồn | Người bàn giao | Artifact & CHECKS đối chiếu | Status trên Project | Cách tiếp nhận và xử lý trong SEM-47 |
|---|---|---|---|---|---|
| **Bắt đầu** | [SEM-15](../../../tasks/backlog/SEM-15.md) | Trang | [`SILENT_PUSH.md`](../../mechanisms/SILENT_PUSH.md), [CHECKS SEM-15](../SEM-15/CHECKS.md) | **Done** | Kế thừa phân tích `data-only` vs muted notification, `normal` vs `high` priority (deprioritization), giới hạn callback và 8 nguyên nhân trễ/mất tin; đồng thời chuẩn hóa endpoint `GET /api/bulletin` và cách diễn đạt theo [`INPUT_REVIEW.md` (SEM-19)](../SEM-19/INPUT_REVIEW.md). |
| **Hoàn tất** | [SEM-33](../../../tasks/backlog/SEM-33.md) | Trang | [`FcmTokenManager.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/FcmTokenManager.kt), [`PUSH.md`](../../PUSH.md), [CHECKS SEM-33](../SEM-33/CHECKS.md) | **Done** | Kế thừa vòng đời token (`STARTUP`/`ON_NEW_TOKEN`), cơ chế chỉ ghi `fcmTokenFingerprint` 16 hex (không lộ token thô), quy trình `adb exec-out run-as` ở bản debug, payload đã loại token, TTL `86400000 ms` và bảng phân biệt `accepted`/`received`/`applied`. |
| **Hoàn tất** | [SEM-38](../../../tasks/backlog/SEM-38.md) | Trang | [`PushInputPolicy.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushInputPolicy.kt), [`PushSyncEnqueueAdapter.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushSyncEnqueueAdapter.kt), [`PUSH_INPUT_CASES.md`](../SEM-38/PUSH_INPUT_CASES.md), [CHECKS SEM-38](../SEM-38/CHECKS.md) | **Done** | Đưa vào Slide 4 và kịch bản Demo cơ chế sổ cái 64 khóa `pushSeenSignalKeys` dưới `Mutex`: chặn redelivery bằng `trigger_rejected` (`DUPLICATE_SIGNAL`), nhưng bảo toàn tín hiệu có `version_hint` cũ và tín hiệu mới đến khi worker đang chạy (29/29 unit test JVM pass; E05 thiết bị ghi `Not run`). |
| **Hoàn tất** | [SEM-34](../../../tasks/backlog/SEM-34.md) | Vinh | `experiments/runs/<push-pilot-run>/manifest.json`, `events.jsonl`, `docs/evidence/SEM-34/CHECKS.md` | **Todo (`Not run` — Blocker B1)** | Chưa có artifact trên repo vì thiếu cấu hình Firebase project/credential/token thật (**Blocker B1** từ [SEM-13](../SEM-13/CHECKS.md)/[SEM-33](../SEM-33/CHECKS.md)/[SEM-35](../SEM-35/CHECKS.md)). Tài liệu giữ nguyên nhãn **`Not run — chờ SEM-34 / Blocker B1`**, cung cấp phương án TH5 (`--validate-only` và Room M1), tuyệt đối không bịa log E02. |
| **Tham chiếu liên quan** | [SEM-29](../../../tasks/backlog/SEM-29.md), [SEM-35](../../../tasks/backlog/SEM-35.md), [SEM-40](../../../tasks/backlog/SEM-40.md), [SEM-49](../../../tasks/backlog/SEM-49.md) | Vinh, Tâm | [`SEM-29 CHECKS`](../SEM-29/CHECKS.md), [`SEM-35 CHECKS`](../SEM-35/CHECKS.md), [`FAULT_INJECTION.md`](../SEM-40/FAULT_INJECTION.md), [`TAM.md`](../../../slides/inputs/TAM.md) | **Done** | Dùng dữ liệu thật của Pilot Periodic E01 (`run-sem29-periodic-emulator-20261107-r2` và run đầu `ABORTED`) cho phần `[PLAYBACK]` Periodic; khớp nối lời chuyển từ Tâm (cuối Slide 5) sang Trang (đầu Slide 6 Demo) và từ Trang sang Vinh (đầu Slide 7). |

---

## 3. Kết quả Kiểm tra Chi tiết (Expected / Actual)

| STT | Hạng mục kiểm tra | Expected | Actual / Evidence | Kết quả |
|:---:|---|---|---|:---:|
| 1 | **Đầy đủ file đầu ra riêng của SEM-47** | Có mặt `slides/inputs/TRANG.md`, `slides/DEMO_SCRIPT.md` và `docs/evidence/SEM-47/CHECKS.md`; không tự ý sửa file của task khác | Đã tạo đủ 3 file theo đúng quy ước thư mục; `git status` xác nhận chỉ thêm 3 file thuộc quyền sở hữu của SEM-47 | **Pass** |
| 2 | **Nội dung cơ chế Silent Push, Payload, TTL, Token & Giới hạn (Slide 4)** | Phân biệt rõ `data-only` v1 với muted/mixed notification; nêu đúng payload đã loại token, TTL `86400000 ms` (24h), quản lý token bằng SHA-256 fingerprint, chính sách `PushInputPolicy` và 8 giới hạn nền | [`slides/inputs/TRANG.md`](../../../slides/inputs/TRANG.md) Mục 2–4 trình bày đầy đủ, súc tích (~1.617 từ), có sơ đồ Mermaid, bảng so sánh 3 loại payload, JSON payload từ [`fcm_sender.js`](../../../server/src/fcm_sender.js) và mã trạng thái [`FcmTokenManager.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/FcmTokenManager.kt) | **Pass** |
| 3 | **Mạch lời dẫn Demo gói gọn trong 4 phút (`07:00–11:00`) và đánh dấu `[LIVE]` / `[PLAYBACK]`** | Có kịch bản liền mạch 240 giây cho cả Push, Periodic và Doze/Hybrid; Trang dẫn xuyên suốt, Trí thao tác; gắn nhãn `[LIVE]` và `[PLAYBACK]` rõ ràng ở từng phân đoạn; lời nói ~345 từ (~135 wpm) chừa thời gian thao tác máy | [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) Mục 1 & Mục 2 chia chính xác 5 phân đoạn (`30s + 60s + 60s + 60s + 30s = 240s`, kèm biến thể rút 30s còn `210s` cho phương án 13+2 phút) | **Pass** |
| 4 | **Ngưỡng 30 giây đổi sang video dự phòng không bị coi là bảo đảm của FCM** | Ghi rõ chuyển sang bản ghi dự phòng nếu chưa `snapshot_applied` sau 30 giây từ lúc gửi; giải thích 30 giây là ngưỡng thời lượng trình bày, không phải SLA của FCM | [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) Phân đoạn 2 (`0:30–1:30`) và [`slides/inputs/TRANG.md`](../../../slides/inputs/TRANG.md) Mục 4 khẳng định 30 giây là ngưỡng quản trị thời lượng thuyết trình | **Pass** |
| 5 | **Phương án dự phòng khi chưa có run push bàn giao** | Nêu rõ phương án khi chưa có run push (do SEM-34 vướng Blocker B1): dùng TH5 với lệnh `--validate-only` và Room M1; chỉ chuyển PLAYBACK push khi SEM-34/SEM-53 đã hoàn tất | [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) Phân đoạn 2 Nhánh B và bảng TH5 quy định rõ ràng | **Pass** |
| 6 | **Thao tác thiết bị và giao diện thực tế** | Không giả định UI hiển thị token hoặc có bộ chọn mode; kiểm token qua logcat / metadata Room; ghi rõ chuyển mode phụ thuộc SEM-36 | [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) Phân đoạn 1 bám sát `BulletinScreen.kt` (hiển thị `Version cache: v1` và mặc định `Mode: HYBRID` do chưa nối bộ chọn mode SEM-36); đối chiếu dòng log thật `FCM token stored: ... fingerprint=...` qua `adb logcat -s FcmTokenManager` sau bước khởi động lại app; giải thích trạng thái bền vững `fcmTokenStatus = READY` trong Room | **Pass** |
| 7 | **Lệnh CLI đầy đủ tham số** | Lệnh `npm run send-push` có `--send`, `--run`, `--mode`, `--device`, `--update-id`, `--signal-id`, `--version`; `npm run update` có đủ tham số; có phương án `--validate-only` | [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) Phân đoạn 2 và 4 ghi đầy đủ lệnh CLI, không để trống tham số gây `INVALID_ARGUMENT` | **Pass** |
| 8 | **Câu trả lời chuẩn "Vì sao `accepted` khác `delivered` và khác `applied`?"** | Tách biệt rõ `server_updated`, `push_send_accepted`, `push_received`, `work_enqueued`, `work_started` và `snapshot_applied`; có câu trả lời trực diện 20 giây | [`slides/inputs/TRANG.md`](../../../slides/inputs/TRANG.md) Mục 2, Mục 4 và [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) Mục 4 cung cấp phân tích 3 khoảng trống độc lập | **Pass** |
| 9 | **Dẫn chứng Pilot E01 chính xác nhãn và số liệu** | Ghi rõ nhãn `run_phase: pilot, validity: NOT_ASSESSED`, 5 chu kỳ mới + 1 recovery setup, khoảng cách 15 đến 20 phút (11:14:22 → 11:34:23 là tròn 20 phút) | [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) Phân đoạn 3 ghi đúng thông số artifact `run-sem29-periodic-emulator-20261107-r2` | **Pass** |
| 10 | **Kiểm tra liên kết nội bộ, cú pháp Markdown và `git diff --check`** | Toàn bộ đường dẫn tương đối trong 3 file trỏ tới file tồn tại; code fence/Mermaid cân bằng; không có lỗi whitespace | Chạy script kiểm tra toàn bộ link tương đối của 3 file và `git diff --check`: **0 broken links, 0 whitespace errors** | **Pass** |
| 11 | **Chạy Pilot Push E02 trên thiết bị ([SEM-34](../../../tasks/backlog/SEM-34.md)) & các ca thiết bị E03/E05/E06/OPPO** | Có manifest và `events.jsonl` từ thiết bị thật/emulator cho E02 và các ca mở rộng | Thuộc các task thực nghiệm [SEM-34](../../../tasks/backlog/SEM-34.md), [SEM-36](../../../tasks/backlog/SEM-36.md), [SEM-41](../../../tasks/backlog/SEM-41.md), [SEM-42](../../../tasks/backlog/SEM-42.md); hiện đang chờ cấu hình Firebase thật (**Blocker B1**) và candidate [SEM-37](../../../tasks/backlog/SEM-37.md) | **`Not run — Blocker B1 & chờ task thực nghiệm`** |
| 12 | **Quay video dự phòng ([SEM-53](../../../tasks/backlog/SEM-53.md)) và bấm giờ diễn tập ([SEM-54](../../../tasks/backlog/SEM-54.md))** | Có file video dự phòng trên Drive và biên bản bấm giờ 2 lần diễn tập | Thuộc [SEM-53](../../../tasks/backlog/SEM-53.md) (Trí) và [SEM-54](../../../tasks/backlog/SEM-54.md) (Tuấn) sau khi ghép deck [SEM-51](../../../tasks/backlog/SEM-51.md) và đóng gói [SEM-52](../../../tasks/backlog/SEM-52.md) | **`Not run — thuộc SEM-53 / SEM-54`** |

---

## 4. Lệnh kiểm tra thực tế đã chạy trên máy kiểm

```powershell
# 1. Tái kiểm tính toàn vẹn của 2 artifact Pilot Periodic E01 (SEM-29) được trích dẫn trong kịch bản PLAYBACK:
python docs/evidence/SEM-29/validate_pilot.py experiments/runs/run-sem29-periodic-emulator-20261107
python docs/evidence/SEM-29/validate_pilot.py experiments/runs/run-sem29-periodic-emulator-20261107-r2

# 2. Kiểm tra toàn bộ đường dẫn tương đối (relative markdown links) trong 3 file bàn giao của SEM-47:
python -c "import pathlib, re, sys; files=[pathlib.Path('slides/inputs/TRANG.md'), pathlib.Path('slides/DEMO_SCRIPT.md'), pathlib.Path('docs/evidence/SEM-47/CHECKS.md')]; pat=re.compile(r'\[[^\]]+\]\(([^)#]+)(?:#[^)]*)?\)'); missing=[(str(f), m.group(1)) for f in files for m in pat.finditer(f.read_text(encoding='utf-8')) if not m.group(1).startswith(('http://','https://','mailto:')) and not (f.parent / m.group(1)).resolve().exists()]; print('Checked links, missing:', len(missing)); sys.exit(1 if missing else 0)"

# 3. Kiểm tra định dạng diff và khoảng trắng thừa:
git diff --check
```

---

## 5. Xử lý phản hồi Review của ThanhTris (PR #25)

### 5.1. Xử lý Review lần 1 (commit `1e1276d` — [pullrequestreview-5853296736](https://github.com/ThanhTris/Seminar-IE307/pull/25#pullrequestreview-5853296736))

1. **Chưa có bản ghi dự phòng cho push:** Đã cập nhật Phân đoạn 2 (Nhánh B) và bảng tình huống TH5 trong [`DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) nêu rõ: do SEM-34 vướng Blocker B1 và SEM-53 chưa quay video, phương án dự phòng khi live quá 30s là dùng lệnh `--validate-only` và đối chiếu bằng chứng Room M1 ([`M1.md`](../SEM-28/M1.md)). Chỉ chuyển sang `[PLAYBACK]` push khi SEM-34/SEM-53 đã bàn giao.
2. **Thao tác UI thực tế:** Đã loại bỏ việc nói chỉ vào token trên UI (vì `BulletinScreen.kt` không in token để bảo mật).
3. **Lệnh CLI đầy đủ tham số:** Đã bổ sung đầy đủ các tham số bắt buộc cho `npm run send-push` (`--send`, `--run`, `--mode`, `--device`, `--update-id`, `--signal-id`, `--version`) và `npm run update`, tránh lỗi `INVALID_ARGUMENT`. Cung cấp thêm biến thể `--validate-only` cho kịch bản dry-run.
4. **Lời nói thuyết trình:** Đã tinh gọn lời nói xuống tốc độ chuẩn 130–140 từ/phút: Slide 4 còn ~250 từ (cho 120 giây); Slide 6 Demo còn ~345 từ (cho 240 giây) phân bổ đều theo 5 phân đoạn, đảm bảo Trí có đủ thời gian gõ lệnh CLI và chiếu dòng log.
5. **Các lỗi nhỏ & Dung lượng:**
   - Đã sửa nhãn PLAYBACK Periodic thành `run_phase: pilot, validity: NOT_ASSESSED`.
   - Đã chỉnh sửa khoảng cách giữa các chu kỳ thành "15 đến 20 phút (khoảng 11:14:22 đến 11:34:23 là tròn 20 phút)".
   - Đã sửa lỗi gõ "protocolo" thành "protocol".
   - Đã cô đọng cả hai file từ hơn 9.600 từ xuống còn khoảng 3.520 từ (~1.617 từ cho `TRANG.md` và ~1.903 từ cho `DEMO_SCRIPT.md`), tập trung vào ý chính và kịch bản để Tuấn ([SEM-51](../../../tasks/backlog/SEM-51.md)) dễ dàng ghép vào deck.

### 5.2. Xử lý Review lần 2 (commit hiện tại — [issuecomment-6793197880](https://github.com/ThanhTris/Seminar-IE307/pull/25#issuecomment-6793197880))

1. **Khớp mode hiển thị trên màn hình với code:**
   - Trong code hiện tại, `RealBulletinUiGateway.kt` chưa có nơi gọi `setMode` (chờ bộ chọn mode và controller của [SEM-36](../../../tasks/backlog/SEM-36.md)), nên khi bảng `sync_metadata` chưa có key `mode`, app lấy giá trị mặc định là **HYBRID**.
   - Đã cập nhật [`DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) Phân đoạn 1 và lời dẫn: màn hình ban đầu hiển thị `Mode: HYBRID`. Ở chế độ HYBRID, app cho phép nhận push bình thường (vượt qua kiểm tra mode guard trong `PushSyncEnqueueAdapter`), đồng thời là nền tảng cho kịch bản Doze/Hybrid ở các phân đoạn sau.
   - Bổ sung ghi chú thao tác: nếu môi trường có `sqlite3`, người chạy có thể gán `mode = PUSH` thủ công qua ADB, nhưng kịch bản chuẩn thống nhất dùng hiển thị `HYBRID` để chạy ổn định mà không phụ thuộc binary ngoài.
2. **Khớp dòng Logcat và trạng thái token với code:**
   - Sửa đúng nội dung logcat: [`FcmTokenManager.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/FcmTokenManager.kt) ghi dòng `FCM token stored: source=STARTUP, changed=..., fingerprint=<16-hex>` (không ghi chuỗi `fcmTokenStatus = READY`).
   - Làm rõ cơ chế lưu: `fcmTokenStatus = READY` được lưu bền vững trong bảng `sync_metadata` của Room. Vì Logcat chỉ ghi dòng `FCM token stored` tại thời điểm app khởi động và nhận token, kịch bản bổ sung bước chuẩn bị: khởi động lại app bằng `am force-stop` và `am start` trước khi bắt đầu demo để dòng log luôn mới nhất trong buffer, hoặc kiểm tra tính ổn định qua file debug token `.local/secrets/device-token.txt`.

---

## 6. Trạng thái Nghiệm thu & Handoff

- **Về gate hoàn tất:** [SEM-34](../../../tasks/backlog/SEM-34.md) (Pilot Push E02 của Vinh) là gate hoàn tất của SEM-47. Do SEM-34 hiện vẫn ở trạng thái `Todo` (`Not run` do Blocker B1), theo đúng nguyên tắc quản trị tiến trình của repo, **task SEM-47 được bàn giao ở trạng thái Review**; không tự ý chuyển sang `Done` cho tới khi SEM-34 bàn giao artifact.
- **Bàn giao mở khóa cho downstream:**
  - **[SEM-51](../../../tasks/backlog/SEM-51.md) (Tuấn — Ghép deck 15 phút, PDF và speaker notes):** Nhận [`slides/inputs/TRANG.md`](../../../slides/inputs/TRANG.md) (Slide 4) và [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) (Slide 6).
  - **[SEM-52](../../../tasks/backlog/SEM-52.md) (Trung) & [SEM-53](../../../tasks/backlog/SEM-53.md) (Trí):** Nhận lệnh CLI và kịch bản 5 phân đoạn để biên soạn runbook và quay video demo.
  - **[SEM-54](../../../tasks/backlog/SEM-54.md) (Tuấn):** Nhận khung bấm giờ 240 giây để điều phối 2 lần diễn tập.

Trạng thái đề xuất: **Review** (chờ SEM-34 hoàn tất gate; sẵn sàng cho SEM-51 ghép slide).
