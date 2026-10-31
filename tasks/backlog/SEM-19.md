# SEM-19 — Tổng hợp mô hình cơ chế và câu hỏi phản biện

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chuẩn bị trước**.
- Đối chiếu Project: 2026-10-31 12:44:19 UTC.
- Người thực hiện duy nhất: **Tuấn** (`mtuan2491`).
- Hạn: **30/10/2026 22:00 (UTC+7)**.
- Công sức: 4/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-02](SEM-02.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** [SEM-11](SEM-11.md), [SEM-12](SEM-12.md), [SEM-13](SEM-13.md), [SEM-14](SEM-14.md), [SEM-15](SEM-15.md), [SEM-16](SEM-16.md), [SEM-17](SEM-17.md), [SEM-18](SEM-18.md)

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Hoàn tất | [SEM-11 — Chốt phạm vi và môi trường build Android](SEM-11.md) | Trí | `docs/SCOPE.md`<br>`docs/environment/ANDROID_BUILD.md` | `docs/evidence/SEM-11/CHECKS.md` | Done |
| Hoàn tất | [SEM-12 — Lập hồ sơ OPPO và emulator](SEM-12.md) | Vinh | `docs/environment/DEVICES.md` | `docs/evidence/SEM-12/CHECKS.md` | Todo |
| Hoàn tất | [SEM-13 — Kiểm môi trường Node và quyền Firebase](SEM-13.md) | Tâm | `docs/environment/SERVER_FIREBASE.md` | `docs/evidence/SEM-13/CHECKS.md` | Done |
| Hoàn tất | [SEM-14 — Vẽ luồng dữ liệu và hợp đồng sync chung](SEM-14.md) | Trí | `docs/mechanisms/SHARED_SYNC.md` | `docs/evidence/SEM-14/CHECKS.md` | Done |
| Hoàn tất | [SEM-15 — Giải thích cơ chế silent push và giới hạn FCM](SEM-15.md) | Trang | `docs/mechanisms/SILENT_PUSH.md` | `docs/evidence/SEM-15/CHECKS.md` | Todo |
| Hoàn tất | [SEM-16 — Lập ma trận lifecycle và protocol E01–E06](SEM-16.md) | Vinh | `experiments/PROTOCOL.md`<br>`experiments/RUN_SCHEDULE.md` | `docs/evidence/SEM-16/CHECKS.md` | Todo |
| Hoàn tất | [SEM-17 — Giải thích periodic WorkManager và constraints](SEM-17.md) | Trung | `docs/mechanisms/PERIODIC_FETCH.md` | `docs/evidence/SEM-17/CHECKS.md` | Todo |
| Hoàn tất | [SEM-18 — Giải thích server, FCM accepted và correlation](SEM-18.md) | Tâm | `docs/mechanisms/SERVER_FCM.md` | `docs/evidence/SEM-18/CHECKS.md` | Todo |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-31 12:44:19 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Tuấn cần làm

1. Soạn khung MECHANISMS và QUESTIONS ngay từ kế hoạch; nhận tài liệu từng nguồn vào khi được bàn giao.
2. Tổng hợp hai sơ đồ trigger-to-cache, bảng thuật ngữ, lifecycle, giới hạn và phạm vi version.
3. Viết ít nhất 10 câu hỏi kèm đáp án ngắn và nguồn; ghi giả thuyết, chưa ghi kết quả đo.

## Đầu ra bắt buộc

- `docs/MECHANISMS.md`
- `docs/QUESTIONS.md`
- `docs/evidence/SEM-19/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Các phần tham chiếu đúng đầu ra riêng của SEM-14…18, không yêu cầu người khác cùng viết file tổng hợp.
- [ ] Cơ chế, API và cấu hình môi trường khớp; giải thích được hai luồng không cần đọc code.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-50](SEM-50.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Tuấn thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
