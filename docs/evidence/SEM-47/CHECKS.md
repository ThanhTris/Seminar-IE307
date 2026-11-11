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
  - [`slides/inputs/TRANG.md`](../../../slides/inputs/TRANG.md): Nội dung Slide 4 (`04:00–06:00`, 120 giây), sơ đồ cơ chế, bảng phân biệt payload `data-only` v1 vs `notification` tắt tiếng, cấu trúc payload/TTL 24h/token fingerprint, chính sách lọc `PushInputPolicy`, ranh giới sự kiện `accepted != delivered != applied`, 8 nguyên nhân trễ/mất tin, tóm tắt khung Slide 6 và bộ câu hỏi phản biện.
  - [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md): Kịch bản điều phối và lời dẫn chi tiết 4 phút (`07:00–11:00`, 240 giây) cho cả **Push**, **Periodic** và **Doze / Hybrid**, đóng nhãn rõ **`[LIVE]`** và **`[PLAYBACK]`**, quy tắc **ngưỡng 30 giây đổi sang bản ghi dự phòng**, ma trận xử lý tình huống trực tiếp và câu trả lời chuẩn vì sao `push_send_accepted` khác `delivered`/`snapshot_applied`.
  - [`docs/evidence/SEM-47/CHECKS.md`](CHECKS.md): Hồ sơ kiểm chứng và bàn giao này.

---

## 2. Đối chiếu các đầu vào (Inputs & Dependencies)

Theo [bảng đầu vào SEM-47](../../../tasks/backlog/SEM-47.md), trạng thái thực tế của các task nguồn tại commit `3fa78ac` như sau:

| Loại cổng | Task nguồn | Người bàn giao | Artifact & CHECKS đối chiếu | Status trên Project | Cách tiếp nhận và xử lý trong SEM-47 |
|---|---|---|---|---|---|
| **Bắt đầu** | [SEM-15](../../../tasks/backlog/SEM-15.md) | Trang | [`SILENT_PUSH.md`](../../mechanisms/SILENT_PUSH.md), [CHECKS SEM-15](../SEM-15/CHECKS.md) | **Done** | Kế thừa phân tích `data-only` vs muted notification, `normal` vs `high` priority (deprioritization), giới hạn callback và 8 nguyên nhân trễ/mất tin; đồng thời chuẩn hóa endpoint `GET /api/bulletin` và cách diễn đạt theo [`INPUT_REVIEW.md` (SEM-19)](../SEM-19/INPUT_REVIEW.md). |
| **Hoàn tất** | [SEM-33](../../../tasks/backlog/SEM-33.md) | Trang | [`FcmTokenManager.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/FcmTokenManager.kt), [`PUSH.md`](../../PUSH.md), [CHECKS SEM-33](../SEM-33/CHECKS.md) | **Done** | Kế thừa vòng đời token (`STARTUP`/`ON_NEW_TOKEN`), cơ chế chỉ ghi `fcmTokenFingerprint` 16 hex (không lộ token thô), quy trình `adb exec-out run-as` ở bản debug, payload đã loại token, TTL `86400000 ms` và bảng phân biệt `accepted`/`received`/`applied`. |
| **Hoàn tất** | [SEM-38](../../../tasks/backlog/SEM-38.md) | Trang | [`PushInputPolicy.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushInputPolicy.kt), [`PushSyncEnqueueAdapter.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushSyncEnqueueAdapter.kt), [`PUSH_INPUT_CASES.md`](../SEM-38/PUSH_INPUT_CASES.md), [CHECKS SEM-38](../SEM-38/CHECKS.md) | **Done** | Đưa vào Slide 4 và kịch bản Demo cơ chế sổ cái 64 khóa `pushSeenSignalKeys` dưới `Mutex`: chặn redelivery bằng `trigger_rejected` (`DUPLICATE_SIGNAL`), nhưng bảo toàn tín hiệu có `version_hint` cũ và tín hiệu mới đến khi worker đang chạy (29/29 unit test JVM pass; E05 thiết bị ghi `Not run`). |
| **Hoàn tất** | [SEM-34](../../../tasks/backlog/SEM-34.md) | Vinh | `experiments/runs/<push-pilot-run>/manifest.json`, `events.jsonl`, `docs/evidence/SEM-34/CHECKS.md` | **Todo (`Not run` — Blocker B1)** | Chưa có artifact trên repo vì thiếu cấu hình Firebase project/credential/token thật (**Blocker B1** từ [SEM-13](../SEM-13/CHECKS.md)/[SEM-33](../SEM-33/CHECKS.md)/[SEM-35](../SEM-35/CHECKS.md)). Tài liệu giữ nguyên nhãn **`Not run — chờ SEM-34 / Blocker B1`**, cung cấp khung gắn `run_id` và lời dẫn minh bạch khi báo cáo, tuyệt đối không bịa log E02. |
| **Tham chiếu liên quan** | [SEM-29](../../../tasks/backlog/SEM-29.md), [SEM-35](../../../tasks/backlog/SEM-35.md), [SEM-40](../../../tasks/backlog/SEM-40.md), [SEM-49](../../../tasks/backlog/SEM-49.md) | Vinh, Tâm | [`SEM-29 CHECKS`](../SEM-29/CHECKS.md), [`SEM-35 CHECKS`](../SEM-35/CHECKS.md), [`FAULT_INJECTION.md`](../SEM-40/FAULT_INJECTION.md), [`TAM.md`](../../../slides/inputs/TAM.md) | **Done** | Dùng dữ liệu thật của Pilot Periodic E01 (`run-sem29-periodic-emulator-20261107-r2` và run đầu `ABORTED`) cho phần `[PLAYBACK]` Periodic; khớp nối lời chuyển từ Tâm (cuối Slide 5) sang Trang (đầu Slide 6 Demo) và từ Trang sang Vinh (đầu Slide 7). |

---

## 3. Kết quả Kiểm tra Chi tiết (Expected / Actual)

| STT | Hạng mục kiểm tra | Expected | Actual / Evidence | Kết quả |
|:---:|---|---|---|:---:|
| 1 | **Đầy đủ file đầu ra riêng của SEM-47** | Có mặt `slides/inputs/TRANG.md`, `slides/DEMO_SCRIPT.md` và `docs/evidence/SEM-47/CHECKS.md`; không tự ý sửa file của task khác | Đã tạo đủ 3 file theo đúng quy ước thư mục; `git status` xác nhận chỉ thêm 3 file thuộc quyền sở hữu của SEM-47 | **Pass** |
| 2 | **Nội dung cơ chế Silent Push, Payload, TTL, Token & Giới hạn (Slide 4)** | Phân biệt rõ `data-only` v1 với muted/mixed notification; nêu đúng payload đã loại token, TTL `86400000 ms` (24h), quản lý token bằng SHA-256 fingerprint, chính sách `PushInputPolicy` và 8 giới hạn nền | [`slides/inputs/TRANG.md`](../../../slides/inputs/TRANG.md) Mục 2–4 trình bày đầy đủ kèm sơ đồ Mermaid, bảng so sánh 3 loại payload, JSON payload thực tế từ [`fcm_sender.js`](../../../server/src/fcm_sender.js), mã trạng thái [`FcmTokenManager.kt`](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/FcmTokenManager.kt) và ma trận [`PUSH_INPUT_CASES.md`](../SEM-38/PUSH_INPUT_CASES.md) | **Pass** |
| 3 | **Mạch lời dẫn Demo gói gọn trong 4 phút (`07:00–11:00`) và đánh dấu `[LIVE]` / `[PLAYBACK]`** | Có kịch bản liền mạch 240 giây cho cả Push, Periodic và Doze/Hybrid; Trang dẫn xuyên suốt, Trí thao tác; gắn nhãn `[LIVE]` và `[PLAYBACK]` rõ ràng ở từng phân đoạn | [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) Mục 1 & Mục 3 chia chính xác 5 phân đoạn (`30s + 60s + 60s + 60s + 30s = 240s`, kèm biến thể rút 30s còn `210s` cho phương án 13+2 phút) và đóng nhãn `[LIVE]` / `[PLAYBACK]` cho từng khung | **Pass — kiểm nội dung** *(Bấm giờ thực tế: `Not run` — thuộc SEM-54)* |
| 4 | **Ngưỡng 30 giây đổi sang video dự phòng không bị coi là bảo đảm của FCM** | Ghi rõ chuyển sang bản ghi dự phòng nếu chưa `snapshot_applied` sau 30 giây từ lúc gửi; giải thích 30 giây là ngưỡng thời lượng trình bày, không phải SLA của FCM | [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) Phân đoạn 2 (`0:30–1:30`), Mục 4.1–4.2 và [`slides/inputs/TRANG.md`](../../../slides/inputs/TRANG.md) Mục 6 Câu 2 quy định rõ lời dẫn và cấm tuyên bố FCM bảo đảm 30 giây | **Pass** |
| 5 | **Câu trả lời chuẩn "Vì sao `accepted` khác `delivered` và khác `applied`?"** | Tách biệt rõ `server_updated`, `push_send_accepted`, `push_received`, `work_enqueued`, `work_started` và `snapshot_applied`; có câu trả lời trực diện cho hội đồng | [`slides/inputs/TRANG.md`](../../../slides/inputs/TRANG.md) Mục 4.1, Mục 6 Câu 1 và [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) Mục 5 cung cấp bảng ranh giới nhận thức, sơ đồ 3 khoảng trống và lời đáp 20 giây | **Pass** |
| 6 | **Mỗi khẳng định có nguồn/evidence hoặc ghi rõ giả thuyết / `Not run`** | Không biến kế hoạch hoặc fixture thành kết quả chạy thật; dẫn đúng số liệu Pilot E01 (`SEM-29`) và ghi `Not run` cho `SEM-34` (E02), `E03`, `E05` thiết bị, `E06` Android, `SEM-42` OPPO | Kiểm đối chiếu [`run-sem29-periodic-emulator-20261107-r2`](../../../experiments/runs/run-sem29-periodic-emulator-20261107-r2/manifest.json) bằng `validate_pilot.py` khớp `analysis.json` (6 `work_started` = 1 recovery setup `snapshot_applied` v3 + 5 chu kỳ mới `snapshot_unchanged`; giữ cả run đầu `ABORTED`). Các ca chưa chạy đều ghi rõ **`Not run`** | **Pass** |
| 7 | **Bảo mật thông tin nhạy cảm** | Không chứa FCM token thô, `google-services.json`, service-account key hay serial thiết bị cá nhân trong tài liệu và kịch bản hiển thị | Đã kiểm toàn bộ 3 file; kịch bản chỉ cho phép hiển thị `fcmTokenFingerprint` (16 hex) và `device_alias` | **Pass** |
| 8 | **Kiểm tra liên kết nội bộ, cú pháp Markdown và `git diff --check`** | Toàn bộ đường dẫn tương đối trong 3 file trỏ tới file tồn tại; code fence/Mermaid cân bằng; không có lỗi whitespace | Chạy script kiểm tra toàn bộ link tương đối của 3 file và `git diff --check`: **0 broken links, 0 whitespace errors** | **Pass** |
| 9 | **Chạy Pilot Push E02 trên thiết bị ([SEM-34](../../../tasks/backlog/SEM-34.md)) & các ca thiết bị E03/E05/E06/OPPO** | Có manifest và `events.jsonl` từ thiết bị thật/emulator cho E02 và các ca mở rộng | Thuộc các task thực nghiệm [SEM-34](../../../tasks/backlog/SEM-34.md), [SEM-36](../../../tasks/backlog/SEM-36.md), [SEM-41](../../../tasks/backlog/SEM-41.md), [SEM-42](../../../tasks/backlog/SEM-42.md); hiện đang chờ cấu hình Firebase thật (**Blocker B1**) và candidate [SEM-37](../../../tasks/backlog/SEM-37.md) | **`Not run — Blocker B1 & chờ task thực nghiệm`** |
| 10 | **Quay video dự phòng ([SEM-53](../../../tasks/backlog/SEM-53.md)) và bấm giờ diễn tập ([SEM-54](../../../tasks/backlog/SEM-54.md))** | Có file video dự phòng trên Drive và biên bản bấm giờ 2 lần diễn tập | Thuộc [SEM-53](../../../tasks/backlog/SEM-53.md) (Trí) và [SEM-54](../../../tasks/backlog/SEM-54.md) (Tuấn) sau khi ghép deck [SEM-51](../../../tasks/backlog/SEM-51.md) và đóng gói [SEM-52](../../../tasks/backlog/SEM-52.md) | **`Not run — thuộc SEM-53 / SEM-54`** |

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

## 5. Blocker, Giới hạn và Bàn giao cho Task sau

1. **Blocker và Giới hạn hiện hành:**
   - **Blocker B1 (kế thừa từ SEM-13 / SEM-33 / SEM-35):** Chưa có Firebase project, `google-services.json`, service-account key và registration token thiết bị thật được xác nhận trong repo. Do đó, [SEM-34](../../../tasks/backlog/SEM-34.md) (Pilot Push E02 của Vinh) vẫn đang ở trạng thái `Todo` (`Not run`).
   - **Ranh giới cách dùng:** Trong [`slides/inputs/TRANG.md`](../../../slides/inputs/TRANG.md) và [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md), phần cơ chế và chính sách đầu vào được dẫn từ code/unit test đã nghiệm thu ([SEM-15](../SEM-15/CHECKS.md), [SEM-27](../SEM-27/CHECKS.md), [SEM-28](../SEM-28/M1.md), [SEM-30](../SEM-30/CHECKS.md), [SEM-31](../SEM-31/CHECKS.md), [SEM-32](../SEM-32/CHECKS.md), [SEM-33](../SEM-33/CHECKS.md), [SEM-35](../SEM-35/CHECKS.md), [SEM-38](../SEM-38/CHECKS.md), [SEM-39](../SEM-39/CHECKS.md), [SEM-40](../SEM-40/CHECKS.md)); phần `[PLAYBACK]` Periodic E01 dẫn từ 2 run thật của [SEM-29](../SEM-29/CHECKS.md); các kết quả chạy thiết bị cho `E02`, `E03`, `E05`, `E06` và `OPPO Find X9` được giữ nguyên nhãn **`Not run`** cho tới khi các task tương ứng bàn giao.
2. **Đầu ra bàn giao mở khóa cho các task tiếp theo:**
   - **[SEM-51](../../../tasks/backlog/SEM-51.md) (Tuấn — Ghép deck 15 phút, PDF và speaker notes):** Nhận [`slides/inputs/TRANG.md`](../../../slides/inputs/TRANG.md) cho Slide 4 (`04:00–06:00`) và [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) cho Slide 6 (`07:00–11:00`) cùng `SPEAKER_NOTES.md`.
   - **[SEM-52](../../../tasks/backlog/SEM-52.md) (Trung — Build APK bàn giao và viết DEMO_RUNBOOK) & [SEM-53](../../../tasks/backlog/SEM-53.md) (Trí — Tái lập runbook và quay video dự phòng):** Sử dụng cấu trúc 5 phân đoạn 240 giây, quy tắc ngưỡng 30 giây và danh mục trường hiển thị bắt buộc trong [`slides/DEMO_SCRIPT.md`](../../../slides/DEMO_SCRIPT.md) để thống nhất thao tác runbook và quay video dự phòng.
   - **[SEM-54](../../../tasks/backlog/SEM-54.md) (Tuấn — Điều phối hai lần diễn tập và ghi thời lượng):** Sử dụng các mốc bấm giờ dự kiến của Trang (Slide 4: `115s + 5s chuyển = 120s`; Slide 6 Demo: `30s + 60s + 60s + 60s + 25s + 5s chuyển = 240s`) để đo thời lượng thực tế.
3. **Trạng thái đề xuất:** Đề nghị nhóm trưởng (`@ThanhTris`) kiểm nhận ở cột **Review** (kèm trạng thái `Not run` của các ca thiết bị/diễn tập được ghi nhận minh bạch; không tự chuyển `Done` từ kế hoạch).
