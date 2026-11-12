# SEM-46 — CHECKS hoàn tất và bàn giao tài liệu

Tuấn (`mtuan2491`), cập nhật ngày 12/11/2026. Nhánh `codex/SEM-46-opening-demo`.

**Đầu ra tài liệu SEM-46 đã hoàn tất để review và bàn giao SEM-51 theo quy tắc nhóm ngày 12/11.** Candidate SEM-37, live FCM, playback push/Doze/E06 trên Android và diễn tập thời lượng được ghi Not run tại lần chốt này. [Quy tắc task](../../../tasks/README.md)

## Revision và các bước đã hoàn tất

- Nhánh được tạo từ main `54d48c2ed48588b59b16cc652a8d1b77912c15b7` ngày 09/11. Hai commit soạn ban đầu là `acf341e` và `1369893`.
- Lần chốt này nhận main `cc2bd1cbaecbd8e2e235af7985bbe720a6e8f1ff`, trong đó đầu vào còn thiếu được ghi Not run/giới hạn khi owner chốt đầu ra của mình.
- Người soạn là Tuấn. Trí nói mở bài và thao tác, Trang dẫn demo, Vinh nhận phần kết quả theo PRESENTATION_PLAN.

| Bước trong lần chốt | Đầu ra / kết quả | Commit |
|---|---|---|
| 1. Cập nhật main | Nhận policy ngày 12/11, SEM-47/49 và source messaging/token mới | `107d271` |
| 2. Hoàn thiện TRI.md | Lời mở bài, mode HYBRID mặc định, phối hợp SEM-47, lựa chọn evidence và lệnh CONTRACT đã chạy | `175257e` |
| 3. Kiểm cuối và chốt bàn giao | Hồ sơ này và checklist SEM-46, ghi các phép kiểm và Not run | Tra commit bằng `git log --oneline -- docs/evidence/SEM-46/CHECKS.md` |

## Artifact và nguồn đã nhận

| Nguồn | Artifact / kiểm chứng | Cách dùng |
|---|---|---|
| SEM-14, Done | [SHARED_SYNC](../../mechanisms/SHARED_SYNC.md), [CHECKS](../SEM-14/CHECKS.md) | Trigger, worker, transaction/version và UI |
| Kế hoạch | [SCOPE](../../SCOPE.md), [PRESENTATION_PLAN](../../PRESENTATION_PLAN.md) | Mở bài 45 giây, demo 4 phút, vai nói/thao tác |
| SEM-19, Done | [MECHANISMS](../../MECHANISMS.md), [QUESTIONS](../../QUESTIONS.md) | Cách gọi event và giới hạn nguồn |
| SEM-47, Done | [TRANG.md](../../../slides/inputs/TRANG.md), [DEMO_SCRIPT](../../../slides/DEMO_SCRIPT.md), [CHECKS](../SEM-47/CHECKS.md) | Năm phân đoạn, nhịp phối hợp và đường CONTRACT khi thiếu Firebase |
| SEM-28, Done | [M1](../SEM-28/M1.md) | Hồ sơ MANUAL và giao dịch cache, giữ nhãn M1 |
| SEM-29, Done | [CHECKS](../SEM-29/CHECKS.md), [manifest r2](../../../experiments/runs/run-sem29-periodic-emulator-20261107-r2/manifest.json), [analysis r2](../../../experiments/runs/run-sem29-periodic-emulator-20261107-r2/analysis.json) | Playback pilot periodic có provenance |
| Source token/mode/sender | [Gateway](../../../android/app/src/main/java/com/thanhtris/seminarie307/integration/RealBulletinUiGateway.kt), [adapter](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/PushSyncEnqueueAdapter.kt), [token](../../../android/app/src/main/java/com/thanhtris/seminarie307/fcm/FcmTokenManager.kt), [sender](../../../server/bin/fcm-sender.js), [hướng dẫn sender](../../setup/FCM_SENDER.md) | Đối chiếu mode hiển thị, dòng Logcat và CLI |

Artifact bàn giao là [TRI.md](../../../slides/inputs/TRI.md), với lời mở bài, phiếu thao tác, bảng tình huống và các nhãn LIVE/CONTRACT/PLAYBACK/PROTOCOL.

## Expected / actual

| Check | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| Scope / opening / phân vai | Khớp flow và kế hoạch nói | Mở bài 40 giây dự kiến + 5 giây chuyển Trung, Trí thao tác và Trang dẫn demo | Pass cho đối chiếu tài liệu |
| Nhịp phối hợp SEM-47 | Giữ 5 phân đoạn, 240 giây tổng | Các đoạn dài 30, 60, 60, 60, 30 giây. TRI chia phần 60 giây push thành hai khoảng 30 giây | Pass cho kiểm ngân sách |
| Mode / UI / log | Thao tác và lời nói khớp source | Gateway/adapter mặc định HYBRID, setMode thuộc tích hợp SEM-36. Log token dùng fingerprint, key READY ở metadata. Hướng dẫn live dùng mode đọc thực tế tại setup | Pass cho rà source |
| CONTRACT CLI | Lệnh có đủ ID, mode/source và payload hợp lệ | Chạy lệnh mục dưới trả `validated_locally`, mode HYBRID, source PUSH, normal priority, TTL 86400000 ms, cấu trúc output chỉ có data/android | Pass local |
| Playback periodic | Counts/provenance khớp run gốc | Validator SEM-29 audit cả hai run và so analysis đã lưu, cả hai khớp. R2 có 6 start trong window, gồm 5 cycle mới + 1 recovery setup, applied v3 thuộc recovery | Pass cho kiểm artifact |
| Lựa chọn nội dung khi thiếu run | Phần trình bày có evidence hoặc nhãn tương ứng | CONTRACT dùng payload + MANUAL M1, PLAYBACK dùng periodic r2. Doze/E06 dùng PROTOCOL và source/test của SEM-40 khi run Android chưa nhận | Pass cho review tài liệu |
| Link / bảng / format | File/link/nhãn đọc được, diff hợp lệ | TRI.md, CHECKS và task có 62 link nội bộ hợp lệ, 10 bảng đúng cấu trúc, fence/whitespace đạt, 3 tiêu chí có kết quả và git diff --check đạt | Pass cho kiểm tĩnh |
| Candidate SEM-37 và live FCM | Có kiểm trên build/device thật khi công bố đã chạy | Candidate/config và credential/token thật chưa nhận cho lần này | **Not run** |
| Playback push, Doze/E06 Android, video | Có run/video kèm metadata | Bộ evidence đang nhận chỉ có M1 và pilot periodic | **Not run** |
| Diễn tập/bấm giờ thật | Có lượt nói/thao tác thực để chốt thời lượng | 45/240 giây là ngân sách biên tập, diễn tập thuộc SEM-54 | **Not run** |

## Lệnh đã kiểm và cách tái lập

Máy kiểm Windows, Node 24.20.0, Python 3.12.14 có sẵn trong runtime. Cài dependency `server/` theo lockfile bằng `npm ci --ignore-scripts --no-audit --no-fund`, sau đó từ root repo chạy

```powershell
node server/bin/fcm-sender.js --validate-only --run run-sem46-contract --mode HYBRID --device emulator-01 --update-id update-sem46-contract --signal-id signal-sem46-contract --version 1
python -B docs/evidence/SEM-29/validate_pilot.py experiments/runs/run-sem29-periodic-emulator-20261107
python -B docs/evidence/SEM-29/validate_pilot.py experiments/runs/run-sem29-periodic-emulator-20261107-r2
git diff --check
```

Kết quả CLI được đối chiếu từng trường payload. Đối với playback, gọi `audit(run_dir)` của validator và so toàn object với analysis.json đã commit, các phép kiểm hash/manifest/events đạt. Tool output lưu tại `.local/sem46/` để đối chiếu cục bộ. Lần kiểm này đọc các artifact đã bàn giao, live/candidate/diễn tập giữ trạng thái Not run trong bảng trên.

## Bàn giao và cập nhật tiếp theo

SEM-51 nhận TRI.md để ghép slide mở bài và notes thao tác trong demo 4 phút. SEM-46 áp dụng policy `cc2bd1c`, ghi nguồn/candidate thiếu dưới Not run và hoàn tất phần tài liệu của owner. Khi có candidate, run hoặc video mới, cập nhật phiếu cấu hình và CHECKS theo artifact thực tế.

Các điều chỉnh so với bản ngày 09/11 gồm mode HYBRID mặc định, phương án CONTRACT khi thiếu push playback, nhận diện 5 cycle mới và 1 recovery của pilot r2, nhãn PROTOCOL cho Doze/E06 chưa có run. Quy định WIP/chờ SEM-37 bắt buộc ở bản cũ được thay bằng trạng thái Not run theo policy mới. Draft PR dùng cho Tuấn review trước khi gửi nhóm trưởng kiểm nhận.
