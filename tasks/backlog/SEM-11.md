# SEM-11 — Chốt phạm vi và môi trường build Android

- Trạng thái: **Todo** (Project).
- Trạng thái đầu vào: **Sẵn sàng**.
- Đối chiếu Project: 2026-10-29 16:22:16 UTC.
- Người thực hiện duy nhất: **Trí** (`ThanhTris`).
- Hạn: **2026-10-29** (UTC+7).
- Công sức: 3/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-01](SEM-01.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là có thể chuẩn bị ngay. Gate hoàn tất chỉ chặn bàn giao cuối; bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md).

Không cần nhận đầu ra từ task khác để bắt đầu. Owner thực hiện từ tài liệu nền và tự ghi các blocker môi trường/quyền truy cập trong CHECKS của task này.

Status nguồn được đối chiếu Project lúc **2026-10-29 16:22:16 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trí cần làm

1. Ghi SCOPE: Kotlin native, ba mode, demo 15 phút và các tính năng ngoài phạm vi.
2. Kiểm JDK/Android SDK/Gradle/ADB trên máy build; pin phiên bản stable và application ID.
3. Ghi kết quả lệnh thật và blocker; bàn giao cấu hình build cho scaffold Android.

## Đầu ra bắt buộc

- `docs/SCOPE.md`
- `docs/environment/ANDROID_BUILD.md`
- `docs/evidence/SEM-11/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [ ] Lệnh kiểm công cụ có version và kết quả thực; không suy cấu hình máy từ kế hoạch.
- [ ] Nêu rõ baseline FCM v1/data-only/normal priority và giới hạn demo.
- [ ] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Task được mở khóa

- [SEM-14](SEM-14.md) cần đầu ra này để **bắt đầu**.
- [SEM-19](SEM-19.md) cần đầu ra này để **hoàn tất**.
- [SEM-20](SEM-20.md) cần đầu ra này để **hoàn tất**.
- [SEM-21](SEM-21.md) cần đầu ra này để **hoàn tất**.
- [SEM-23](SEM-23.md) cần đầu ra này để **bắt đầu**.
- [SEM-26](SEM-26.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trí thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
