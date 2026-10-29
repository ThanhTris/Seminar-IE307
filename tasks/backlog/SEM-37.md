# SEM-37 — Chốt bản ứng viên và manifest phục vụ tập chính

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-29 16:31:03 UTC.
- Người thực hiện duy nhất: **Trí** (`ThanhTris`).
- Hạn: **05/11/2026 22:00 (UTC+7)**.
- Công sức: 2/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-07](SEM-07.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-31](SEM-31.md), [SEM-33](SEM-33.md), [SEM-36](SEM-36.md), [SEM-38](SEM-38.md), [SEM-39](SEM-39.md), [SEM-40](SEM-40.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-31 — Bàn giao chẩn đoán và tài liệu periodic](SEM-31.md) | Trung | `docs/PERIODIC.md`<br>`docs/evidence/SEM-31/SCHEDULER_CHECKS.md` | `docs/evidence/SEM-31/CHECKS.md` | Todo |
| Bắt đầu | [SEM-33 — Xử lý token refresh và bàn giao PUSH.md](SEM-33.md) | Trang | `android/ (token lifecycle)`<br>`docs/PUSH.md` | `docs/evidence/SEM-33/CHECKS.md` | Todo |
| Bắt đầu | [SEM-36 — Tích hợp ba mode và pilot hybrid](SEM-36.md) | Trí | `android/ (mode controller và tích hợp)`<br>`docs/SYNC.md`<br>`docs/evidence/SEM-36/HYBRID_PILOT.md` | `docs/evidence/SEM-36/CHECKS.md` | Todo |
| Bắt đầu | [SEM-38 — Xử lý duplicate và version hint của push](SEM-38.md) | Trang | `android/ (messaging input policy)`<br>`docs/evidence/SEM-38/PUSH_INPUT_CASES.md` | `docs/evidence/SEM-38/CHECKS.md` | Todo |
| Bắt đầu | [SEM-39 — Củng cố version guard, retry và race trong core](SEM-39.md) | Trung | `android/ (sync robustness và logic checks)`<br>`docs/evidence/SEM-39/CORE_CASES.md` | `docs/evidence/SEM-39/CHECKS.md` | Todo |
| Bắt đầu | [SEM-40 — Thêm fault injection cố ý bỏ gửi push](SEM-40.md) | Tâm | `server/ (skip-push CLI)`<br>`docs/evidence/SEM-40/FAULT_INJECTION.md` | `docs/evidence/SEM-40/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-29 16:31:03 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trí cần làm

1. Pin app/server commit, APK SHA256, dependency/config và danh sách ca pilot trên bản ứng viên.
2. Build candidate, rà M1/hai trigger/hybrid và ghi cổng đủ để đo main.
3. Bàn giao đường dẫn artifact và quy tắc phải chạy lại ca khi code/config liên quan đổi.

## Đầu ra bắt buộc

- `release/CANDIDATE_MANIFEST.json`
- `docs/evidence/SEM-37/CANDIDATE_GATE.md`
- `docs/evidence/SEM-37/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Truy được artifact tới đúng source/config và pilot đã ghi; không chỉ gửi APK không metadata.
- [ ] Chốt cuối 05/11 để tập chính 06–07/11; nếu trễ ghi blocker và điều chỉnh ca mở rộng.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-41](SEM-41.md) cần đầu ra này để **bắt đầu**.
- [SEM-42](SEM-42.md) cần đầu ra này để **bắt đầu**.
- [SEM-46](SEM-46.md) cần đầu ra này để **hoàn tất**.
- [SEM-52](SEM-52.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trí thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
