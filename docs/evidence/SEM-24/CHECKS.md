# SEM-24 — Kiểm công cụ xuất log và run manifest

## Nhận dạng và đầu vào

- **Người thực hiện:** Vinh (`Vinh5905`), hỗ trợ thao tác bằng Codex; ngày **03/11/2026 (UTC+7)**. Hạn gốc 31/10/2026 15:00 được giữ, không ghi lùi ngày làm.
- **Nhánh:** `codex/SEM-24-log-export-manifest`, từ SEM-16 `a5bb70c8b360819dc13091475c3a89ddb2c06afa`, kế thừa SEM-12 `6767b70`; source app/server trên nền `8f8d39e`. Không sửa output SEM-12/16 hoặc Android/server của task khác.
- **SEM-12:** đã nhận [DEVICES](../../environment/DEVICES.md), [CHECKS](../SEM-12/CHECKS.md), cấu hình emulator, alias và blocker không có OPPO. Hồ sơ thỏa acceptance cho phép blocker; [PR #7](https://github.com/ThanhTris/Seminar-IE307/pull/7) còn mở khi bắt đầu, chưa coi Project Done.
- **SEM-26:** đã nhận [API](../../API.md), [EVENT_SCHEMA](../../EVENT_SCHEMA.md) **2.0.0**, [CHECKS](../SEM-26/CHECKS.md); artifact `981b430` đã qua [PR #6](https://github.com/ThanhTris/Seminar-IE307/pull/6) và merge `3d49386`, Project snapshot ghi Done. Không lấy đoạn nháp v1 lịch sử trong CHECKS làm contract hiện hành.
- **SEM-16 bổ sung:** [PROTOCOL](../../../experiments/PROTOCOL.md) / [RUN_SCHEDULE](../../../experiments/RUN_SCHEDULE.md) 1.0.0 và [CHECKS](../SEM-16/CHECKS.md), đang ở [PR #8](https://github.com/ThanhTris/Seminar-IE307/pull/8). Không tự tạo dependency mới cho SEM-24; user yêu cầu kế thừa nhánh này.
- **Môi trường kiểm:** macOS máy Vinh, `python3 --version` → **3.9.6**, standard library, không cài package. Không build/cài APK, không chạy app/server/send FCM hay thay idle/mạng. `app_commit`, `server_commit`, `apk_sha256` trong fixture đều **tổng hợp**, không phải APK được đo.

Đủ artifact để triển khai/kiểm công cụ trên nhánh kế thừa. Việc PR nguồn chưa merge và Status cũ không được đổi thành xác nhận workflow đã Done; các task nhận kiểm artifact/CHECKS và thứ tự merge trước khi dùng trên main.

## Đầu ra

- [RUN_MANIFEST_TEMPLATE.json](../../../experiments/RUN_MANIFEST_TEMPLATE.json) `1.0.0`: mặc định TEMPLATE/NOT_RUN, đủ build/OS/config/phase/outcome/window/clock/cleanup; chưa biết để null.
- [export_logs.py](../../../experiments/scripts/export_logs.py) `1.0.0`: chọn run + alias, đọc canonical JSONL v2 hoặc ADB file riêng của app, projection/validation/deny values, dedup và report.
- [README](../../../experiments/README.md): cách chuẩn bị manifest/nguồn private, lệnh tái lập, producer interface, reset/cleanup và giới hạn.
- [Fixture inputs](../../../experiments/fixtures/sem24/) và [fixture export mẫu](../../../experiments/fixture_exports/run-sem24-fixture/): gắn nhãn FIXTURE/development, **không phải run thật**, tách khỏi `runs/`.
- [test_export_logs.py](../../../experiments/scripts/tests/test_export_logs.py): kiểm công cụ hoàn toàn tổng hợp; ADB subprocess được mock, không dùng máy thật.

## Expected / actual và kết quả

| Thao tác đã kiểm | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| Đối chiếu yêu cầu SEM-24 và protocol/schema | Đủ template, exporter, README, CHECKS; không tự điền log v1 thành v2 | Template có app/server commit, APK SHA-256, OS/config, phase/outcome và metadata SEM-16; exporter yêu cầu đủ 27 key v2, từ chối missing/future type/version | Pass |
| Chạy bộ kiểm công cụ | Các tình huống privacy/provenance/lỗi và nhãn dataset được kiểm bằng fixture | **36 tests, OK**, có ví dụ hợp lệ cho cả 18 event type trong schema; kiểm event values/correlation đúng nguyên đầu vào | Pass — synthetic |
| CLI fixture đầy đủ | Đúng run + alias, dedup replay giống hệt | `{"status":"EXPORTED","data_kind":"FIXTURE","events":8}`; report: Android 7 dòng → 6 selected + 1 other run; server 3 dòng → 2 selected + 1 duplicate | Pass — fixture, không phải số đo |
| Bảo toàn giá trị | Không sửa timestamp/version/outcome/IDs/TTL; không xếp clock thành nhân quả | Assertions so sánh chính xác canonical output với input; giữ thứ tự nguồn, elapsed realtime/boot/request/work/network/signal/message ID và event muộn. Manifest TIMEOUT không bị đổi thành SUCCESS | Pass — synthetic |
| Privacy | Token/serial/credential không bị copy sang public; lỗi không echo raw | Trường ngoài allowlist bị bỏ; fake token/serial không có trong fixture export. Deny values trong trường giữ lại, signature credential, object lồng sai kiểu đều chặn trước output. Stderr ADB chỉ ra mã lỗi an toàn | Pass — synthetic; vẫn cần deny local đầy đủ và rà evidence phụ |
| JSON/schema lỗi | Không tạo public run nửa hợp lệ | Duplicate JSON key, NaN, boolean thay integer, legacy/missing fields, major/type không hỗ trợ, applied/cache không khớp, receipt mang data_version, mode/origin sai, event ID mâu thuẫn đều bị từ chối | Pass — synthetic |
| Fixture/observed/main | Fixture không được đi nhầm vào dữ liệu main | Bắt buộc `--fixture` + FIXTURE/development; observed từ chối event `fixture=true`/placeholder message ID; output vào `fixture_exports/`, không vào `runs/`; main VALID cần candidate/hash/OS/window | Pass — kiểm công cụ, không xác nhận candidate thật |
| Output/audit | Không overwrite, không lộ path input, hash đúng bytes | Run đã tồn tại bị từ chối; SHA-256 giữ đúng input CRLF; report không có đường dẫn/serial/raw lỗi; clock controlled thiếu mẫu bị chặn | Pass — synthetic |
| ADB capture adapter | Chỉ đọc file canonical qua run-as, private capture; không fallback logcat | Mock xác nhận đúng argv theo map alias → serial, file raw 0600 trong capture dir 0700; ADB lỗi không echo stderr và không gọi fallback | Pass — mock; **Not run trên thiết bị** |
| Reset/cleanup | Có thao tác/mốc xác nhận, không force-stop làm reset thường | README nối protocol, nêu cancel/drain, run isolation/version baseline, unforce/battery reset, restore transport, user reopen sau force-stop và cleanup status | Pass — hướng dẫn; cleanup thực **Not run** |
| Kiểm contract SEM-26 có sẵn | Bộ ví dụ contract vẫn hợp lệ, không sửa nguồn | `python3 docs/evidence/SEM-26/validate_fixtures.py` Pass: 5 JSON API, 4 JSONL events và các fixture sai được phát hiện | Pass — offline |
| Kiểm artifact bàn giao | File/link đọc được, JSON/Python/shell hợp lệ, tái lập được output mẫu | 12 file kiểm newline/whitespace, parse JSON/JSONL/Python; 44 link nội bộ tồn tại, 4 block shell qua `sh -n`; 3 file fixture export tái lập giống từng byte; `.local/` và `experiments/private/` được gitignore | Pass — kiểm file |
| Thu runtime/FCM/Doze/OPPO | Chỉ báo chạy thật khi có producer và run evidence | Không cài/build/send/đổi thiết bị trong SEM-24; không tạo manifest OBSERVED giả cho main/pilot | **Not run** |

Lệnh đã chạy từ root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s experiments/scripts/tests -v
python3 docs/evidence/SEM-26/validate_fixtures.py

python3 experiments/scripts/export_logs.py \
  --manifest experiments/fixtures/sem24/manifest.json \
  --android-log experiments/fixtures/sem24/android.jsonl \
  --server-log experiments/fixtures/sem24/server.jsonl \
  --device-alias fixture-device --run-id run-sem24-fixture \
  --fixture --output-base .local/sem24-reproduce
git diff --check
```

Bản export mẫu được tạo bằng cùng CLI với output mặc định trước khi commit; bản tái lập ở `.local/sem24-reproduce/fixture_exports/run-sem24-fixture/` phải giống cả ba file mẫu. Để chạy lại chọn output base mới vì công cụ cố ý không ghi đè. Không cần file private của tác giả để chạy fixture/tests.

## Blocker / giới hạn còn lại của tích hợp

| Mục | Hiện trạng | Đầu vào cần nhận tiếp |
|---|---|---|
| Android producer | [TimelineEventEntity](../../../android/app/src/main/java/com/thanhtris/seminarie307/data/local/TimelineEventEntity.kt) chưa có toàn bộ schema v2; source chưa có producer file `files/experiment-events.jsonl` được kiểm nhận | SEM-25/32/36: canonical event từ thực tế, run/config/alias/correlation, atomic applied, flush/read interface; dùng file đó qua run-as hoặc xuất canonical JSONL private qua giao diện đã bàn giao. Không bịa adapter v1→v2 |
| Server/sender producer | Server/CLI hiện chưa có canonical v2 outbox/send log được kiểm nhận | SEM-27/35: SERVER JSONL v2 thật, accepted/rejected/unknown/skipped đúng provenance; không dùng dry-run/mock accepted làm event thật |
| Máy OPPO | Vinh chưa có máy | Gỡ blocker tại SEM-12/42 trước các run OPPO; không chặn kiểm fixture/exporter SEM-24 |
| Candidate/runtime | Chưa nhận SEM-37, chưa thu run thật qua exporter | SEM-28/29/34/41/42 kiểm tích hợp sau gate của từng task; exporter sẵn để nhận file canonical, không xác nhận app đang phát đủ log |
| Clock | Công cụ nhận mẫu/offset/uncertainty, không tự lấy mẫu hoặc chứng nhận clock đã đồng bộ | Người chạy ghi phép đo trước/sau. Source health có `server_time_utc` nhưng contract v2 không bảo đảm field đó; kiểm đúng producer/client clock trước dùng, không coi offset host là offset Android |

Đây là giới hạn tích hợp, không phải các bài đo đã thất bại. Tính an toàn với chuỗi opaque phụ thuộc deny values chứa định danh/secret thật; regex chỉ bổ sung các signature đã biết. Công cụ không scan/sao chép file evidence phụ hoặc certify phân tích thống kê; dữ liệu ấy phải được làm sạch/kiểm riêng trước bàn giao.

## Bàn giao và workflow

- **SEM-28:** template và exporter cho M1, cần canonical Android/server được nhận từ module và run MANUAL đúng nhãn; không dùng fixture mẫu làm M1.
- **SEM-29/34:** manifest pilot và export theo run/alias, metadata/timeout/cleanup thật; chưa nâng pilot thành main.
- **SEM-41/42:** main theo candidate, device/OS/APK/config và window/provenance riêng; OPPO hiện Not run.
- **SEM-45:** manifest `1.0.0`, event `2.0.0`, report count/hash, JSONL giữ giá trị/late/duplicate; đọc data_kind/phase và chỉ phân tích tập được kiểm nhận. Exporter không sinh CSV hoặc tính latency.

SEM-24 đã có đủ đầu ra để đề nghị **Review** theo yêu cầu cho phép dùng fixture kiểm công cụ. Checklist cục bộ không đổi Status Project/nguồn; không tự chuyển Done hoặc cập nhật dependency snapshot hàng loạt. Thứ tự nhánh/PR: SEM-12 → SEM-16 → SEM-24, PR đích `main`; các merge do workflow kiểm nhận, chưa merge trong lần này.
