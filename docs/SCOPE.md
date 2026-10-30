# Phạm vi demo Seminar IE307

Cập nhật 30/10/2026 theo kế hoạch hiện hành. Đây là phạm vi sản phẩm demo, không phải xác nhận rằng app hoặc backend đã được triển khai.

## Mục tiêu

Xây một demo Android nhỏ dạng bảng tin môn học để quan sát việc dữ liệu mới đi từ server vào cache khi ứng dụng ở nền. Người nghe cần phân biệt được trigger, lúc worker thật sự chạy và lúc snapshot mới được áp dụng.

## Phạm vi chức năng

- Một bảng tin và một snapshot nhỏ có `version` tăng đơn điệu.
- Ba mode thử nghiệm: `PERIODIC` dùng periodic WorkManager; `PUSH` dùng tín hiệu FCM data-only; `HYBRID` kết hợp hai trigger.
- Cả ba mode dùng chung sync engine và Room cache. UI hiển thị snapshot/version trong cache, mode, lần đồng bộ gần nhất và timeline có thể lọc theo `run_id`.
- Mở UI trong ca thử chỉ đọc cache. Đồng bộ thủ công, nếu có, được gắn nhãn riêng và không tính là kết quả đồng bộ nền.
- Silent Push dùng FCM HTTP v1 với Android message data-only và normal priority. Không dùng notification payload hoặc high priority để tạo cảm giác cập nhật tức thời. `FCM accepted`, callback nhận được, worker chạy và snapshot áp dụng là các sự kiện riêng.

## Nền tảng và cách trình bày

- Android native: Kotlin, Jetpack Compose, Room, WorkManager và Firebase Messaging.
- Bài trình bày dài 15 phút, gồm demo 4 phút. Demo cho thấy cơ chế cùng giới hạn; kết quả phải truy về log/run thực, không trình bày dữ liệu minh họa như kết quả đo.
- Thiết bị dự kiến là Android emulator và OPPO Find X9. Phiên bản Android/API/ColorOS và khả năng kết nối thực tế được ghi ở các task thiết bị tương ứng.

## Ngoài phạm vi

- iOS, đa người dùng, đăng nhập sản phẩm và thiết kế UI cầu kỳ.
- Dashboard web, benchmark pin và phát hành ứng dụng lên store.
- Scheduler riêng, foreground service hoặc alarm để né chính sách chạy nền Android.
- Tuyên bố rằng periodic chạy đúng giờ, push luôn đến tức thì hoặc hybrid vượt được Doze/force-stop.

## Ranh giới task và câu hỏi còn mở

- **SEM-11 (Trí):** phạm vi demo và baseline Android build; các giá trị build được chốt trong [ANDROID_BUILD.md](environment/ANDROID_BUILD.md).
- **SEM-12 (Vinh):** hồ sơ emulator/OPPO, phiên bản hệ điều hành thực tế, trạng thái ADB và lịch sử dụng thiết bị.
- **SEM-13 (Tâm):** Node/Firebase project và quyền gửi test, cấu hình server, phương án kết nối LAN/ADB reverse/tunnel và kiểm tra Internet tới FCM.
- Package ID được chọn cho scaffold Android: `com.thanhtris.seminarie307`.
- Firebase project cụ thể, quyền truy cập và file cấu hình Firebase vẫn chờ SEM-13; không tạo hoặc lưu credential trong task này.
- Rubric riêng của giảng viên chưa có trong repo; nếu được cung cấp, đối chiếu lại trước khi chốt slide.
