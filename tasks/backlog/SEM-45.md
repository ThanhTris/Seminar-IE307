# SEM-45 — Viết parser log và sinh results.csv

- Trạng thái: **In Progress** (Project).
- Trạng thái đầu vào: **Đang thực hiện**.
- Còn chờ: Nên nhận: [SEM-42](SEM-42.md).
- Đối chiếu Project: 2026-11-18 02:33:31 UTC.
- Người thực hiện duy nhất: **Tuấn** (`mtuan2491`).
- Hạn: **07/11/2026 17:00 (UTC+7)**.
- Công sức: 2/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-08](SEM-08.md); nhóm cũ chỉ còn lưu lịch sử.

> **Cập nhật 16/11/2026 theo review của Trí.** Bộ `experiments/results.csv` giữ 12 lượt OBSERVED/pilot đã bàn giao, cập nhật theo nguồn SEM-41 `42ca000` thành **0 VALID / 12 INVALID** sau audit collector thu hồi 8 qualification. Sáu lượt chạy lại mới của nguồn nằm ngoài bộ chọn hiện tại và được liệt kê trong INPUTS. Mẫu số main bằng 0; main emulator 27 slot Not run, OPPO chưa có log, kiểm độc lập SEM-44 và các phép đo thiếu clock/boot ghi Not run/giới hạn trong CHECKS. Trạng thái Project hiện vẫn In Progress, chờ review bản sửa.

> **Cập nhật 18/11/2026.** Đã nhận main `9caaf38`, sửa guard E04 cho apply trước reconnect/thiếu clock và guard E06 cho fetch đúng target/correlation/thứ tự. Công cụ v0.3.0 có 12 test hồi quy mới, suite Ubuntu đạt 145/145. Bộ artifact vẫn giữ 12 pilot lịch sử INVALID, main/OPPO chưa có phép đo nhận vào bộ này, mẫu số main bằng 0. Audit SEM-44 trên main đã kiểm bản producer trước; bản sửa hiện tại chờ reviewer đối chiếu. CHECKS và ANALYSIS ghi giới hạn Windows symlink và cách phục hồi LF để tái lập report. PR tiếp tục Draft.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-24](SEM-24.md), [SEM-26](SEM-26.md)
- **Hoàn tất còn cần:** [SEM-41](SEM-41.md), [SEM-42](SEM-42.md)

Không có gate bắt đầu nghĩa là làm được ngay. Mục Hoàn tất còn cần là đầu vào nên dùng nếu đã có, không chặn chuyển Done: owner chuyển Done khi đầu ra và CHECKS của chính task có thật; đầu vào chưa có thì ghi Not run/giới hạn trong CHECKS. Bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Protocol cốt lõi](../../docs/EXPERIMENT_PROTOCOL.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-24 — Chuẩn bị bộ xuất log và run manifest](SEM-24.md) | Vinh | `experiments/RUN_MANIFEST_TEMPLATE.json`<br>`experiments/scripts/export_logs.*`<br>`experiments/README.md` | `docs/evidence/SEM-24/CHECKS.md` | Done |
| Bắt đầu | [SEM-26 — Chốt hợp đồng API và event schema](SEM-26.md) | Tâm | `docs/API.md`<br>`docs/EVENT_SCHEMA.md` | `docs/evidence/SEM-26/CHECKS.md` | Done |
| Hoàn tất | [SEM-41 — Chạy tập chính E01–E06 trên emulator](SEM-41.md) | Vinh | `experiments/runs/<emulator-main-run>/manifest.json`<br>`experiments/runs/<emulator-main-run>/events.jsonl` | `docs/evidence/SEM-41/CHECKS.md` | Done |
| Hoàn tất | [SEM-42 — Chạy đối chiếu OPPO E01/E02 và ghi giới hạn OEM](SEM-42.md) | Trí | `experiments/runs/<oppo-main-run>/manifest.json`<br>`experiments/runs/<oppo-main-run>/events.jsonl` | `docs/evidence/SEM-42/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-11-18 02:33:31 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Tuấn cần làm

1. Xây parser từ manifest/events sang outcome/timings/counts theo protocol; có thể chuẩn bị bằng fixture có nhãn.
2. Khi main logs bàn giao, chạy để sinh results.csv và lệnh tái lập.
3. Giữ timeout riêng, kiểm clock offset và nhóm theo case/device/mode/build.

## Đầu ra bắt buộc

- `experiments/scripts/analyze.*`
- `experiments/results.csv`
- `docs/evidence/SEM-45/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [x] Tái sinh được CSV từ log; fixture không lẫn main, không gán latency timeout bằng 0.
- [x] Accepted/received/queue/sync không bị gộp thành một mốc.
- [x] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Các bước thực hiện trên nhánh SEM-45

Nhánh `codex/SEM-45-log-parser`, từ main `d29532a` ngày 08/11/2026. Lịch sử loader/metrics/CLI đã làm được giữ trong [CHECKS](../../docs/evidence/SEM-45/CHECKS.md). Lần tiếp tục ngày 15/11 có bốn bước, mỗi bước một commit.

1. **Đã xong** cập nhật main `bcc7c58`, chạy lại 71 test cũ — merge commit `0d4a0e9`.
2. **Đã xong** kiểm đầu vào thật, thêm index nguồn pinned/hash, giữ uncertainty khi thiếu boot và tách outcome khai báo — `c8ae2fe`.
3. **Đã xong** sinh CSV 12 dòng pilot, summary/report có provenance, đối chiếu và tái lập giống từng byte — `fd3aa8c`.
4. **Đã xong** rà nhóm epoch store và LF/checksum, kiểm 81 test, cập nhật hướng dẫn/CHECKS/Not run và chuẩn bị Draft PR — `dec00b7`.

Đầu vào SEM-41 được tham chiếu từ Draft PR #29 tại commit `42ca000da1de2b7465851e1485fec2631f4b1a3c`. CSV hiện có nhãn pilot và cả 12 dòng INVALID. Main/OPPO chưa nhận được bộ đo cho lần bàn giao này. SEM-43/44/48/50 dùng bộ lịch sử cùng giới hạn đã ghi để kiểm pipeline và truy vết. Batch đo lại của nguồn đang RUNNING, các lượt mới được nhận riêng theo revision/evidence phù hợp.

### Ba bước sửa theo review ngày 16/11

1. **Đã xong** cập nhật pin/hash theo nguồn mới, audit thu hồi và phạm vi 12 lượt cũ — `d202701`.
2. **Đã xong** tái sinh CSV/summary/report/VERIFICATION với 0 VALID/12 INVALID, kiểm 81 test và tái lập — `0629f24`.
3. **Đã xong** sửa CHECKS/ANALYSIS/task theo qualification mới, ghi rõ 6 lượt đo lại nằm ngoài bộ chọn và phần Not run — `1a0c667`.

### Bốn bước sửa theo review ngày 18/11

1. **Đã xong** cập nhật main `9caaf38` — `42a466a`.
2. **Đã xong** sửa và kiểm hồi quy E04 reconnect/clock/cửa sổ — `fd53736`.
3. **Đã xong** sửa và kiểm hồi quy E06 work/fetch/apply — `5654664`.
4. **Đã xong** tái sinh artifact, đối chiếu Windows/Ubuntu, ghi hướng dẫn CRLF/LF và kiểm bàn giao. Commit cuối tra trong lịch sử CHECKS.

## Task được mở khóa

- [SEM-43](SEM-43.md) cần đầu ra này để **hoàn tất**.
- [SEM-44](SEM-44.md) cần đầu ra này để **hoàn tất**.
- [SEM-48](SEM-48.md) cần đầu ra này để **hoàn tất**.
- [SEM-50](SEM-50.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Tuấn thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
