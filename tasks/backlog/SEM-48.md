# SEM-48 — Viết nội dung và biểu đồ kết quả cho bài nói

- Trạng thái: **Done** (Project).
- Trạng thái đầu vào: **Đã hoàn thành**.
- Còn chờ: Không.
- Đối chiếu Project: 2026-11-18 02:33:31 UTC.
- Người thực hiện duy nhất: **Vinh** (`Vinh5905`).
- Hạn: **08/11/2026 18:00 (UTC+7)**.
- Công sức: 1/100 — Nghiên cứu/lập luận.
- Tách từ nhóm cũ: [SEM-09](SEM-09.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** [SEM-43](SEM-43.md), [SEM-44](SEM-44.md), [SEM-45](SEM-45.md)

Không có gate bắt đầu nghĩa là làm được ngay. Mục Hoàn tất còn cần là đầu vào nên dùng nếu đã có, không chặn chuyển Done: owner chuyển Done khi đầu ra và CHECKS của chính task có thật; đầu vào chưa có thì ghi Not run/giới hạn trong CHECKS. Bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Kịch bản 15 phút](../../docs/PRESENTATION_PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Hoàn tất | [SEM-43 — Chốt SUMMARY và bộ evidence thực nghiệm](SEM-43.md) | Vinh | `experiments/SUMMARY.md` | `docs/evidence/SEM-43/CHECKS.md` | Done |
| Hoàn tất | [SEM-44 — Kiểm độc lập trigger và phép tính dữ liệu main](SEM-44.md) | Tâm | `experiments/AUDIT.md` | `docs/evidence/SEM-44/CHECKS.md` | Review |
| Hoàn tất | [SEM-45 — Viết parser log và sinh results.csv](SEM-45.md) | Tuấn | `experiments/scripts/analyze.*`<br>`experiments/results.csv` | `docs/evidence/SEM-45/CHECKS.md` | In Progress |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-11-18 02:33:31 UTC**; mở link task nguồn để xem cập nhật mới hơn.
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
- [x] Không kết luận pin hoặc mọi Android từ request count/OPPO.
- [x] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Tiến độ ngày 16/11/2026

- Đã nhận SUMMARY ở head `fce39b0` của PR SEM-43 #31 (chưa merge khi nhận). Hoàn thiện [VINH.md](../../slides/inputs/VINH.md): lời dẫn 105 giây, bản rút 75 giây, nguồn run/build và Q&A; đây là ngân sách nói, chưa diễn tập đo thời lượng.
- [Bộ results](../../slides/inputs/results/README.md) có hai hình PNG/SVG, hai CSV phục vụ vẽ, renderer/dependency và INPUTS/hash. Inventory giữ 8 pilot VALID/SUCCESS mới cùng 12 INVALID cũ; main 0 run/33 slot kế hoạch ghi NOT_RUN, rate/median N/A.
- Biểu đồ hiệu năng main từ CSV đã audit **NOT_RUN**: Draft SEM-45 #30 chỉ chứa 12 pilot cũ INVALID, chưa có tám pilot mới; SEM-44 chưa ký bộ mới. Không dùng ảnh pilot thay biểu đồ main hoặc sửa output của owner khác.
- [CHECKS](../../docs/evidence/SEM-48/CHECKS.md) và [VERIFICATION](../../docs/evidence/SEM-48/VERIFICATION.json) ghi tái sinh/đối chiếu ảnh-data và giới hạn. Đã chuẩn bị đầy đủ input có thể dùng cho SEM-51; cập nhật khi nhận main/CSV/audit, không tự chuyển trạng thái Project.

## Sửa theo review ngày 17/11/2026

- Đã merge main `1475e67` sau khi SEM-43 #31 merge. Giữ source `fce39b0` vì commit nguồn vẫn nằm trong main và 71 file nguồn không đổi.
- Sửa kiểm input để chấp nhận CRLF/LF nhưng giữ hash Git blob chính xác; SVG ép ghi LF. Thêm 7 regression tests và workflow Windows/autocrlf kiểm SHA-256 đủ 6 artifact. Windows native/Python 3.12 với autocrlf=true đạt 7/7 tests, 51/71 source CRLF và 6/6 SHA-256 khớp; báo cáo CI lưu trong evidence. Dữ liệu/ảnh/scope main NOT_RUN không đổi; xem CHECKS và VERIFICATION cho bằng chứng review.

## Task được mở khóa

- [SEM-51](SEM-51.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Vinh thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
