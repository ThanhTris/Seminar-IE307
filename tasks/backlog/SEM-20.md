# SEM-20 — Đọc bài nghiên cứu thứ nhất và ghi chú nguồn

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chuẩn bị trước**.
- Đối chiếu Project: 2026-11-02 02:54:44 UTC.
- Người thực hiện duy nhất: **Tuấn** (`mtuan2491`).
- Hạn: **01/11/2026 16:00 (UTC+7)**.
- Công sức: 5/100 — Nghiên cứu/lập luận.
- Tách từ nhóm cũ: [SEM-03](SEM-03.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** [SEM-11](SEM-11.md), [SEM-12](SEM-12.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Nguồn kỹ thuật và nghiên cứu](../../research/README.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Hoàn tất | [SEM-11 — Chốt phạm vi và môi trường build Android](SEM-11.md) | Trí | `docs/SCOPE.md`<br>`docs/environment/ANDROID_BUILD.md` | `docs/evidence/SEM-11/CHECKS.md` | Done |
| Hoàn tất | [SEM-12 — Lập hồ sơ OPPO và emulator](SEM-12.md) | Vinh | `docs/environment/DEVICES.md` | `docs/evidence/SEM-12/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-11-02 02:54:44 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Tuấn cần làm

1. Chọn và đọc toàn văn một nghiên cứu về scheduling/push-polling/mobile sync, không chỉ abstract.
2. Kiểm metadata/DOI, phương pháp, môi trường, kết quả gốc và giới hạn áp dụng cho demo.
3. Lưu ghi chú, metadata riêng và PDF chỉ khi được phép chia sẻ; đề xuất claim/case kiểm chứng.

## Đầu ra bắt buộc

- `research/notes/PAPER_1.md`
- `research/metadata/paper-1.bib`
- `docs/evidence/SEM-20/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Tên/tác giả/DOI khớp nguồn gốc; ít nhất một lập luận gắn được quyết định thử hoặc trade-off.
- [ ] Không dùng số đo paper làm số đo OPPO; phân biệt nguồn paper và tài liệu API.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-22](SEM-22.md) cần đầu ra này để **hoàn tất**.
- [SEM-50](SEM-50.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Tuấn thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
