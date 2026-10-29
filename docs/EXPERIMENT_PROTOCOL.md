# Thiết kế kiểm thử — chưa có kết quả

Version phân công: 2026-10-29; giữ thông số thử từ kế hoạch 28/10. SEM-16/24/29/34/41/42/43/44/45 dùng tài liệu này theo đầu ra riêng để tạo run manifest, script và kết quả thật tại experiments/. Mọi expected dưới đây là điều cần kiểm tra, không phải số liệu đã đo.

## Cấu hình và cách tránh nhầm nguyên nhân

- Máy ảo Android có Google Play services; OPPO Find X9. Ghi API level, Android/ColorOS, build fingerprint đã loại định danh, SDK app, package, commit và pin/nguồn điện/mạng.
- Kiểm tra kết nối server và FCM riêng. Cáp USB/ADB reverse dùng cho truy cập server không tự chứng minh có Internet cho FCM.
- Baseline giữ cấu hình pin mặc định; nếu đổi tối ưu pin, ghi là một cấu hình riêng và hoàn tác sau thử.
- Mỗi run có run_id; reset lịch/background work từ mode trước, xác nhận worker cũ đã xong, đặt cache/server version ban đầu. Không re-register periodic ở từng tick để làm sai lịch.
- UI mở lại chỉ đọc Room; manual sync phải ghi trigger MANUAL và loại khỏi kết quả background.
- Xác nhận Doze bằng trạng thái hệ thống trước/sau; màn hình tắt chỉ là một điều kiện riêng. Dùng quy trình ADB từ tài liệu Android, có bước khôi phục nguồn điện/idle sau mỗi run.
- Không dùng lệnh force-run job hoặc test driver để suy ra thời điểm chạy tự nhiên; nếu dùng cho debug phải gắn nhãn INJECTED.
- Lưu log trên máy/thiết bị trong thời gian idle; tải lên sau run để giảm ảnh hưởng của telemetry.

## Tập ca cốt lõi và số lượt

| ID | Trigger / thiết bị | Cách tạo tình huống | Điều cần đối chiếu | Tối thiểu |
|---|---|---|---|---|
| E01 | Periodic, emulator + OPPO | Background, có mạng, giữ lịch đã đăng ký | Lịch tồn tại; có lần chạy tự nhiên; version/cache và trigger khớp | 1 phiên 90 phút/máy, mục tiêu ít nhất 3 lần chạy |
| E02 | Push, emulator + OPPO | Tắt periodic, background, thay snapshot và gửi data-only | Received và applied tách biệt; không cần mở app để bắt đầu sync | 5 lượt/máy, cửa sổ 120 giây/lượt |
| E03 | Periodic và push riêng, emulator | Xác nhận Doze, giữ 20 phút, sau đó thoát và quan sát thêm 10 phút | Sự kiện trước/trong/sau Doze, không suy ra luôn trễ từ một lần | 2 lượt/trigger |
| E04 | Hai trigger riêng, emulator | Mất mạng 2 phút, cập nhật server, sau đó nối lại | Pending/retry, cache cuối và lỗi; push TTL được ghi cố định | 3 lượt/trigger; 30 phút sau nối lại cho periodic, 5 phút cho push |
| E05 | Push + sync engine, emulator | Gửi tín hiệu trùng, phiên bản cũ và bản mới khi worker đang chạy | Version không giảm, không ghi trùng, không bỏ mất bản mới | 3 lượt/kịch bản + test logic |
| E06 | Hybrid, emulator | Cập nhật server nhưng cố ý không gửi push | Cập nhật đến từ periodic; đây là bỏ gửi có kiểm soát, không phải bằng chứng FCM làm mất tin | 2 lượt, 45 phút/lượt |

Pilot trước mỗi loại ca, không gộp pilot vào tập chính nếu đổi cấu hình sau đó. E01 thiếu số lần chạy sau 90 phút: giữ dữ liệu, ghi chưa đạt mục tiêu quan sát, kiểm tra nguyên nhân và lên lịch chạy thêm nếu còn thời gian; không force-run để bù mẫu.

Tập trên cần khoảng 10–12 giờ cửa sổ quan sát tuần tự, chưa tính setup/pilot. Có thể để chạy dài ngoài giờ làm việc nhưng không để các run cùng app làm nhiễu nhau. Tăng số lượt nếu còn thời gian; không tuyên bố độ tin cậy thống kê rộng từ mẫu nhỏ.

## Phiên bản dùng đo và lịch chạy

- 02–05/11: chạy thử để tìm lỗi; Vinh ghi run_phase=pilot/development. Trí bàn giao bản ứng viên vào cuối 05/11 sau tích hợp SEM-36, qua gate SEM-37, gồm commit app/server, APK checksum và cấu hình.
- 06–07/11: Vinh chạy tập chính với run_phase=main trên bản ứng viên. Đặt lịch ít nhất 10–12 giờ quan sát cùng thời gian setup/pilot; hai thiết bị có thể chạy song song khi run và cấu hình tách biệt.
- Run trước bản ứng viên chỉ dùng cho kết quả chính nếu SEM-44 kiểm độc lập và ghi code/config có liên quan không đổi, ghi rõ quyết định trong CHECKS. Mặc định giữ là pilot; không dùng để mô tả APK cuối.
- Nếu sửa scheduler, callback, sync core, retry, version guard hoặc logging sau khi đo: ghi bản mới và chạy lại ca chịu ảnh hưởng trước khi chốt SUMMARY. Thay đổi chỉ ở slide/tài liệu không bắt buộc chạy lại app.
- Không gộp các commit/build khác nhau vào cùng thống kê. Nếu chỉ so sánh hai phiên bản, tạo nhóm kết quả riêng và giải thích thay đổi.

## Ca đối chiếu bổ sung

Bắt buộc mô tả giới hạn process death/vuốt recent/force-stop trong bài. Nếu khả thi, mỗi trạng thái một ca mô tả trên OPPO với PUSH, ghi hành động chính xác và quan sát 5 phút; sau force-stop chỉ quan sát tiếp sau khi người dùng mở app, ghi rõ mốc mở lại. Không coi hybrid là cách vượt force-stop.

Battery Saver, reboot, TTL hết hạn và collapse key là mở rộng sau tập cốt lõi. Các ô chưa chạy mang trạng thái NOT_RUN. Không cần thử mọi tổ hợp trạng thái × mode × máy.

## Dữ liệu phải lưu

Mỗi run có manifest: case_id, run_id, run_phase, device_alias, cấu hình OS/app, mode, thời gian bắt đầu/kết thúc, cửa sổ quan sát, network/power/Doze, version trước/sau, TTL/collapse settings, app_commit, server_commit, apk_sha256, outcome và đường dẫn logs.

Sự kiện: server_updated, push_send_accepted/rejected, push_received, work_enqueued, work_started, snapshot_applied/unchanged, retry/failure. Dùng message_id từ FCM khi có; message_id chưa có thì null, không bịa. Work ID, request ID và trigger nối được về run.

Ghi UTC ở hai đầu và monotonic time ở Android. Đo clock offset với server trước/sau phiên; không báo end-to-end milliseconds chính xác nếu sai lệch đồng hồ chưa được kiểm soát. Duration nội bộ Android dùng monotonic time.

## Phân tích

- Tỷ lệ cập nhật trong cửa sổ = số run applied đúng version trong cửa sổ / tổng run hợp lệ cùng case/device/mode/build và cấu hình; dùng tập main, không trộn pilot.
- Run timeout không bị xóa hoặc gán latency bằng 0; trình bày riêng dưới dạng chưa quan sát được trong cửa sổ.
- Median và min–max chỉ trên run đã hoàn tất, luôn đi kèm n_complete/n_total và số timeout.
- Tách độ trễ nhận push, thời gian chờ worker và thời gian sync; không lấy FCM accepted làm thời điểm app nhận.
- Đếm GET, retry và DB writes nếu đã instrument; không quy đổi thành mAh.
- E01 là quan sát định kỳ tự nhiên; không so “ai nhanh hơn” với E02 nếu thời điểm server update so với lịch không được kiểm soát. Muốn so định lượng cần thêm trial có cùng vị trí update trong chu kỳ và khai báo trước.
- So OPPO và emulator theo từng cấu hình, không suy rộng mọi Android; trình bày giới hạn số lượt.

## File bàn giao

experiments/runs/<run_id>/manifest.json và events.jsonl; experiments/results.csv; experiments/SUMMARY.md; script tái lập trong experiments/scripts/. README của experiments ghi cách chạy và phiên bản.

Repo public chỉ nhận bản dữ liệu đã loại FCM token, service-account key, serial và thông tin cá nhân. Bản nguyên gốc nhạy cảm giữ trong experiments/private/ (gitignored). Không thay đổi giá trị đo khi loại định danh.

## Task một người dùng protocol

SEM-16 Vinh chuẩn bị protocol; SEM-24 Vinh exporter/manifest; SEM-29 Vinh pilot periodic; SEM-34 Vinh pilot push; SEM-41 Vinh main emulator; SEM-42 Vinh main OPPO; SEM-45 Tuấn parser/CSV; SEM-44 Trung kiểm độc lập; SEM-43 Vinh chốt SUMMARY. Không có task nhiều người cùng thực hiện.
