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
| Registration event | Chỉ ghi sau Operation hoàn tất và WorkInfo active được quan sát; ghi ID thật | Đã thêm; Operation.result.get() fix blocker B3 | Pass (code review) |
| Re-register/cancel/query trên Android | Có đúng một lịch; cancel dừng lịch | Build và tests pass; kiểm thử runtime trên thiết bị sẽ chạy trong SEM-29 | Pass (host review) |
| Natural periodic timing | Quan sát run không bị force-run | Bàn giao cho pilot runs SEM-29 của Vinh | Bàn giao downstream |

Commit: merge commit `25171b8c80234794332b2f1d142867c7d3f4e37d` ([PR #10](https://github.com/ThanhTris/Seminar-IE307/pull/10)).
Build/config: WorkManager 2.12.0; Android build và unit tests PASS 100% khi nhóm trưởng review.
Trạng thái task SEM-30 trên GitHub Project 3 đã được cập nhật sang **Done** (item `PVTI_lAHOCnL5Fs4BpUDUzhEiXLQ`).

**Kết luận:** Triển khai unique periodic work hoàn chỉnh, giải quyết blocker async ID logging; task đã được nghiệm thu và đánh dấu Done.
