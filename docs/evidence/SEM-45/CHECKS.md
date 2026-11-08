# SEM-45 — Kiểm parser và bàn giao từng bước

- Người thực hiện: Tuấn (`mtuan2491`), ngày 08/11/2026 (UTC+7).
- Nhánh: `codex/SEM-45-log-parser`, tạo từ main `d29532ac19a2fba402d2d1c6d25dfb63a306a87a`.
- Phạm vi hiện tại: hoàn thành phần công cụ bằng fixture; chưa có dữ liệu chính SEM-41/42, chưa nghiệm thu toàn task. Không push hoặc đổi Status Project trong lần làm này.

## Bốn bước và điều kiện thực hiện

| Bước | Đầu ra / kiểm chứng | Trạng thái |
|---|---|---|
| 1. Nhận contract, đọc và kiểm dữ liệu | Loader JSONL/manifest canonical; test routing, duplicate, version, phân loại dataset | **Hoàn tất — `85aab1c`** |
| 2. Tính chỉ số và kiểm trường hợp biên | Correlation, cửa sổ/timeout/late, clock, counts; test bằng fixture | **Hoàn tất — `f7c1958`** |
| 3. Xuất CSV và hướng dẫn bàn giao | CLI tái lập, nhóm thống kê, provenance/hash, [hướng dẫn](../../../experiments/ANALYSIS.md) và kiểm tích hợp | **Hoàn tất phần công cụ — commit bước 3** |
| 4. Chạy trên tập chính và chốt SEM-45 | Nhận SEM-41/42 + CHECKS, sinh `experiments/results.csv`, bàn giao SEM-44 kiểm độc lập | **Chờ SEM-41/42; Not run** |

Mỗi bước thực hiện xong có một commit riêng. SHA tra bằng `git log --oneline -- docs/evidence/SEM-45/CHECKS.md`, tránh tự ghi SHA của commit đang tạo.

## Đầu vào đã nhận

| Nguồn | Artifact / evidence | Cách dùng |
|---|---|---|
| SEM-24 — Done | [Template](../../../experiments/RUN_MANIFEST_TEMPLATE.json), [exporter](../../../experiments/scripts/export_logs.py), [README](../../../experiments/README.md), [CHECKS](../SEM-24/CHECKS.md) | Manifest 1.0.0, exporter 1.0.0; tái sử dụng validator đọc, không sửa module nguồn |
| SEM-26 — Done | [API](../../API.md), [EVENT_SCHEMA](../../EVENT_SCHEMA.md), [CHECKS](../SEM-26/CHECKS.md) | Contract 2.0.0, 27 key/event; ID và timestamp giữ nguyên |
| SEM-16 | [PROTOCOL](../../../experiments/PROTOCOL.md), [protocol cốt lõi](../../EXPERIMENT_PROTOCOL.md) | Cửa sổ, nguồn/case, clock và mẫu số thống kê |
| SEM-29 — pilot | [CHECKS](../SEM-29/CHECKS.md) | Android `legacy-room-v1` được nghiệm thu cho pilot; không đổi thành canonical v2 hoặc tập chính |
| SEM-41/42 — Todo | Chưa có bộ run chính/CHECKS trên main nền | Chỉ chặn bước 4; không tạo `results.csv` đo thật từ fixture |

## Kết quả kiểm

Máy kiểm Windows, Python **3.12.14**, standard library. Python alias của Windows không chạy được nên dùng Python có sẵn trong runtime của Codex; không thêm dependency. Sandbox không cho ghi temp mặc định; đặt TEMP/TMP/TMPDIR của tiến trình kiểm vào `.local/sem45-temp` (Git bỏ qua), sau đó chạy đạt.

| Check | Expected | Actual | Kết quả |
|---|---|---|---|
| Loader canonical | Không suy trường thiếu, không trộn route/schema/dataset, giữ giá trị và hash | 8 test đạt: fixture SEM-24 giữ nguyên, legacy bị từ chối, replay dedup, conflict/duplicate key/NaN/blank/future field/type sai bị chặn | Pass — synthetic/offline |
| Chỉ số / correlation / clock | Không biến accepted/hint thành applied; không đo qua boot hoặc lấy host clock làm Android | Tổng 22 test đạt, gồm 14 test chỉ số: timeout/late, clock sign/uncertainty, ambiguous receipt, retry/GET ID, cycle dùng chung work ID, setup/MANUAL/window ngắn và nhóm phase/build/config/injection | Pass — synthetic/offline |
| CLI / CSV / summary / tích hợp | Fixture/pilot không vào main; timeout giữ mẫu số, missing duration để trống; hash đúng và không overwrite | Bộ kiểm cuối **71 tests**: 35 SEM-45 + 36 SEM-24; tích hợp exporter → analyzer, sample main tổng hợp trong temp để kiểm mẫu số và candidate gate, output độc lập thứ tự input và kiểm hash | Pass — synthetic/offline |
| CLI fixture thực chạy | Nhận export SEM-24, giữ NOT_RUN; không sinh kết quả main | `--dataset fixture`, batch `fixture-check`: COMPLETED, 1 dòng FIXTURE/development, NOT_RUN, eligible=false, n_eligible=0, latency null; output chỉ ở `.local/sem45/fixture_analysis/fixture-check/` | Pass — fixture |
| Từ chối legacy pilot | Không lấp trường thiếu hoặc lấy pilot thay main | CLI `--dataset pilot` trên run SEM-29 r2 trả exit 2 / `CONTRACT_VERSION_UNSUPPORTED`; không tạo batch `legacy-reject` | Pass — kiểm từ chối, không phân tích pilot |
| Tái lập / file bàn giao | CSV/summary ổn định; link, syntax và whitespace hợp lệ | CLI batch `fixture-reproduce` cho CSV/summary giống từng byte với `fixture-check`; 36 link nội bộ trong 3 tài liệu hợp lệ, fence cân, Python AST tương thích syntax 3.9, git diff --check đạt | Pass — offline |
| Tập chính / dữ liệu thật | Nhận đúng SEM-41/42 trước sinh CSV nghiệm thu | Chưa có bộ run chính hoặc CHECKS nguồn; không tạo `experiments/results.csv` | **Not run — chờ đầu vào bước 4** |

Lệnh bước 1: `python -B -m unittest discover -s experiments/scripts/tests -p test_analyze.py -v`. Runtime Android/server/FCM/OPPO và tập chính **Not run**.

Duration nội bộ dùng monotonic cùng alias/boot. Latency liên máy chỉ có estimate kèm uncertainty khi có clock ANDROID được khai và kiểm mẫu; thiếu dữ liệu để null. Counts là số event/GET start quan sát được, không phải tổng DB writes hoặc chứng nhận instrumentation đầy đủ. `eligible` sẽ dùng cho lọc thống kê main dựa trên manifest và các mâu thuẫn phát hiện được, không thay nghiệm thu OS/Doze/race của SEM-41/42/44.

## Lệnh tái lập bước 3

```sh
python -B -m unittest discover -s experiments/scripts/tests -v
python -B experiments/scripts/analyze.py --dataset fixture \
  --run experiments/fixture_exports/run-sem24-fixture \
  --output-base .local/sem45 --batch-id fixture-check
python -B experiments/scripts/analyze.py --dataset pilot \
  --run experiments/runs/run-sem29-periodic-emulator-20261107-r2 \
  --output-base .local/sem45 --batch-id legacy-reject
git diff --check
```

Lệnh legacy **phải trả exit 2**, không phải failure runtime của pilot. Batch fixture đã có thì dùng ID mới; cố ghi đè phải trả `OUTPUT_EXISTS`. Mẫu success/main trong unit tests là dữ liệu tổng hợp ở temp, chỉ kiểm logic denominator/candidate; không được lấy làm run thật hoặc publish như OBSERVED.

## Giới hạn và bàn giao tiếp

- Đã có [analyze.py](../../../experiments/scripts/analyze.py), [test_analyze.py](../../../experiments/scripts/tests/test_analyze.py) và ANALYSIS hướng dẫn schema/CLI/cột CSV/quy tắc clock/mẫu số. Không sửa exporter, contract hoặc artifact của owner khác.
- Summary hiện tính whole-run; phase idle/offline E03/E04 phải đối chiếu milestones và hệ clock từ run thật với SEM-41/42/44, bổ sung mapping/test nếu cần aggregate theo phase. Metadata VALID không chứng minh OS condition hoặc race E05 đã được tạo đúng. E06 thiếu skip đúng target/update có cờ chặn eligible.
- Bước 4 nhận SEM-41/42 + CHECKS, tự đối chiếu candidate/APK/config, target/window/clock/source/phase trước khi chốt CSV rồi bàn giao SEM-44 kiểm độc lập. SEM-44 là consumer sau SEM-45, không thêm làm gate đầu vào gây vòng phụ thuộc. Không tự đổi outcome để vượt gate hoặc gộp emulator thay OPPO.
- Bàn giao phần công cụ để SEM-43/44/48/50 biết interface; **chưa mở khóa nghiệm thu toàn SEM-45**. Các task sau vẫn chờ CSV main thực và CHECKS bước 4. Status Project giữ nguyên; chưa push nhánh.
