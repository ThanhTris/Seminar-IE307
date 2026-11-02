# SEM-27 — Triển khai server snapshot và CLI cập nhật

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Chờ đầu vào**.
- Đối chiếu Project: 2026-11-02 02:54:44 UTC.
- Người thực hiện duy nhất: **Tâm** (`HoaiTam`).
- Hạn: **31/10/2026 17:00 (UTC+7)**.
- Công sức: 4/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-04](SEM-04.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-13](SEM-13.md), [SEM-26](SEM-26.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-13 — Kiểm môi trường Node và quyền Firebase](SEM-13.md) | Tâm | `docs/environment/SERVER_FIREBASE.md` | `docs/evidence/SEM-13/CHECKS.md` | Done |
| Bắt đầu | [SEM-26 — Chốt hợp đồng API và event schema](SEM-26.md) | Tâm | `docs/API.md`<br>`docs/EVENT_SCHEMA.md` | `docs/evidence/SEM-26/CHECKS.md` | Review |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-11-02 02:54:44 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Tâm cần làm

1. Tạo server Node/TypeScript, lockfile và cấu hình mẫu; hiện thực health/read/update snapshot.
2. Persist snapshot và version tăng đơn điệu qua restart; CLI cập nhật và log theo schema.
3. Viết cách chạy/kết nối từ emulator và OPPO; không tạo dashboard hay auth sản phẩm.

## Đầu ra bắt buộc

- `server/ (API, snapshot store, update CLI)`
- `docs/setup/SERVER.md`
- `docs/evidence/SEM-27/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Đọc/update/restart không giảm version, payload và lỗi khớp API.md.
- [ ] Log đối chiếu được run/request; cấu hình thật giữ local.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-28](SEM-28.md) cần đầu ra này để **bắt đầu**.
- [SEM-35](SEM-35.md) cần đầu ra này để **bắt đầu**.
- [SEM-40](SEM-40.md) cần đầu ra này để **bắt đầu**.
- [SEM-49](SEM-49.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Tâm thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
