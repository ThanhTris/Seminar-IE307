# Periodic background fetch trên Android

Phần này mô tả cơ chế trong app seminar: WorkManager giữ một yêu cầu định kỳ có ràng buộc mạng, sau đó gọi cùng `SyncWorker`/`SyncRepository` mà các trigger khác dùng. Đăng ký lịch, worker bắt đầu, GET hoàn tất và snapshot được commit là các mốc riêng.

## Ai quyết định lúc chạy?

App mô tả yêu cầu công việc bằng `PeriodicWorkRequest`; WorkManager lưu và lập lịch bền vững, thường dựa trên `JobScheduler` khi app chạy nền. Hệ điều hành quyết định khi tài nguyên và điều kiện cho phép. Khoảng lặp là khoảng tối thiểu giữa các chu kỳ, không phải lời hẹn chạy vào đúng phút đó. Lịch có thể trễ do Doze, standby bucket, giới hạn tài nguyên, app bị force-stop, thiết bị tắt hoặc constraint chưa thỏa. Khi constraint mất trong lúc worker đang chạy, WorkManager có thể dừng worker rồi thử lại khi điều kiện được đáp ứng.

Trong bản app này, thư viện được khóa là `androidx.work:work-runtime-ktx:2.12.0`. Chu kỳ mặc định là 15 phút — mức tối thiểu của `PeriodicWorkRequest`; code từ chối giá trị thấp hơn. Lượt đầu có thể chạy ngay hoặc khi constraint thỏa; lượt sau tuân theo các cửa sổ chu kỳ không chính xác. Chỉ đặt `NetworkType.CONNECTED`, vì sync cần truy cập server và không yêu cầu Wi-Fi không giới hạn. Đăng ký dùng tên duy nhất `periodic_bulletin_sync`; đăng ký lại cập nhật yêu cầu có cùng tên thay vì tạo một chuỗi lịch độc lập. Hủy dùng cùng tên duy nhất.

## Trạng thái là các sự kiện khác nhau

| Mốc | Điều gì đã xảy ra | Điều gì chưa thể kết luận |
|---|---|---|
| `periodic_registered` | WorkManager operation hoàn tất và một unique WorkInfo active được quan sát | Worker đã chạy hoặc server đã nhận request |
| `work_started` | `SyncWorker` thực sự bắt đầu | GET thành công hoặc có dữ liệu mới |
| `snapshot_fetch_completed` (khi instrument fetch) | HTTP fetch có kết quả | Room đã commit snapshot |
| `snapshot_applied` | Snapshot version mới đã commit nguyên tử với cache | Trigger khác không xảy ra cùng lúc |
| `snapshot_unchanged` / `snapshot_stale` | Server trả version bằng / thấp hơn cache | Bản tin mới đã được áp dụng |
| `sync_retrying` / `sync_failed` | Lỗi phân loại transient còn lượt thử / lỗi dừng | Nên suy ra mất mạng vĩnh viễn nếu không có bằng chứng |

Work định kỳ thường lặp trạng thái `ENQUEUED → RUNNING → ENQUEUED`; nó không kết thúc bằng `SUCCEEDED` như one-time work. Một `work_id` có thể đại diện nhiều chu kỳ, vì vậy mỗi chu kỳ cần correlation/request ID riêng khi event instrumentation đầy đủ được tích hợp.

## Network, Doze và cách diễn giải

`CONNECTED` có nghĩa điều kiện mạng của WorkManager được thỏa; nó không đảm bảo DNS, TLS, server hoặc API đang hoạt động. Nếu mất mạng, constraint trì hoãn lượt chạy; nếu mạng mất khi worker đang chạy, WorkManager có thể dừng worker. Lỗi HTTP tạm thời cũng được retry hữu hạn bởi worker, còn lỗi response/HTTP vĩnh viễn được ghi failure.

Trong Doze, Android hạn chế mạng và trì hoãn `JobScheduler`; WorkManager không phải cơ chế đánh thức chính xác theo đồng hồ. Không dùng force-run để kết luận periodic tự nhiên đã chạy đúng hạn. Force-run, enqueue manual, `adb shell cmd jobscheduler run`, hoặc ép thoát Doze là thao tác chẩn đoán riêng, phải gắn nhãn và loại khỏi số đo run tự nhiên. Một worker bắt đầu sau khi màn hình bật có thể do điều kiện vừa được mở, không chứng minh lịch chạy trong Doze.

Không kết luận tiết kiệm pin từ số request/DB write. Cần phép đo năng lượng riêng mới hỗ trợ được kết luận đó.

## Nguồn kỹ thuật

- [Android Developers: Define work requests](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work) — chu kỳ tối thiểu, flex, constraints và sai số thời điểm.
- [AndroidX `PeriodicWorkRequest` API reference](https://developer.android.com/reference/androidx/work/PeriodicWorkRequest) — lifecycle, 15 phút tối thiểu, Doze và constraint.
- [Android Developers: Optimize for Doze and App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby) — giới hạn mạng và job trong Doze.
- Dependency trong repo: `android/gradle/libs.versions.toml`, WorkManager `2.12.0`.

Các trang Android là tài liệu sống; kiểm tra lại khi cập nhật WorkManager/target SDK và ghi phiên bản dependency thật của run.
