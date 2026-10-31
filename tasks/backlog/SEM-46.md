# SEM-46 — Viết phần mở bài và bàn giao lời dẫn thao tác demo

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chuẩn bị trước**.
- Đối chiếu Project: 2026-10-31 12:44:19 UTC.
- Người thực hiện duy nhất: **Trí** (`ThanhTris`).
- Hạn: **08/11/2026 16:00 (UTC+7)**.
- Công sức: 1/100 — Nghiên cứu/lập luận.
- Tách từ nhóm cũ: [SEM-09](SEM-09.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** [SEM-14](SEM-14.md), [SEM-37](SEM-37.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Kịch bản 15 phút](../../docs/PRESENTATION_PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Hoàn tất | [SEM-14 — Vẽ luồng dữ liệu và hợp đồng sync chung](SEM-14.md) | Trí | `docs/mechanisms/SHARED_SYNC.md` | `docs/evidence/SEM-14/CHECKS.md` | Done |
| Hoàn tất | [SEM-37 — Chốt bản ứng viên và manifest phục vụ tập chính](SEM-37.md) | Trí | `release/CANDIDATE_MANIFEST.json`<br>`docs/evidence/SEM-37/CANDIDATE_GATE.md` | `docs/evidence/SEM-37/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-31 12:44:19 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trí cần làm

1. Viết nội dung mở bài/câu hỏi trigger-to-cache và thao tác thiết bị cho demo.
2. Liên kết bản ứng viên, mode/reset và phương án mở log/video trong đúng phần nói.
3. Bàn giao file nội dung riêng; không chỉnh deck chính của Tuấn.

## Đầu ra bắt buộc

- `slides/inputs/TRI.md`
- `docs/evidence/SEM-46/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Lời dẫn khớp scope/candidate thật, ghi rõ live và playback.
- [ ] Không thêm tính năng hoặc lời hứa độ trễ chưa được evidence hỗ trợ.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-51](SEM-51.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Trí thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
