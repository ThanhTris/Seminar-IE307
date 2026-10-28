# Dàn ý thuyết trình 15 phút — Chủ đề 12

Đây là kế hoạch nội dung, chưa phải bộ slide hoàn chỉnh hoặc kết quả demo. Mục tiêu: người nghe hiểu trigger → hệ điều hành → worker → dữ liệu, rồi thấy bằng chứng và giới hạn.

## Phân bổ chính xác 15 phút

| Mốc | Thời lượng | Nội dung / slide | Thông điệp và bằng chứng |
|---|---:|---|---|
| 00:00–00:45 | 0:45 | 1. Bài toán bảng tin | Khi app không mở, làm sao dữ liệu mới đến cache? |
| 00:45–02:00 | 1:15 | 2. Hai cách kích hoạt | Định kỳ chủ động hỏi server; push báo cần kiểm tra dữ liệu |
| 02:00–04:00 | 2:00 | 3. Cơ chế fetch nền | Scheduler, constraints, worker; một timeline thực của periodic |
| 04:00–06:00 | 2:00 | 4. Cơ chế silent push | Server/FCM/callback/work; phân biệt notification và data-only v1 |
| 06:00–07:00 | 1:00 | 5. Kiến trúc demo | Cùng sync engine, version guard và ba mode; một sơ đồ |
| 07:00–11:00 | 4:00 | 6. Demo | Push live + periodic/Doze từ log hoặc video có nhãn |
| 11:00–12:45 | 1:45 | 7. Kết quả thực nghiệm | Tỷ lệ trong cửa sổ, độ trễ, ca không quan sát được và OPPO/emulator |
| 12:45–14:00 | 1:15 | 8. Lập luận và lựa chọn | Hai nghiên cứu hỗ trợ giả thuyết; kết quả nào phù hợp/khác và vì sao |
| 14:00–15:00 | 1:00 | 9. Kết luận | Dùng khi nào, hạn chế nào, cách phục hồi; nguồn và repo ở chân slide |

Nếu giảng viên tính cả hỏi đáp trong 15 phút: dùng biến thể 13 phút trình bày + 2 phút hỏi đáp; rút mỗi phần cơ chế 30 giây, demo 30 giây và kết quả 30 giây. Phương án chính hiện là 15 phút trình bày gồm demo theo xác nhận của người dùng.

## Phân vai trình bày đề xuất

| Phần theo lịch phía trên | Người trình bày |
|---|---|
| Mở bài 00:00–00:45 | Trí |
| Hai cách kích hoạt 00:45–02:00 | Trung |
| Periodic 02:00–04:00 | Trung |
| Silent push 04:00–06:00 | Trang |
| Kiến trúc 06:00–07:00 | Tâm |
| Demo 07:00–11:00 | Trang dẫn toàn bộ; Trí thao tác thiết bị và mở log/video dự phòng |
| Kết quả 11:00–12:45 | Vinh |
| Đối chiếu nghiên cứu 12:45–14:00 | Tuấn |
| Kết luận 14:00–15:00 | Tuấn |

Gộp thành 7 lượt nói liên tục: Trí → Trung → Trang → Tâm → Trang (demo) → Vinh → Tuấn. Chỉ có 6 lần chuyển người; dành 5 giây mỗi lần ngay trong khung thời gian đã chia, tổng 30 giây chuyển tiếp và tối đa 14 phút 30 giây nội dung. Trang dẫn cả periodic/Doze trong demo để không đổi người giữa thao tác. Không thêm thời gian giới thiệu thành viên. Đây là phân vai nói, không thay phân công triển khai trong [TEAM_ASSIGNMENTS](TEAM_ASSIGNMENTS.md).

## Kịch bản demo 4 phút

1. 0:00–0:30: cho thấy mode PUSH, cache version N; đưa app về background. Màn hình timeline của server và log đã lọc device/run sẵn.
2. 0:30–1:30: tạo version N+1 và gửi normal-priority data-only; chỉ ra accepted → received → work_started → snapshot_applied. Mở lại app chỉ đọc cache để xác nhận.
3. 1:30–2:30: mở timeline/video **đã ghi trước** của periodic tự nhiên; chỉ ra schedule khác start, không bấm chạy worker rồi gọi đó là periodic.
4. 2:30–3:30: dùng clip/log **đã ghi trước** của Doze hoặc bỏ gửi push và hybrid phục hồi; liên hệ trạng thái hệ điều hành với kết quả.
5. 3:30–4:00: kết nối lại câu hỏi ban đầu: ai kích hoạt, ai quyết định chạy, lúc nào dữ liệu thật sự đổi.

Ngưỡng đổi sang video: live chưa hoàn tất trong 30 giây kể từ lúc gửi. Nói rõ “chưa cập nhật trong cửa sổ live”, chuyển bản ghi của run có metadata; không gọi đây là bảo đảm push phải tới trong 30 giây. Các file dự phòng phải lấy từ bản build thật đã kiểm chứng.

## Những điều phải nhìn thấy trong evidence

- Version trước/sau; mode; device alias; run_id; UTC thời điểm và event type.
- Có snapshot_applied trước khi UI mở lại; không có foreground auto-refresh trong ca này.
- Ghi rõ live hay phát lại, thiết bị nào, điều kiện nào.
- Không lộ token, service-account key hoặc định danh thiết bị cá nhân.

## Câu hỏi người thuyết trình phải trả lời

- Đặt chu kỳ 15 phút có bảo đảm chạy đúng từng mốc không?
- Silent push khác một thông báo bị tắt tiếng ở chỗ nào?
- Vì sao FCM đã trả về message ID mà cache vẫn cũ?
- Callback nhận push có thể làm việc dài tùy ý không?
- Đóng app, vuốt recent và force-stop có cùng ý nghĩa không?
- Nếu tín hiệu trùng hoặc version cũ đến muộn thì xử lý thế nào?
- Hybrid có vượt qua Doze/force-stop không, hay chỉ thêm cơ hội cập nhật khi được phép?
- Kết quả trên OPPO có đủ đại diện cho Android nói chung không?
- Số request giảm có chứng minh pin giảm không?
- Demo đang dùng nhánh API FCM nào, vì sao không dùng EAP?

## Bộ tài liệu cuối

SEM-09 bàn giao slide chỉnh sửa được, PDF slide, speaker notes và báo cáo ngắn. SEM-10 bàn giao demo runbook, APK, server và video. Phụ lục dành cho sơ đồ chi tiết, metadata, payload đã loại token và tài liệu API mới; không nhồi vào 15 phút.
