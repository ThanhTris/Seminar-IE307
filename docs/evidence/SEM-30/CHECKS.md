# SEM-30 CHECKS — Unique periodic work

## Đầu ra

- Scheduler: `android/app/src/main/java/com/thanhtris/seminarie307/sync/PeriodicSyncScheduler.kt`.
- Constraints: `CONNECTED`; unique name `periodic_bulletin_sync`; interval tối thiểu 15 phút; mode phải là PERIODIC/HYBRID.

## Kiểm tra

| Hạng mục | Expected | Actual | Trạng thái |
|---|---|---|---|
| Interval dưới 15 phút | Bị từ chối rõ ràng | `require` kiểm tra trước khi tạo request | Pass (code review) |
| Đăng ký lặp | Chỉ một unique periodic work | Cùng unique name, policy UPDATE; đợi Operation rồi đọc WorkInfo thật | Pass (code review) |
| Hủy | Unique work bị cancel | Đợi Operation cancel hoàn tất rồi ghi cancel event | Pass (code review) |
| Network constraint | Không chạy khi chưa CONNECTED | Constraint được gắn vào request | Pass (code review) |
| Registration event | Chỉ ghi sau Operation hoàn tất và WorkInfo active được quan sát; ghi ID thật | Đã thêm; chưa chạy Android | Pass (code review) |
| Re-register/cancel/query trên Android | Có đúng một lịch; cancel dừng lịch | Chưa chạy trên thiết bị | Not run |
| Natural periodic timing | Quan sát run không bị force-run | Chưa có run manifest/log | Not run |

Commit/config: working tree hiện tại, chưa commit; WorkManager 2.12.0; build chưa chạy. SEM-28 setup/M1 artifacts đã có trong checkout; M1 document ghi nhận historical build/runtime pass. Các thay đổi core hiện tại chưa được build lại. Blocker runtime: Android SDK/ADB và thiết bị không hiện diện trong môi trường này. `periodic_registered` chỉ xác nhận WorkManager chấp nhận/đang giữ unique work, không xác nhận worker đã dispatch.

**Kết luận:** implementation có; runtime acceptance và kiểm nhận đầu vào vẫn mở.
