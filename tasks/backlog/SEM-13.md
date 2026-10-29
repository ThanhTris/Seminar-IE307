# SEM-13 — Kiểm môi trường Node và quyền Firebase

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Sẵn sàng**.
- Đối chiếu Project: 2026-10-29 16:22:16 UTC.
- Người thực hiện duy nhất: **Tâm** (`HoaiTam`).
- Hạn: **2026-10-29** (UTC+7).
- Công sức: 1/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-01](SEM-01.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Nguồn kỹ thuật và nghiên cứu](../../research/README.md).

Không cần nhận đầu ra từ task khác để bắt đầu. Owner thực hiện từ tài liệu nền và tự ghi các blocker môi trường/quyền truy cập trong CHECKS của task này.

Status nguồn được đối chiếu Project lúc **2026-10-29 16:22:16 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Tâm cần làm

1. Kiểm Node/package manager và phương án Firebase project cho demo.
2. Ghi quyền gửi test, cấu hình local và cách cấp cấu hình cho app/server.
3. Kiểm phương án kết nối LAN/ADB reverse và Internet tới FCM.

## Đầu ra bắt buộc

- `docs/environment/SERVER_FIREBASE.md`
- `docs/evidence/SEM-13/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Có phiên bản thực và kết quả quyền/kết nối hoặc blocker, không ghi đã gửi thành công nếu chưa gửi.
- [ ] Chỉ commit cấu hình mẫu; không đưa token/service-account key/google-services.json thật vào repo.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-19](SEM-19.md) cần đầu ra này để **hoàn tất**.
- [SEM-26](SEM-26.md) cần đầu ra này để **bắt đầu**.
- [SEM-27](SEM-27.md) cần đầu ra này để **bắt đầu**.
- [SEM-33](SEM-33.md) cần đầu ra này để **bắt đầu**.
- [SEM-35](SEM-35.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Tâm thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
