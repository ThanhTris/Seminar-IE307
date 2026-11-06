# Câu hỏi phản biện — SEM-19

Tuấn (`mtuan2491`), khởi tạo 03/11, **chốt ngày 06/11/2026 (UTC+7)**. Bộ 25 câu hỏi đi cùng [MECHANISMS](MECHANISMS.md), đã đối chiếu SEM-14..18 và contract; [INPUT_REVIEW](evidence/SEM-19/INPUT_REVIEW.md) ghi chi tiết tiếp nhận SEM-15. Đáp án mô tả cơ chế hoặc thiết kế; **không phải kết quả đo**.

## 1. Background Fetch trong đề tài có phải tên một API Android không?

Không. Trong seminar, đó là khái niệm lấy dữ liệu nền được ánh xạ sang periodic WorkManager. Cần nói rõ nền tảng và cơ chế đang minh họa.

Nguồn: [SCOPE](SCOPE.md), [PLAN](PLAN.md). Phạm vi: quyết định của project.

## 2. Đặt chu kỳ 15 phút có bảo đảm worker chạy đúng từng mốc không?

Không. Đây là interval tối thiểu được cấu hình, còn thời điểm chạy phụ thuộc điều kiện hệ thống. Ca E01 phải giữ lịch ổn định và quan sát tự nhiên; force-run không chứng minh thời điểm chạy thật.

Nguồn: [SEM-17](mechanisms/PERIODIC_FETCH.md), [Define work requests](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work). Kiểm chứng sau: E01/E03.

## 3. Vì sao đã ghi periodic_registered mà chưa có bản tin mới?

Event chỉ xác nhận lịch được chấp nhận. Cần kiểm `work_started`, kết quả GET và `snapshot_applied` riêng; worker cũng có thể thấy version không đổi hoặc lỗi.

Nguồn: [EVENT_SCHEMA](EVENT_SCHEMA.md), [MECHANISMS mục 5](MECHANISMS.md#5-ranh-giới-bằng-chứng-và-đồng-bộ-dùng-chung). Phạm vi: ranh giới evidence.

## 4. Constraint CONNECTED có bảo đảm gọi API thành công không?

Không. Nó là điều kiện mạng của scheduler; DNS, TLS, địa chỉ server hoặc response API vẫn có thể lỗi. Phải phân loại lỗi và chỉ retry hữu hạn theo core.

Nguồn: [SEM-17](mechanisms/PERIODIC_FETCH.md), [API](API.md). Kiểm chứng sau: E04.

## 5. Silent push có phải một notification bị tắt âm thanh không?

Không. Demo chọn data-only, không có notification payload và không tạo thông báo hiển thị. Loại payload quyết định cách xử lý; tắt tiếng một notification không đổi nó thành tín hiệu data-only.

Nguồn: [SCOPE](SCOPE.md), [SEM-15](mechanisms/SILENT_PUSH.md), [Firebase receive messages](https://firebase.google.com/docs/cloud-messaging/android/receive-messages). Phạm vi: baseline AndroidConfig v1, không trộn notification/mixed với data-only.

## 6. Callback có thể tải snapshot và xử lý tùy ý đến khi xong không?

Không nên dựa vào cửa sổ callback ngắn để chạy tác vụ dài. Thiết kế ghi receipt, kiểm input và enqueue worker chung; công việc sync diễn ra trong worker. Không coi mốc 50/100ms ở blueprint là cam kết thời gian của OS.

Nguồn: [SEM-15](mechanisms/SILENT_PUSH.md), [SHARED_SYNC](mechanisms/SHARED_SYNC.md), [Firebase receive messages](https://firebase.google.com/docs/cloud-messaging/android/receive-messages). Runtime thuộc các task callback/core.

## 7. Vì sao FCM trả message ID nhưng cache vẫn cũ?

ID từ send chỉ xác nhận accepted for delivery. Còn phải quan sát callback, enqueue, worker, HTTP và transaction. Không có `snapshot_applied` thì chưa đủ kết luận cache đã cập nhật.

Nguồn: [SEM-15](mechanisms/SILENT_PUSH.md), [SEM-18](mechanisms/SERVER_FCM.md), [Message lifespan](https://firebase.google.com/docs/cloud-messaging/customize-messages/setting-message-lifespan). Kiểm chứng runtime: E02/E04; thiếu applied không tự xác định lỗi thuộc FCM hay worker.

## 8. Vì sao không tăng high priority để demo luôn nhanh?

Baseline normal priority phục vụ câu hỏi đồng bộ không khẩn cấp. Đổi priority sẽ đổi điều kiện thí nghiệm; high priority có mục đích riêng cho nội dung cần người dùng chú ý và cũng không chứng minh transaction hoàn tất.

Nguồn: [SCOPE](SCOPE.md), [SEM-15](mechanisms/SILENT_PUSH.md), [Firebase priority](https://firebase.google.com/docs/cloud-messaging/android-message-priority). Không hứa độ trễ hoặc dùng một lần nhận nhanh làm SLA.

## 9. TTL 24 giờ có nghĩa worker sẽ hoàn tất trong 24 giờ không?

Không. TTL của protocol là thời gian giữ tin tại FCM, không phải timeout worker. Sau khi app nhận và enqueue, không suy worker bị hủy chỉ vì TTL của message hết; outcome phải đọc từ work/cache events.

Nguồn: [protocol SEM-16](../experiments/PROTOCOL.md), [SEM-15](mechanisms/SILENT_PUSH.md), [SEM-18](mechanisms/SERVER_FCM.md), [Message lifespan](https://firebase.google.com/docs/cloud-messaging/customize-messages/setting-message-lifespan). TTL/collapse được ghi theo cấu hình run, không suy nguyên nhân mất tin từ timeout.

## 10. Foreground, background, process chết và force-stop có giống nhau không?

Không. UI hiển thị, process còn tồn tại và package stopped là các trục khác nhau. Cần ghi hành động và trạng thái thực tế, không dùng một nhãn “đóng app” cho tất cả.

Nguồn: [ma trận SEM-16](../experiments/PROTOCOL.md), [Processes and app lifecycle](https://developer.android.com/guide/components/activities/process-lifecycle). Kiểm chứng sau: ca lifecycle riêng.

## 11. Vuốt app khỏi Recents có chắc là force-stop không?

Không thể mặc định. Theo protocol phải kiểm task, PID và stopped sau vuốt, đặc biệt trên OEM. Chỉ hành động vuốt chưa đủ phân loại trạng thái.

Nguồn: [protocol SEM-16](../experiments/PROTOCOL.md), [hồ sơ thiết bị](environment/DEVICES.md). Giới hạn: OPPO chưa có máy để kiểm.

## 12. Tắt màn hình có đủ để gọi ca thử là Doze không?

Không. Cần chứng cứ idle state trước, trong và sau ca. Kết quả screen-off đơn thuần không thay E03; Doze và App Standby cũng cần phân biệt.

Nguồn: [SEM-16](../experiments/PROTOCOL.md), [Doze and App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby). Kiểm chứng sau: E03.

## 13. Hybrid có vượt Doze hoặc force-stop không?

Không có cam kết đó. Hybrid thêm hai nguồn kích hoạt cho cùng core và vẫn chịu giới hạn nền. Sau force-stop cần tách mốc người dùng mở lại; E06 chỉ thử một lần bỏ gửi push có chủ ý.

Nguồn: [PLAN](PLAN.md), [SEM-16](../experiments/PROTOCOL.md), [Firebase về mở lại Android sau force-quit trong Settings](https://firebase.google.com/docs/cloud-messaging/flutter/receive-messages). Chỉ dùng điều kiện nền tảng từ nguồn Flutter, không dùng API Flutter cho app Kotlin.

## 14. Hai trigger đến cùng lúc có cần ghi bản tin hai lần không?

Không. Cùng core so version trong transaction: version bằng thì unchanged, thấp hơn thì stale, chỉ version mới hơn được áp dụng. Số GET có thể lớn hơn số lần ghi; idempotence không tự chứng minh coalesce tối ưu.

Nguồn: [SHARED_SYNC](mechanisms/SHARED_SYNC.md), [API](API.md). Kiểm chứng sau: E05 và test logic core.

## 15. Worker đã chạy, tại sao còn cần đọc lại version trong transaction?

Trong lúc GET ở ngoài transaction, một worker khác có thể commit snapshot mới hơn. So lại cached version tại lúc ghi giúp tránh response cũ rollback cache.

Nguồn: [SHARED_SYNC](mechanisms/SHARED_SYNC.md), [API](API.md). Phạm vi: bất biến thiết kế, cần test concurrency.

## 16. Version hint cũ có đủ để bỏ GET không?

Theo contract hiện tại là không: hint chỉ là metadata; server có thể đã có snapshot mới hơn. Worker lấy snapshot hiện hành rồi áp dụng version guard. Stale hint không nhất thiết tạo stale response.

Nguồn: [EVENT_SCHEMA](EVENT_SCHEMA.md), [protocol E05-B](../experiments/PROTOCOL.md). Kiểm chứng sau: E05.

## 17. KEEP, REPLACE và version guard có tự bảo đảm không mất tín hiệu không?

Không được giả định như vậy. KEEP có thể bỏ yêu cầu mới khi work cũ chưa xong; REPLACE hủy work cũ. Version guard ngăn rollback nhưng không tự chứng minh lần sync tiếp theo sẽ chạy hoặc giữ đủ signal. Cần chiến lược và test race đúng implementation.

Nguồn: [SHARED_SYNC](mechanisms/SHARED_SYNC.md), [EVENT_SCHEMA](EVENT_SCHEMA.md), [Managing work](https://developer.android.com/develop/background-work/background-tasks/persistent/how-to/manage-work). Kiểm chứng runtime: SEM-38/39, E05-C.

## 18. Mở app lên thấy version mới có chứng minh đã sync ở nền không?

Chưa đủ. Phải có applied trước mốc mở UI, đúng source/run và không có auto-fetch hoặc MANUAL tạo thành công. Việc UI chỉ đọc Room là điều kiện để tránh nhầm nguyên nhân.

Nguồn: [SCOPE](SCOPE.md), [protocol E02](../experiments/PROTOCOL.md). Phạm vi: thiết kế chứng cứ.

## 19. Vì sao không tính latency bằng UTC received trừ UTC accepted ngay?

Hai event nằm trên hai máy có thể lệch đồng hồ và accepted không phải mốc receipt. Theo protocol cần kiểm offset; duration nội bộ Android chỉ dùng monotonic của cùng thiết bị và boot session. Thiếu evidence thì báo chưa đủ cơ sở.

Nguồn: [EVENT_SCHEMA](EVENT_SCHEMA.md), [SystemClock](https://developer.android.com/reference/android/os/SystemClock), [SEM-18](mechanisms/SERVER_FCM.md).

## 20. Timeout có được xóa khỏi thống kê hoặc gán latency 0 không?

Không. Run hợp lệ đã hết đủ cửa sổ phải giữ outcome quan sát được. Median chỉ tính mẫu hoàn tất và phải kèm n_complete/n_total; timeout, failure, NOT_RUN và run sai điều kiện được trình bày riêng theo protocol.

Nguồn: [EXPERIMENT_PROTOCOL](EXPERIMENT_PROTOCOL.md), [protocol SEM-16](../experiments/PROTOCOL.md). Chưa có thống kê nào được tạo trong SEM-19.

## 21. Bỏ gửi push trong E06 có chứng minh FCM làm mất tin không?

Không. Server chủ động không gửi; cần event skip có reason `FAULT_INJECTION_SKIP`. Nếu periodic cập nhật được, đó là quan sát phục hồi trong ca bỏ gửi có kiểm soát.

Nguồn: [EVENT_SCHEMA](EVENT_SCHEMA.md), [protocol E06](../experiments/PROTOCOL.md). Kiểm chứng sau: SEM-40/36/41.

## 22. Ít request hơn hoặc một lần chạy trên OPPO có đủ kết luận pin và mọi Android không?

Không. Request/DB write count là lượng công việc; năng lượng cần phép đo riêng. Kết quả OEM chỉ áp dụng trong cấu hình đã ghi, nhất là khi hồ sơ hiện chưa có OPPO thật để kiểm.

Nguồn: [PLAN](PLAN.md), [protocol SEM-16](../experiments/PROTOCOL.md), [DEVICES](environment/DEVICES.md). Phạm vi: giới hạn suy luận.

## 23. Build thành công hoặc task Done có chứng minh hai luồng end-to-end hoạt động không?

Không. Cần artifact, CHECKS và run tương ứng đúng commit/config. Một task môi trường có thể hoàn tất bằng việc ghi blocker; build/unit test cũng không thay bằng chứng callback, scheduler tự nhiên hoặc OEM.

Nguồn: [quy tắc bàn giao](../tasks/README.md), [SEM-12](evidence/SEM-12/CHECKS.md), [SEM-13](evidence/SEM-13/CHECKS.md), [SEM-17](evidence/SEM-17/CHECKS.md). Đáp án dựa trên loại evidence, không đánh giá lại nghiệm thu của owner.

## 24. Worker phải gọi /api/snapshot hay /api/bulletin?

Contract hiện hành là **GET /api/bulletin**. Path trong sơ đồ minh họa của tài liệu khác phải được chuẩn hóa theo API và client thật; không suy endpoint mới từ một blueprint. GET, version guard và commit cache vẫn là các mốc khác nhau.

Nguồn: [API](API.md), [remote datasource](../android/app/src/main/java/com/thanhtris/seminarie307/data/remote/SnapshotRemoteDataSource.kt), [đối chiếu I1](evidence/SEM-19/INPUT_REVIEW.md).

## 25. Thiếu run hoặc mode có được tự lấy run hiện hành hay mặc định PUSH không?

Không dùng fallback đó để tạo event thí nghiệm. Input không xác định được run/config hợp lệ phải từ chối và ghi diagnostic ngoài dataset. Nếu run xác định được nhưng mode không cho phép trigger, giữ receipt có thật và ghi trigger_rejected; không ghi enqueue như đã thành công.

Nguồn: [EVENT_SCHEMA](EVENT_SCHEMA.md), [SHARED_SYNC](mechanisms/SHARED_SYNC.md), [đối chiếu I2](evidence/SEM-19/INPUT_REVIEW.md). Source PUSH không có nghĩa mode luôn là PUSH; mode HYBRID cũng có push.

## Cách dùng khi chuẩn bị bài nói

Đã đối chiếu các câu 5-9 với SEM-15 và nguồn chính thức, ghi cách xử lý blueprint tại INPUT_REVIEW. Khi dùng ví dụ thực nghiệm trong bài nói, dẫn run/commit/config thật và gắn nhãn live/playback. Chưa có run thì giữ lời giải ở mức cơ chế/giả thuyết; không thêm số latency, tỷ lệ thành công hoặc câu “đã chứng minh” chỉ từ lời giải. Có thể chọn nhóm câu theo periodic (2-4), push (5-9, 24-25), lifecycle (10-13), tính đúng (14-18), đo lường/giới hạn (19-23).
