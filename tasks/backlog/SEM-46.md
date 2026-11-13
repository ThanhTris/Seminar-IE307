# SEM-46 — Viết phần mở bài và bàn giao lời dẫn thao tác demo

- Trạng thái: **In Progress** (Project).
- Trạng thái đầu vào: **Đang thực hiện**.
- Còn chờ: Nên nhận: [SEM-37](SEM-37.md).
- Đối chiếu Project: 2026-11-12 14:11:12 UTC.
- Người thực hiện duy nhất: **Tuấn** (`mtuan2491`).
- Hạn: **08/11/2026 16:00 (UTC+7)**.
- Công sức: 1/100 — Nghiên cứu/lập luận.
- Tách từ nhóm cũ: [SEM-09](SEM-09.md); nhóm cũ chỉ còn lưu lịch sử.

> **Đầu ra tài liệu SEM-46 đã hoàn tất ngày 12/11/2026 để review và bàn giao SEM-51.** Áp dụng quy tắc `cc2bd1c`, candidate SEM-37, live FCM và diễn tập được ghi Not run/giới hạn trong CHECKS. Nhánh có TRI.md và hồ sơ kiểm cuối để Tuấn đọc trước khi gửi nhóm trưởng kiểm nhận.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** [SEM-14](SEM-14.md), [SEM-37](SEM-37.md)

Không có gate bắt đầu nghĩa là làm được ngay. Mục Hoàn tất còn cần là đầu vào nên dùng nếu đã có, không chặn chuyển Done: owner chuyển Done khi đầu ra và CHECKS của chính task có thật; đầu vào chưa có thì ghi Not run/giới hạn trong CHECKS. Bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Kịch bản 15 phút](../../docs/PRESENTATION_PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Hoàn tất | [SEM-14 — Vẽ luồng dữ liệu và hợp đồng sync chung](SEM-14.md) | Trí | `docs/mechanisms/SHARED_SYNC.md` | `docs/evidence/SEM-14/CHECKS.md` | Done |
| Hoàn tất | [SEM-37 — Chốt bản ứng viên và manifest phục vụ tập chính](SEM-37.md) | Trung | `release/CANDIDATE_MANIFEST.json`<br>`docs/evidence/SEM-37/CANDIDATE_GATE.md` | `docs/evidence/SEM-37/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-11-12 14:11:12 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Tuấn cần làm

1. Viết nội dung mở bài/câu hỏi trigger-to-cache và thao tác thiết bị cho demo.
2. Liên kết bản ứng viên, mode/reset và phương án mở log/video trong đúng phần nói.
3. Bàn giao file nội dung riêng cho phần mở bài do Trí trình bày; deck chính được ghép ở SEM-51.

## Đầu ra bắt buộc

- `slides/inputs/TRI.md`
- `docs/evidence/SEM-46/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [x] Lời dẫn đã đối chiếu với scope/source baseline, có nhãn LIVE/CONTRACT/PLAYBACK/PROTOCOL. Candidate thật ghi Not run theo quy tắc ngày 12/11 trong CHECKS.
- [x] Nội dung bám các event và evidence đã nhận, ngưỡng chuyển 30 giây được ghi là ngân sách điều phối.
- [x] TRI.md và CHECKS có thật, link đã kiểm, candidate/live/video/diễn tập ghi đúng Not run.

## Các bước đã thực hiện

1. **Đã soạn và commit** mở bài, vai nói và mốc cơ chế trong TRI.md, commit `acf341e`.
2. **Đã soạn** kịch bản thao tác và phiếu cấu hình tại `1369893`, nhận main ngày 12/11 tại `107d271`, chốt mode/CLI/evidence và phương án phối hợp SEM-47 tại `175257e`.
3. **Đã kiểm cuối và hoàn tất bàn giao** theo policy hiện hành, candidate và các run thiếu ghi Not run trong [CHECKS](../../docs/evidence/SEM-46/CHECKS.md). Nội dung dùng cho SEM-51 ở [TRI.md](../../slides/inputs/TRI.md).

## Task được mở khóa

- [SEM-51](SEM-51.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Tuấn thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
