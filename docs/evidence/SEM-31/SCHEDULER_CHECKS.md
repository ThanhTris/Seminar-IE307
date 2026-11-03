# SEM-31 Scheduler checks

Thiết bị/run chưa được cung cấp trong workspace nên các bước dưới đây chưa được thực thi. Đây là biên bản chờ chạy, không phải bằng chứng pass.

| Case | Input/thao tác | Expected | Actual | Trạng thái |
|---|---|---|---|---|
| Re-register | Gọi suspend schedule 2 lần với cùng unique name; quan sát WorkManager unique work | Một periodic work còn hoạt động; `periodic_registered` có ID thật sau khi Operation/WorkInfo xác nhận | Chưa chạy | Not run |
| Cancel | Gọi suspend cancel unique work; xem WorkInfo và timeline | Không còn lịch đang hoạt động; cancel event sau Operation | Chưa chạy | Not run |
| Constraint | Tắt mạng trước cửa sổ đủ điều kiện, sau đó bật lại | Worker chờ CONNECTED rồi mới có thể chạy; thời điểm không được khẳng định chính xác | Chưa chạy | Not run |
| Natural run | Để máy không tương tác trong khoảng đo, không force-run | `work_started` chỉ khi worker thực sự chạy; applied chỉ khi commit | Chưa chạy | Not run |
| Dump state | `adb -s <serial> shell dumpsys jobscheduler` và `dumpsys deviceidle` | Có artifact/log đã lọc định danh, nối với build/run | Chưa chạy | Not run |

Không dùng `adb shell cmd jobscheduler run` trong case natural run. Ghi build SHA, Android/API, thiết bị alias, interval, thời điểm bật lịch và log gốc khi thực thi.
