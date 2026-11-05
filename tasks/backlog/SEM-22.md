# SEM-22 — Đối chiếu hai bài nghiên cứu với API push hiện hành

- Trạng thái: **In Progress** (Project).
- Trạng thái đầu vào: **Sẵn sàng**.
- Đối chiếu Project: 2026-11-05 05:25:56 UTC.
- Người thực hiện duy nhất: **Trang** (`rosy179`).
- Hạn: **01/11/2026 22:00 (UTC+7)**.
- Công sức: 2/100 — Nghiên cứu/lập luận.
- Tách từ nhóm cũ: [SEM-03](SEM-03.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** [SEM-15](SEM-15.md), [SEM-20](SEM-20.md), [SEM-21](SEM-21.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Nguồn kỹ thuật và nghiên cứu](../../research/README.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Hoàn tất | [SEM-15 — Giải thích cơ chế silent push và giới hạn FCM](SEM-15.md) | Trang | `docs/mechanisms/SILENT_PUSH.md` | `docs/evidence/SEM-15/CHECKS.md` | Done |
| Hoàn tất | [SEM-20 — Đọc bài nghiên cứu thứ nhất và ghi chú nguồn](SEM-20.md) | Tuấn | `research/notes/PAPER_1.md`<br>`research/metadata/paper-1.bib` | `docs/evidence/SEM-20/CHECKS.md` | Done |
| Hoàn tất | [SEM-21 — Đọc bài nghiên cứu thứ hai và ghi chú nguồn](SEM-21.md) | Tâm | `research/notes/PAPER_2.md`<br>`research/metadata/paper-2.bib` | `docs/evidence/SEM-21/CHECKS.md` | Done |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-11-05 05:25:56 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trang cần làm

1. Chuẩn bị bảng documentation cho FCM v1/data-only/normal priority ngay.
2. Khi hai ghi chú paper có sẵn, đối chiếu claim push với API/OS version của demo.
3. Đánh dấu claim còn là giả thuyết và case cần evidence; ghi EAP khác baseline ở phụ lục.

## Đầu ra bắt buộc

- `research/notes/API_CROSSCHECK.md`
- `docs/evidence/SEM-22/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [x] Mỗi dòng có nguồn/vị trí/version và giới hạn, không trộn kết quả paper với demo.
- [x] Không yêu cầu paper hoàn tất mới bắt đầu đọc tài liệu API; chỉ gate bản đối chiếu cuối.
- [x] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Đầu ra đã soát ngày 05/11/2026

[API_CROSSCHECK 1.0.0](../../research/notes/API_CROSSCHECK.md) · [CHECKS SEM-22](../../docs/evidence/SEM-22/CHECKS.md).

Đã hoàn thành đối chiếu hai bài nghiên cứu với API push và scheduler hiện hành:
1. Chuẩn hóa bảng documentation FCM HTTP v1 data-only normal priority (TTL 24h, payload < 1 KB, WorkManager handoff).
2. Đối chiếu Paper 1 (Simon et al., 2017): chu kỳ rỗng 96.8% trên iOS 7 vs WorkManager interval tối thiểu 15 phút, giải quyết Lost Wake-Up bằng WorkManager REPLACE và Room Version Guard thay cho cờ in-memory loopOnceMore, và nguyên tắc tách trigger khỏi snapshot payload.
3. Đối chiếu Paper 2 (González-Pérez et al., 2022): lập lịch dự kiến khác thực thi trên Doze/Standby Buckets (tỷ lệ miss 84%), phân tích các kỹ thuật lách luật bị Google cấm (exact alarm, foreground service), và phân mảnh OEM (ColorOS trên OPPO Find X9).
4. Bảng ma trận 8 claims chi tiết có vị trí mục/trang trong paper, API hiện hành, đánh giá và gắn mã ca thử nghiệm E01–E06.
5. Luận giải định vị mô hình HYBRID của Seminar IE307 từ góc độ học thuật.

Đây là bàn giao nghiên cứu đối chiếu học thuật của SEM-22; các ca đo thực nghiệm vẫn **Not run** để bàn giao cho các task pilot/main runs downstream. Checklist này không tự chuyển Status Project sang Done; các trường Project phía trên vẫn là snapshot hiện hành.

## Task được mở khóa

- [SEM-50](SEM-50.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Trang thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
