# SEM-36 — Tích hợp ba mode và pilot hybrid

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-30 12:33:46 UTC.
- Người thực hiện duy nhất: **Trí** (`ThanhTris`).
- Hạn: **05/11/2026 18:00 (UTC+7)**.
- Công sức: 3/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-07](SEM-07.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-29](SEM-29.md), [SEM-30](SEM-30.md), [SEM-32](SEM-32.md), [SEM-34](SEM-34.md), [SEM-35](SEM-35.md)
- **Hoàn tất còn cần:** [SEM-38](SEM-38.md), [SEM-39](SEM-39.md), [SEM-40](SEM-40.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-29 — Chạy pilot periodic E01 trên hai thiết bị](SEM-29.md) | Vinh | `experiments/runs/<periodic-pilot-run>/manifest.json`<br>`experiments/runs/<periodic-pilot-run>/events.jsonl` | `docs/evidence/SEM-29/CHECKS.md` | Todo |
| Bắt đầu | [SEM-30 — Triển khai unique periodic work](SEM-30.md) | Trung | `android/ (periodic scheduler)` | `docs/evidence/SEM-30/CHECKS.md` | Todo |
| Bắt đầu | [SEM-32 — Triển khai callback FCM và enqueue sync](SEM-32.md) | Trang | `android/ (messaging callback và enqueue adapter)` | `docs/evidence/SEM-32/CHECKS.md` | Todo |
| Bắt đầu | [SEM-34 — Chạy pilot push E02 và xác nhận cache nền](SEM-34.md) | Vinh | `experiments/runs/<push-pilot-run>/manifest.json`<br>`experiments/runs/<push-pilot-run>/events.jsonl` | `docs/evidence/SEM-34/CHECKS.md` | Todo |
| Bắt đầu | [SEM-35 — Làm CLI gửi FCM data-only normal priority](SEM-35.md) | Tâm | `server/ (FCM sender CLI)`<br>`docs/setup/FCM_SENDER.md` | `docs/evidence/SEM-35/CHECKS.md` | Todo |
| Hoàn tất | [SEM-38 — Xử lý duplicate và version hint của push](SEM-38.md) | Trang | `android/ (messaging input policy)`<br>`docs/evidence/SEM-38/PUSH_INPUT_CASES.md` | `docs/evidence/SEM-38/CHECKS.md` | Todo |
| Hoàn tất | [SEM-39 — Củng cố version guard, retry và race trong core](SEM-39.md) | Trung | `android/ (sync robustness và logic checks)`<br>`docs/evidence/SEM-39/CORE_CASES.md` | `docs/evidence/SEM-39/CHECKS.md` | Todo |
| Hoàn tất | [SEM-40 — Thêm fault injection cố ý bỏ gửi push](SEM-40.md) | Tâm | `server/ (skip-push CLI)`<br>`docs/evidence/SEM-40/FAULT_INJECTION.md` | `docs/evidence/SEM-40/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-30 12:33:46 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trí cần làm

1. Tích hợp PERIODIC/PUSH/HYBRID; hủy lịch không cần và chờ worker kết thúc hoặc đánh dấu run bị nhiễu.
2. Ghép output robustness của core/messaging và skip-push CLI vào bản tích hợp.
3. Chạy E05/E06 pilot và ghi SYNC về version/concurrency/retry/mode transition.

## Đầu ra bắt buộc

- `android/ (mode controller và tích hợp)`
- `docs/SYNC.md`
- `docs/evidence/SEM-36/HYBRID_PILOT.md`
- `docs/evidence/SEM-36/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] E05 không rollback/ghi trùng/mất cập nhật ở race; E06 phục hồi từ PERIODIC khi bỏ gửi có chủ ý.
- [ ] Không coi hybrid là vượt Doze/force-stop; các nhánh code vẫn dùng cùng sync engine.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-37](SEM-37.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trí thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
