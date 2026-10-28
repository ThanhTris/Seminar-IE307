# SEM-08 — Chạy tập ca cốt lõi và phân tích số đo

- Status: backlog
- Lịch mục tiêu: Chuẩn bị từ 28/10; chạy 02–07/11/2026
- Công sức: 10/100 — Thực hành
- Owner: Vinh
- Reviewer: Trang
- Phối hợp: Trung, Tuấn
- Điều kiện bắt đầu: có thể chuẩn bị từ kế hoạch đã chốt
- Điều kiện hoàn tất bổ sung: SEM-05, SEM-06, SEM-07 đã bàn giao

## Đầu vào

docs/EXPERIMENT_PROTOCOL.md. E01 chờ SEM-05; E02 chờ SEM-06; E03/E04 chạy từng trigger khi sẵn sàng; E05/E06 chờ SEM-07.

## Việc cần làm

Phân việc: Vinh điều phối thiết bị, chạy E01–E06, quản lý manifest/log và SUMMARY; Tuấn làm script tổng hợp CSV, bảng/biểu đồ và kiểm số mẫu/timeout; Trung hỗ trợ reset scheduler, xác nhận log periodic. Người viết trigger sửa lỗi thuộc module của mình trước khi Vinh chạy lại.

Theo [phân công 6 người](../../docs/TEAM_ASSIGNMENTS.md); owner tổng hợp đầu ra và CHECKS, reviewer kiểm trước khi chuyển done.

1. Tạo script/manifest theo protocol và test pilot; giữ cấu hình cố định cho tập chính.
   Giai đoạn 02–05/11 dùng cho phát hiện lỗi/pilot. Tập chính chạy 06–07/11 trên bản ứng viên SEM-07 bàn giao; số liệu cũ chỉ được giữ trong tập chính nếu reviewer xác nhận phần code/config liên quan không thay đổi, nếu không phải chạy lại.
2. Thực hiện E01–E06 với số lượt/cửa sổ quy định, ghi cả run lỗi/timeout và tình trạng NOT_RUN.
3. Đối chiếu trên OPPO cho E01/E02; mô tả khác biệt thiết bị mà không suy rộng.
4. Tổng hợp kết quả từ JSONL sang CSV, kiểm tra clock offset và nguồn trigger; tính số request/ghi DB khi có instrument.
5. Lập bảng giả thuyết → quan sát → giải thích → giới hạn, nêu ca bị nhiễu và lý do loại.

## Đầu ra bắt buộc

- experiments/scripts/ — cách reset, chạy, xuất log và tổng hợp dữ liệu.
- experiments/runs/<run_id>/manifest.json và events.jsonl — dữ liệu đã loại định danh nhạy cảm.
- experiments/results.csv — run-level outcome, timings, counts và timeout.
- experiments/SUMMARY.md — kết quả từng case/device/mode, số mẫu, giới hạn và link evidence.
- docs/evidence/SEM-08/CHECKS.md — commit, môi trường, bước kiểm tra, expected/actual, link bằng chứng, hạn chế và phần bàn giao.

## Tiêu chí nghiệm thu

- [ ] Số lượt đạt protocol hoặc ghi rõ phần chưa đạt; không xóa timeout khỏi mẫu số.
- [ ] Tái tính được bảng từ log; median đi kèm n_complete/n_total.
- [ ] Mỗi bảng ghi build/commit app và server, thiết bị, mode và cấu hình; không gộp số liệu khác phiên bản làm kết quả của APK cuối. Thay đổi code có ảnh hưởng phải chạy lại ca tương ứng.
- [ ] Không so độ trễ periodic/push như thử nghiệm kiểm soát nếu vị trí update trong chu kỳ khác nhau.
- [ ] Không suy kết luận pin từ số request; lưu cả kết quả trái giả thuyết.
- [ ] Có đủ đầu ra và CHECKS.md; người làm giải thích được kết quả, reviewer được phân công kiểm tra và ghi kết luận.

## Trạng thái bàn giao

Chưa thực hiện. Tên file ở trên là đầu ra phải tạo khi làm task, không phải bằng chứng đã tồn tại. Cập nhật task và task board cùng lúc khi đổi trạng thái.
