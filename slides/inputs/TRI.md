# WIP — SEM-46 chưa hoàn thành, chưa đủ điều kiện merge

Ngày 09/11/2026. Tuấn (`mtuan2491`) soạn phần làm trước trên nhánh `codex/SEM-46-opening-demo`. Người trình bày mở bài và thao tác thiết bị là Trí theo PRESENTATION_PLAN. Tên file TRI.md giữ đúng đầu ra của task.

**Đang chờ SEM-37 bàn giao candidate, gate và CHECKS để chốt thao tác trên build thật.** Bản hiện tại dùng cho review nội dung. Nghiệm thu SEM-46 và ghép bản cuối vào deck còn chờ bước 3. [Yêu cầu SEM-46](../../tasks/backlog/SEM-46.md)

## 1. Mở bài dự kiến trong 45 giây

| Mốc toàn bài | Nội dung | Người phụ trách |
|---|---|---|
| 00:00–00:40 | Đặt câu hỏi trigger-to-cache | Trí nói |
| 00:40–00:45 | Chuyển sang phần hai trigger | Trí bàn giao Trung |

Lời dẫn dự thảo

> Khi ứng dụng bảng tin đang ở nền, tin mới trên server sẽ đến bộ nhớ đệm của điện thoại bằng cách nào? Nhóm xem xét hai cách kích hoạt đồng bộ. Một cách là kiểm tra định kỳ, cách còn lại là server gửi tín hiệu yêu cầu kiểm tra. Cả hai đi qua worker và cập nhật cùng cache. Trong phần demo, chúng ta sẽ theo dõi từ lúc có tín hiệu đến lúc dữ liệu được áp dụng. Các mốc thời gian và version giúp giải thích hành vi trên từng thiết bị.

Câu chuyển người

> Trung sẽ trình bày hai cách kích hoạt và vai trò của bộ lập lịch Android.

Thời lượng trên là ngân sách biên tập. Bấm giờ lời nói thực tế thuộc lần diễn tập sau khi ghép deck. Lượt mở bài giữ 5 giây chuyển người trong khung 45 giây. [PRESENTATION_PLAN](../../docs/PRESENTATION_PLAN.md)

## 2. Nội dung hình chiếu mở đầu

- Tiêu đề slide dùng câu hỏi “Khi app ở nền, dữ liệu mới đến cache lúc nào?”.
- Hình chính là chuỗi server → trigger → Android/worker → Room cache → UI đọc cache.
- Chân slide ghi case, device alias, run ID và nhãn LIVE hoặc PLAYBACK khi chuyển tới bằng chứng demo.

Hình dùng chung sơ đồ đã nhận trong SHARED_SYNC để giữ cách gọi component nhất quán. Bản deck cuối thuộc SEM-51. [Shared sync flow](../../docs/mechanisms/SHARED_SYNC.md)

## 3. Các mốc cần phân biệt khi dẫn demo

| Mốc | Câu diễn đạt dùng trong bài |
|---|---|
| `server_updated` | “Server đã lưu snapshot version mới.” |
| `push_send_accepted` | “FCM đã trả về kết quả chấp nhận yêu cầu gửi.” |
| `push_received` | “Callback trên Android đã ghi nhận tín hiệu.” |
| `work_enqueued` | “Yêu cầu work đã được hệ thống chấp nhận xếp lịch.” |
| `work_started` | “Worker đã bắt đầu thực hiện.” |
| `snapshot_applied` | “Snapshot version này đã commit vào Room.” |
| UI mở lại | “Màn hình đang hiển thị version đã lưu trong cache.” |

Mode PERIODIC dùng trigger định kỳ, PUSH dùng tín hiệu data-only normal priority, HYBRID nhận cả hai. Source MANUAL được ghi riêng khi chuẩn bị hoặc chẩn đoán. Cơ chế ứng dụng phải kiểm version hiện hành khi áp dụng snapshot. Những câu dẫn ở đây diễn giải contract và chỉ dùng thì quá khứ khi có event thật tương ứng trên màn hình. [SHARED_SYNC](../../docs/mechanisms/SHARED_SYNC.md), [EVENT_SCHEMA](../../docs/EVENT_SCHEMA.md)

## 4. Nguồn và phần đang chờ

| Nguồn | Đã nhận / cần bổ sung |
|---|---|
| SEM-14 | Đã nhận shared flow và CHECKS, đủ để soạn phần cơ chế |
| Scope và kế hoạch nói | Đã nhận phạm vi bảng tin, khung 15 phút và demo 4 phút |
| SEM-37 | Cần candidate manifest, candidate gate và CHECKS để pin build/config và xác nhận thao tác |

Đầu vào candidate đang chờ được theo dõi trong CHECKS của task. [CHECKS SEM-46](../../docs/evidence/SEM-46/CHECKS.md)

## 5. Phiếu gắn candidate trước khi chốt kịch bản

| Thông tin cần pin | Trạng thái hiện tại | Nguồn cần nhận |
|---|---|---|
| App/server commit, APK SHA-256 và package/version | CHỜ SEM-37 | Candidate manifest |
| Alias thiết bị, OS/API, mạng và quyền cần cấp | CHỜ SEM-37 | Candidate config và CHECKS |
| Cách chọn mode/run, hủy lịch và drain work | CHỜ SEM-37 | Giao diện/công cụ thực tế trên candidate đã kiểm |
| Entry point update/send và cấu hình gửi local | CHỜ SEM-37 | Lệnh/cấu hình đã bàn giao cho candidate |
| Run live và version baseline/target | Điền ở lần chuẩn bị demo | Manifest của run được chọn |
| Log/clip phát lại, run/device/build và mốc bắt đầu | Điền khi chọn bằng chứng thật | Manifest/log và chỉ mục playback |

Người soạn dùng phiếu này để chốt các thao tác sau khi nhận candidate. Những nhãn nút, lệnh mode/reset và đường dẫn release sẽ được điền từ giao diện hoặc công cụ đã kiểm trên build đó.

## 6. Trình tự chuẩn bị thao tác

Các bước dưới là dự thảo để nhận xét trước khi có candidate. Trạng thái thực hiện thiết bị hiện là **Not run**.

1. Đối chiếu candidate manifest/gate/CHECKS, ghi build/hash/alias/config vào phiếu trên. Mở sẵn log đã lọc đúng run và che thông tin local trước khi chia sẻ màn hình.
2. Chọn run mới, đóng trigger của run trước, hủy lịch và drain work qua cơ chế được candidate bàn giao. Ghi work cũ còn active hoặc việc drain chưa xác nhận vào phiếu blocker trước khi tiếp tục chuẩn bị.
3. Chuẩn bị cache version N bằng thao tác MANUAL có nhãn ở ngoài cửa sổ live, chờ work hoàn tất. Đọc lại version server/cache và ghi baseline. Giữ server version tăng đơn điệu giữa các lượt.
4. Chọn mode PUSH và run ID đúng, xác nhận periodic đã hủy, chụp cấu hình và đưa app về Home. Mở sẵn bằng chứng trạng thái background và mốc bắt đầu quan sát.
5. Chuẩn bị update N+1 và tín hiệu data-only normal priority qua entry point được bàn giao. Token và credential giữ trong cấu hình local. Trang dẫn nội dung, Trí thực hiện thao tác và ghi mốc gửi.
6. Chuẩn bị trang playback của periodic và Doze/hybrid theo run thật có metadata. Chốt đoạn trích phù hợp khung 1 phút cho mỗi phần, ghi nhãn LIVE hoặc PLAYBACK ngay trên màn hình.

Mode/source, run isolation, drain và version guard được đối chiếu theo SHARED_SYNC. Cách reset/cửa sổ/cleanup chi tiết dùng protocol. [SHARED_SYNC](../../docs/mechanisms/SHARED_SYNC.md), [PROTOCOL](../../experiments/PROTOCOL.md)

## 7. Kịch bản phối hợp trong demo 4 phút

Trang giữ lời dẫn suốt phần demo. Trí thao tác thiết bị, log và playback theo tín hiệu của Trang. Các câu dưới thuộc phối hợp thao tác, để ghép với lời dẫn demo của SEM-47 khi nhận bàn giao. [PRESENTATION_PLAN](../../docs/PRESENTATION_PLAN.md)

| Mốc trong demo | Việc Trí thực hiện | Câu dẫn hoặc tín hiệu phối hợp |
|---|---|---|
| 00:00–00:30 | Cho thấy run/device/mode PUSH và cache N, đưa app về Home, mở log đã lọc | “Đã ghi baseline và đưa app về nền.” |
| 00:30–01:00 | Update N+1, gửi một tín hiệu theo cấu hình đã chốt, ghi mốc và theo dõi event | “Đã update và gửi. Mình theo dõi từng mốc trong timeline.” |
| 01:00–01:30 | Khi có applied, mở lại UI đọc cache sau mốc đó. Nếu đạt ngưỡng chuyển playback, mở đoạn dự phòng đã chuẩn bị | Dùng câu phù hợp trong bảng xử lý bên dưới |
| 01:30–02:30 | Mở timeline/log hoặc clip periodic đã chọn, đặt con trỏ ở đăng ký lịch, worker start và version | “Đây là PLAYBACK của run periodic trên thiết bị và build đang ghi ở màn hình.” |
| 02:30–03:30 | Mở đoạn Doze hoặc hybrid có evidence tương ứng, cho thấy điều kiện và source của apply | “Đây là PLAYBACK. Các mốc điều kiện hệ thống và cache được ghi trong run này.” |
| 03:30–04:00 | Trở lại sơ đồ trigger-to-cache, sẵn sàng chuyển Vinh ở mốc 04:00 | “Các mốc trigger, worker và cache đã được đặt cạnh nhau để đối chiếu.” |

Ngưỡng biên tập chuyển playback là **30 giây kể từ lúc gửi** trong phần live. Người dẫn giữ mốc gửi thật khi nhận định ngưỡng đã tới. Khung 4 phút được giữ trong mốc 07:00–11:00 của toàn bài. [PRESENTATION_PLAN](../../docs/PRESENTATION_PLAN.md)

| Tình huống nhìn thấy | Câu dùng khi chuyển | Bằng chứng cần hiển thị |
|---|---|---|
| Applied có trước UI reopen | “Cache đã commit version N+1 ở mốc này. Bây giờ mở UI để đọc lại.” | Applied đúng source/run/version và mốc mở UI |
| Chưa có applied sau ngưỡng 30 giây | “Trong cửa sổ live vừa rồi chưa ghi nhận cập nhật. Mình chuyển sang bản ghi đã chuẩn bị.” | Mốc gửi/live hiện tại, nhãn PLAYBACK và metadata run phát lại |
| Có accepted nhưng thiếu receipt/start | “Ở đây đã thấy kết quả gửi. Các mốc phía Android được xem riêng trong timeline.” | Mỗi event đang thực sự có trong log |
| Thiếu build/config hoặc log/clip phù hợp | “Phần thao tác này đang chờ bằng chứng đã kiểm nhận.” | Trạng thái pending và phần sơ đồ/cơ chế đã có |

Sau phần live, lưu log và outcome trong cửa sổ đã khai, giữ event tới muộn để phân tích. Cleanup theo cơ chế cancel/drain và khôi phục môi trường trong protocol, ghi người thao tác và kết quả vào phiếu run. [PROTOCOL](../../experiments/PROTOCOL.md)

## 8. Đầu việc để hoàn tất SEM-46

- [ ] Nhận candidate manifest, candidate gate và CHECKS của SEM-37.
- [ ] Điền đầy đủ bảng build/config/entry point và đối chiếu lời dẫn với thao tác thực trên candidate.
- [ ] Chọn bằng chứng playback có run/device/build và kiểm đường dẫn mở được.
- [ ] Ghi kết quả kiểm live/playback và blocker trong CHECKS, cập nhật bản bàn giao cho SEM-51.

**Giữ trạng thái WIP và chờ hoàn tất các mục trên trước khi merge SEM-46.** [CHECKS SEM-46](../../docs/evidence/SEM-46/CHECKS.md)
