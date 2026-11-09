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
