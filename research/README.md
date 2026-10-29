# Nguồn nghiên cứu và đối chiếu

Nguồn kỹ thuật được đối chiếu ngày **28/10/2026**; phân công cập nhật **29/10/2026**. Nguồn dưới đây là documentation chính thức; **chưa có bài báo học thuật được tuyển chọn hoặc PDF tải về**. [SEM-20](../tasks/backlog/SEM-20.md) do Tuấn đọc bài thứ nhất; [SEM-21](../tasks/backlog/SEM-21.md) do Tâm đọc bài thứ hai; [SEM-22](../tasks/backlog/SEM-22.md) do Trang đối chiếu với API. Mỗi task chỉ một người thực hiện.

## Nguồn kỹ thuật

| ID | Nguồn | Nội dung dùng trong seminar |
|---|---|---|
| D01 | [Work requests](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work) | Periodic tối thiểu 15 phút; thời điểm thực tế phụ thuộc constraints và tối ưu hệ thống. Không cam kết chạy chính xác mỗi 15 phút. |
| D02 | [Doze và App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby) | Điều kiện Doze, giới hạn nền và quy trình thử bằng ADB; phải xác nhận trạng thái thực tế. |
| D03 | [Receive messages Android](https://firebase.google.com/docs/cloud-messaging/android/receive-messages) | Với AndroidConfig v1, data-only đi qua onMessageReceived; notification/mixed có đường xử lý khác khi app background. Callback có thời gian ngắn; công việc dài cần bàn giao phù hợp. |
| D04 | [FCM priority](https://firebase.google.com/docs/cloud-messaging/android-message-priority) | Baseline normal cho đồng bộ không khẩn cấp. High priority phục vụ nội dung người dùng nhìn thấy, không phải lối bảo đảm silent sync tức thì. |
| D05 | [AndroidConfigV2 migration](https://firebase.google.com/docs/cloud-messaging/send/v2-api) | Tài liệu có BackgroundSync và callback mới, hướng cài EAP. Demo chọn v1 stable, ghi rõ phạm vi API và không trộn ví dụ. |
| D06 | [Message lifespan](https://firebase.google.com/docs/cloud-messaging/customize-messages/setting-message-lifespan) | Tra cứu TTL khi chốt payload và thiết kế thử mất mạng; lưu cấu hình theo run. |
| D07 | [Collapsible messages](https://firebase.google.com/docs/cloud-messaging/customize-messages/collapsible-message-types) | Tra cứu collapse key nếu triển khai gom tín hiệu; tách khỏi logic idempotency của app. |
| D08 | [FCM Android setup](https://firebase.google.com/docs/cloud-messaging/android/get-started) | Chốt cấu hình Firebase/client, thiết bị hỗ trợ và token trước test end-to-end. |

D01–D05 đã đối chiếu phần nội dung liên quan; D06–D08 là nguồn setup/tra cứu khi triển khai. Tài liệu thay đổi theo thời gian: ghi version SDK trong evidence và ngày truy cập trong báo cáo. Không kết luận SDK “mới nhất” khi chưa kiểm tra build.

## Tuyển chọn bài báo

Chọn 2 bài có bản gốc/DOI xác minh được, ưu tiên:
- Một nghiên cứu về trade-off độ mới dữ liệu, polling/push hoặc lưu lượng/năng lượng trên mobile.
- Một nghiên cứu về background scheduling, trì hoãn hoặc giới hạn hệ điều hành.

Mỗi ghi chú research/notes/<paper-id>.md gồm metadata, câu hỏi, phương pháp, thiết bị/OS, kết quả, hạn chế, điều có thể áp dụng và case_id liên quan. Không suy kết quả của nghiên cứu sang OPPO nếu chưa đo. Bài ít liên quan không được giữ chỉ để đủ số lượng.

Mỗi người lưu metadata riêng trong research/metadata/paper-1.bib hoặc paper-2.bib, không cùng sửa bibliography tổng hợp. SEM-50 do Tuấn ghép research/references.bib và docs/CLAIMS.md sau khi nhận đủ input. PDF chỉ đưa vào research/papers/ khi quyền chia sẻ cho phép; nếu không, giữ link và ghi chú. Bài thứ 3–4 là tùy chọn sau demo cốt lõi.

## Bảng claim cần phát triển

| Claim cần kiểm chứng | Nguồn ban đầu | Ca thử | Trạng thái |
|---|---|---|---|
| Periodic scheduling không phải lịch chạy chính xác | D01 | E01/E03 | Giả thuyết và ràng buộc tài liệu; chưa đo |
| Nhận push khác hoàn tất đồng bộ | D03/D04 | E02/E04 | Chưa đo |
| Trì hoãn phụ thuộc trạng thái hệ thống | D02/D04 | E03 | Chưa đo |
| Trùng tín hiệu không được làm sai dữ liệu | Quy tắc thiết kế của demo | E05 | Chưa triển khai |
| Periodic bổ sung cơ hội cập nhật khi không gửi push | Giả thuyết thiết kế hybrid | E06 | Chưa đo |

Bảng cuối phải thêm đường dẫn run thực, kết luận và giới hạn. Claim có nguồn không tự biến thành kết quả thực nghiệm.
