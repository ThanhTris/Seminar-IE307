# Lịch độc quyền thực nghiệm — SEM-16

Phiên bản **1.0.0**, lập **03/11/2026**, toàn bộ giờ **UTC+7**, Vinh (`Vinh5905`) thực hiện. Theo [protocol thao tác](PROTOCOL.md), [protocol gốc](../docs/EXPERIMENT_PROTOCOL.md), [PLAN](../docs/PLAN.md) và [deadline task](../tasks/DEADLINES.md).

**Đây là lịch dự trù, chưa phải xác nhận đã chạy/đặt được máy.** Ngày 03/11 Vinh xác nhận không có OPPO; các slot OPPO là chỗ giữ có điều kiện, **NOT_RUN — chưa có thiết bị/người giữ/lịch mượn**. Không đổi SEM-42 thành emulator và không ghi lịch 02/11 đã thực hiện. Trạng thái Project trong task là snapshot cũ; gate thực phải kiểm artifact/CHECKS trước chạy.

## 1. Quyền sử dụng và điều kiện chuyển slot

- Mỗi slot khóa `(device_alias, com.thanhtris.seminarie307)` cho đúng **một run**; setup, quan sát, export và cleanup nằm trong khóa. Không chạy periodic và push của hai run trên cùng app, không để pilot/demo/MANUAL chen vào main.
- Mặc định khóa thêm **server snapshot/store hiện hành** cho slot đó vì backend là một snapshot dùng chung. Không update bằng CLI khác hoặc gửi token cho run khác. Lịch này chạy emulator/OPPO tuần tự nên không cần giả định server đã hỗ trợ tenant riêng.
- Chỉ chạy hai máy song song khi có server/store/port độc lập, run/config/token routing tách biệt được kiểm chứng và đủ người giám sát; phải ghi lịch phiên bản mới. Hai run ID khác nhau trên cùng singleton snapshot chưa tạo cô lập.
- Hết slot không có nghĩa được cắt cửa sổ: nếu setup chưa xong hoặc worker chưa drain thì dùng buffer, dịch slot sau và ghi giờ thật. Khi tràn deadline, báo blocker/ca NOT_RUN và xin điều chỉnh phạm vi/lịch; không lặng giảm số lượt hoặc lấy pilot bù main.
- Các run bổ sung dùng ID mới, giữ nguyên run lỗi/timeout. Main chỉ dùng candidate SEM-37 sau gate cuối 05/11; chưa có candidate thì không đổi nhãn pilot thành main.

## 2. Ngân sách quan sát tối thiểu

| Ca / thiết bị | Số run main | Cách tính phút quan sát | Phút |
|---|---:|---|---:|
| E01 / emulator + OPPO | 2 | 2 × 90; mục tiêu ≥3 cycle tự nhiên/phiên | 180 |
| E02 / emulator + OPPO | 10 | 2 máy × 5 × 120 giây | 20 |
| E03 / emulator, PERIODIC + PUSH | 4 | 2 trigger × 2 × (5 baseline + 20 idle + 10 sau thoát) | 140 |
| E04 / emulator, PERIODIC | 3 | 3 × (2 offline + 30 sau nối lại) | 96 |
| E04 / emulator, PUSH | 3 | 3 × (2 offline + 5 sau nối lại) | 21 |
| E05 / emulator, 3 kịch bản | 9 | 3 × 3 × 15; window bổ sung của SEM-16 | 135 |
| E06 / emulator, HYBRID | 2 | 2 × 45 | 90 |
| **Tổng dự trù cốt lõi** | **33** | **682 phút = 11 giờ 22 phút** | **682** |

Emulator: **27 run, 582 phút = 9 giờ 42 phút**. OPPO: **6 run, 100 phút = 1 giờ 40 phút**, chưa khả dụng. Bỏ 20 phút baseline bổ sung E03 thì các cửa sổ còn lại vẫn **662 phút = 11 giờ 2 phút**. Không gọi 582 phút emulator là đã hoàn tất toàn bộ hai máy. E05 test logic, pilot, setup/drain/export, ca lifecycle mô tả và các run thay thế tính ngoài 682 phút.

## 3. Pilot/development — 02–05/11/2026

Giữ giai đoạn nguồn 02–05/11; tại lúc soạn 03/11 chưa có run nào được SEM-16 xác nhận. Các giờ dưới đây là dự trù/catch-up, không thay deadline gốc SEM-29 ngày 02/11. Mọi slot phụ thuộc module/exporter/thiết bị thật.

| Ngày / giờ dự trù | Thiết bị + server khóa | Nội dung, gate và tình trạng |
|---|---|---|
| 02/11 (mốc kế hoạch gốc) | Chưa xác nhận | SEM-29 pilot periodic; không ghi lùi lịch đã chạy. Nếu không có evidence, giữ NOT_RUN/quá hạn và ghi catch-up |
| 03/11 08:00–10:00 | emulator-main | SEM-24 exporter/manifest và kết nối baseline; chỉ chuẩn bị khi nhận SEM-12/26. Chưa xác nhận hoàn tất |
| 03/11 10:00–12:00 | emulator-main | SEM-29 catch-up E01: giữ phiên 90 phút, mục tiêu pilot ≥2 cycle, không force-run; cần SEM-16/24/30 và SEM-31 để hoàn tất |
| 03/11 13:00–14:00 | emulator-main | SEM-34 E02: 5 × 120 giây + reset/export; cần SEM-16/24/32/35, SEM-33 để hoàn tất; giữ hạn task 22:00 |
| 03/11 14:00–16:30 | oppo-find-x9, có điều kiện | Pilot E01 90 phút và E02 5 × 120 giây + setup; hiện NOT_RUN do chưa có OPPO; không coi đã hẹn mượn |
| 04/11 08:00–11:00 | emulator-main | Pilot E03: 2 trigger riêng, 2 × 35 phút/trigger + setup/cleanup; cần xác nhận Doze và hoàn tác |
| 04/11 13:00–15:30 | emulator-main | Pilot E04: 3 × 32 và 3 × 7 phút + setup; TTL cố định, khôi phục đúng transport |
| 04/11 15:30–18:30 | emulator-main | Pilot E05: 9 × 15 phút + barrier/reset; nhận test logic SEM-38/39 khi có, thiếu thì ghi blocker |
| 05/11 08:00–10:00 | emulator-main | Pilot E06/hybrid: 2 × 45 phút + cleanup; cần SEM-36/40, không dùng debug force-run |
| 05/11 10:00–17:00 | emulator-main; OPPO chỉ khi có máy và slot riêng | Buffer sửa lỗi/rerun, kiểm run isolation và export; không chạy song song trên cùng store |
| 05/11 17:00–22:00 | Giữ môi trường cho tích hợp/candidate | Bàn giao lỗi/commit/config cho SEM-36/37; candidate SEM-37 hạn 22:00. Không giả định candidate đã có để đặt run main sớm |

Nếu module bàn giao trễ, giữ phần chưa chạy là NOT_RUN và ghi thời điểm catch-up thực. Pilot trước **mỗi loại ca** phải đủ kiểm thao tác/logging/reset; nếu chưa có pilot E03–E06 thì chưa đủ điều kiện main các ca đó. Không đổi code trong lúc đang giữ slot đo của người khác.

## 4. Main emulator — 06/11/2026 (SEM-41)

Toàn bộ slot ngày này khóa **emulator-main + app + snapshot store**. Điều kiện: candidate SEM-37, exporter SEM-24 và protocol đã nhận; pilot ca tương ứng đã kiểm. Mọi hàng hiện **NOT_RUN — lịch dự trù**.

| Giờ UTC+7 | Ca / số lượt | Phút quan sát giữ nguyên | Phút slot / phần còn lại |
|---|---|---:|---|
| 07:30–08:00 | Setup candidate, APK checksum, baseline, clock | 0 | 30 setup |
| 08:00–09:40 | E01 PERIODIC, 1 phiên | 90 | 100 / 10 reset/export |
| 09:40–10:00 | E02 PUSH, 5 lượt | 10 | 20 / 10 reset/export |
| 10:00–11:20 | E03 PERIODIC, 2 lượt | 70 | 80 / 10 setup/cleanup |
| 11:20–12:40 | E03 PUSH, 2 lượt | 70 | 80 / 10 setup/cleanup |
| 12:40–13:00 | Nghỉ sau cleanup, giữ máy/server không có run active | 0 | 20 |
| 13:00–14:50 | E04 PERIODIC, 3 lượt | 96 | 110 / 14 reset/export |
| 14:50–15:25 | E04 PUSH, 3 lượt | 21 | 35 / 14 reset/export |
| 15:25–17:55 | E05 A/B/C, 3 lượt/kịch bản | 135 | 150 / 15 setup race/reset |
| 17:55–19:35 | E06 HYBRID, 2 lượt | 90 | 100 / 10 reset/export |
| 19:35–21:35 | Buffer setup kéo dài/ca lỗi/thiếu cycle | 0 định mức | 120 dự phòng; run thêm ghi riêng |
| 21:35–22:00 | Export/clock/cleanup, kiểm manifest và bản sao private | 0 | 25 bàn giao tạm |

Trong mỗi block, chia từng lượt tuần tự đủ window tại PROTOCOL, thêm reset/drain trước lượt tiếp. Ví dụ E04 PERIODIC giữ **32 phút/lượt**, không chia slot 110 phút thành ba cửa sổ ngắn hơn. Slot dư là ước lượng; buffer nhận phần setup vượt dự kiến, không bảo đảm mọi run đều complete đúng giờ.

## 5. Main OPPO và dự phòng — 07/11/2026

Các slot OPPO **chưa được đặt thực tế**, phụ thuộc có máy và hoàn tất hồ sơ/pilot/candidate. Theo baseline cùng build/config tương ứng; không suy emulator là control tương đương phần cứng. Store được khóa tuần tự, kể cả lúc đổi máy.

| Giờ UTC+7 | Thiết bị / nội dung | Window / mục đích | Trạng thái hiện tại |
|---|---|---|---|
| 07:30–08:00 | OPPO: setup/clock/baseline | 30 phút setup; cần biết model/OS/ColorOS thật | NOT_RUN — chưa có máy |
| 08:00–09:40 | OPPO E01, 1 phiên | 90 phút + 10 cleanup | NOT_RUN — chưa có máy |
| 09:40–10:00 | OPPO E02, 5 lượt | 10 phút + 10 reset/export | NOT_RUN — chưa có máy |
| 10:00–10:30 | OPPO lifecycle bổ sung nếu khả thi | Process death 5, recent-swipe 5, sau force-stop/mở lại 5; còn 15 phút thao tác | NOT_RUN — chưa có máy; ngoài 682 phút |
| 10:30–12:30 | Emulator: dự phòng run thay thế | Chọn ca còn thiếu theo window gốc; không cố nhét cả tập E03/E04 nếu không đủ giờ | NOT_RUN — chỉ dùng khi cần |
| 12:30–13:00 | Emulator: khóa dữ liệu bàn giao SEM-41 | Export, kiểm log/manifest/cleanup; SEM-41 hạn 13:00 | NOT_RUN |
| 13:00–14:30 | OPPO: buffer ca cần đo lại | Đủ một phiên E01 90 phút chỉ khi setup đã xong; nếu cần thêm setup thì báo trễ | NOT_RUN — chưa có máy |
| 14:30–15:00 | OPPO: export/cleanup/giới hạn OEM | SEM-42 hạn 15:00; thiếu máy ghi blocker, không tạo số liệu thay thế | NOT_RUN — chưa có máy |

Sau bàn giao dữ liệu: SEM-45 parser/CSV hạn 17:00 → SEM-44 kiểm độc lập hạn 19:00 → SEM-43 SUMMARY hạn 22:00. Đây là mốc nhận đầu ra theo [task board](../tasks/README.md), không xác nhận các task đã chạy hoặc tự giao thêm người vào SEM-16.

Nếu đến 05/11 vẫn không có OPPO, giữ bản ghi blocker cho SEM-42 và báo giới hạn cho SEM-43/44/45; phần emulator tiếp tục khi đủ gate. Không tự xóa yêu cầu OPPO, không hứa đã hoàn tất bộ cốt lõi. Nếu candidate chưa bàn giao 05/11 22:00 hoặc pilot chưa qua, lịch main phải điều chỉnh có ghi nhận; không lùi timestamp hay đổi nhãn dữ liệu.

## 6. Quy tắc bàn giao lịch thực

Người chạy ghi giờ bắt đầu/kết thúc thật, run IDs, artifact/build/config, sai lệch so với slot và cleanup trong CHECKS của task thực nghiệm; không đánh dấu slot đã chạy chỉ từ đồng hồ hoặc từ kế hoạch. Khi đổi lịch, giữ ngày sửa và lý do, không thay định mức gốc. [CHECKS SEM-16](../docs/evidence/SEM-16/CHECKS.md) chỉ kiểm tính đầy đủ/khả thi của thiết kế và phép cộng lịch; không chứng nhận kết quả runtime.
