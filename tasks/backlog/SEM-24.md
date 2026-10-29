# SEM-24 — Chuẩn bị bộ xuất log và run manifest

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-10-29 16:31:03 UTC.
- Người thực hiện duy nhất: **Vinh** (`Vinh5905`).
- Hạn: **31/10/2026 15:00 (UTC+7)**.
- Công sức: 1/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-04](SEM-04.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-12](SEM-12.md)
- **Hoàn tất còn cần:** [SEM-26](SEM-26.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Protocol cốt lõi](../../docs/EXPERIMENT_PROTOCOL.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-12 — Lập hồ sơ OPPO và emulator](SEM-12.md) | Vinh | `docs/environment/DEVICES.md` | `docs/evidence/SEM-12/CHECKS.md` | Todo |
| Hoàn tất | [SEM-26 — Chốt hợp đồng API và event schema](SEM-26.md) | Tâm | `docs/API.md`<br>`docs/EVENT_SCHEMA.md` | `docs/evidence/SEM-26/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-29 16:31:03 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Vinh cần làm

1. Tạo template manifest theo protocol và script lấy log theo device alias/run_id.
2. Bổ sung reset/cleanup và hướng dẫn chạy; nhận event schema để chốt tên trường.
3. Dùng fixture gắn nhãn để kiểm công cụ; không trình bày fixture là số liệu thực nghiệm.

## Đầu ra bắt buộc

- `experiments/RUN_MANIFEST_TEMPLATE.json`
- `experiments/scripts/export_logs.*`
- `experiments/README.md`
- `docs/evidence/SEM-24/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Manifest có commit app/server, APK SHA256, OS/config, phase và outcome.
- [ ] Script không xuất token/serial/credential vào dữ liệu public, không sửa giá trị đo.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-28](SEM-28.md) cần đầu ra này để **bắt đầu**.
- [SEM-29](SEM-29.md) cần đầu ra này để **bắt đầu**.
- [SEM-34](SEM-34.md) cần đầu ra này để **bắt đầu**.
- [SEM-41](SEM-41.md) cần đầu ra này để **bắt đầu**.
- [SEM-42](SEM-42.md) cần đầu ra này để **bắt đầu**.
- [SEM-45](SEM-45.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Vinh thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
