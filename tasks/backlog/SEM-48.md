# SEM-48 — Viết nội dung và biểu đồ kết quả cho bài nói

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chuẩn bị trước**.
- Đối chiếu Project: 2026-11-02 02:54:44 UTC.
- Người thực hiện duy nhất: **Vinh** (`Vinh5905`).
- Hạn: **08/11/2026 18:00 (UTC+7)**.
- Công sức: 1/100 — Nghiên cứu/lập luận.
- Tách từ nhóm cũ: [SEM-09](SEM-09.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** [SEM-43](SEM-43.md), [SEM-44](SEM-44.md), [SEM-45](SEM-45.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Kịch bản 15 phút](../../docs/PRESENTATION_PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Hoàn tất | [SEM-43 — Chốt SUMMARY và bộ evidence thực nghiệm](SEM-43.md) | Vinh | `experiments/SUMMARY.md` | `docs/evidence/SEM-43/CHECKS.md` | Todo |
| Hoàn tất | [SEM-44 — Kiểm độc lập trigger và phép tính dữ liệu main](SEM-44.md) | Trung | `experiments/AUDIT.md` | `docs/evidence/SEM-44/CHECKS.md` | Todo |
| Hoàn tất | [SEM-45 — Viết parser log và sinh results.csv](SEM-45.md) | Tuấn | `experiments/scripts/analyze.*`<br>`experiments/results.csv` | `docs/evidence/SEM-45/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-11-02 02:54:44 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Vinh cần làm

1. Tạo bảng/biểu đồ từ CSV đã audit, có số mẫu, timeout, thiết bị và build.
2. Soạn lời dẫn phần kết quả 1 phút 45 giây và giới hạn mẫu/clock/OS.
3. Bàn giao input có link run/evidence và ảnh/plot tái sinh được.

## Đầu ra bắt buộc

- `slides/inputs/VINH.md`
- `slides/inputs/results/`
- `docs/evidence/SEM-48/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Biểu đồ đúng số liệu main, có n_complete/n_total và không giấu kết quả trái giả thuyết.
- [ ] Không kết luận pin hoặc mọi Android từ request count/OPPO.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-51](SEM-51.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Vinh thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
