# SEM-14 — Vẽ luồng dữ liệu và hợp đồng sync chung

- Trạng thái: **Done** (Project).
- Trạng thái đầu vào: **Sẵn sàng**.
- Đối chiếu Project: 2026-10-30 20:34:26 UTC.
- Người thực hiện duy nhất: **Trí** (`ThanhTris`).
- Hạn: **30/10/2026 14:00 (UTC+7)**.
- Công sức: 1/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-02](SEM-02.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** [SEM-11](SEM-11.md)
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md).

| Cần cho | Task cung cấp | Người bàn giao | Đầu ra phải nhận | Kiểm chứng bàn giao | Status nguồn |
|---|---|---|---|---|---|
| Bắt đầu | [SEM-11 — Chốt phạm vi và môi trường build Android](SEM-11.md) | Trí | `docs/SCOPE.md`<br>`docs/environment/ANDROID_BUILD.md` | `docs/evidence/SEM-11/CHECKS.md` | Done |

Đây là danh sách đầu ra cần bàn giao, chưa phải xác nhận các file đã tồn tại. Trước khi dùng, nhận đúng artifact/commit/config và CHECKS từ task nguồn.

Status nguồn được đối chiếu Project lúc **2026-10-30 20:34:26 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trí cần làm

1. Mô tả trigger → worker → GET snapshot → transaction Room → timeline.
2. Định nghĩa giao diện enqueue chung: source, mode, run_id, version hint và correlation.
3. Chỉ rõ ranh giới UI/cache, sync core, scheduling, messaging và server để mỗi task sửa đúng phần.

## Đầu ra bắt buộc

- `docs/mechanisms/SHARED_SYNC.md`
- `docs/evidence/SEM-14/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Periodic, push và manual cùng dùng một sync core; UI mở lại chỉ đọc cache.
- [ ] Có hình luồng và bảng input/output đủ để API, app và worker triển khai độc lập.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-19](SEM-19.md) cần đầu ra này để **hoàn tất**.
- [SEM-26](SEM-26.md) cần đầu ra này để **bắt đầu**.
- [SEM-46](SEM-46.md) cần đầu ra này để **hoàn tất**.

## Ranh giới thực hiện

Một task chỉ có Trí thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
