# Hướng dẫn chế độ PERIODIC

## Cấu hình hiện tại

- Worker: `SyncWorker`, dùng chung `SyncRepository` và Room cache.
- Tên unique work: `periodic_bulletin_sync`.
- Chu kỳ mặc định/tối thiểu: 15 phút; yêu cầu nhỏ hơn bị từ chối.
- Constraint: `NetworkType.CONNECTED`.
- Policy đăng ký lại: `ExistingPeriodicWorkPolicy.UPDATE`.
- Hủy: `cancelUniqueWork(PERIODIC_WORK_NAME)`.

Đăng ký periodic cần `mode=PERIODIC` hoặc `HYBRID` cùng `runId` hợp lệ. Mode `PUSH` không được phép đăng ký periodic. Trạng thái đăng ký có thể quan sát qua `isPeriodicScheduledFlow()`. Flow cho biết có unique work chưa kết thúc; nó không chứng minh work đã chạy.

## Quy trình chạy ca

1. Ghi build/commit, phiên bản Android, thiết bị alias, mode, run ID, chu kỳ và thời điểm bật lịch.
2. Tắt/hủy trigger không thuộc mode của ca; chờ work đang chạy kết thúc hoặc đánh dấu ca nhiễu.
3. Bật periodic và quan sát timeline. Chỉ `work_started` là bằng chứng worker chạy; `snapshot_applied` mới là bằng chứng cache nhận version mới.
4. Để thiết bị ở trạng thái tự nhiên trong cửa sổ đo. Không bấm manual sync, không ép jobscheduler, không bật/tắt mạng giữa cửa sổ trừ khi protocol của ca yêu cầu.
5. Kết thúc cửa sổ, lưu manifest và event JSONL gốc; nếu không quan sát thấy worker, ghi timeout/NOT_RUN theo protocol, không tạo event thành công.

## Chẩn đoán Android

Thay `<serial>` và `<package>` theo thiết bị/build đã ghi. Các lệnh dump chỉ quan sát trạng thái, không tạo run tự nhiên:

```powershell
adb -s <serial> shell dumpsys jobscheduler
adb -s <serial> shell dumpsys deviceidle
adb -s <serial> shell dumpsys connectivity
```

Tìm package trong output `jobscheduler`, đối chiếu trạng thái và ràng buộc với timeline. Không dùng `cmd jobscheduler run` trong cửa sổ đo tự nhiên; lệnh này chủ động kích hoạt job và làm nhiễu kết quả. Nếu cần khảo sát Doze, ghi riêng bước đưa máy vào Doze và thoát Doze; không xem đó là vận hành tự nhiên.

## Đọc timeline và giới hạn

- `periodic_registered`: WorkManager chấp nhận đăng ký và WorkInfo active được quan sát; không đồng nghĩa worker đã dispatch.
- `work_started`: worker bắt đầu; ghi source `PERIODIC`, run ID, work ID và attempt.
- `snapshot_applied`: transaction Room đã commit version mới.
- `snapshot_unchanged`: version đã biết; không tính là cập nhật dữ liệu.
- `snapshot_stale`: response cũ bị bỏ qua.
- `sync_retrying`/`sync_failed`: lỗi tạm thời còn lượt retry / lỗi kết thúc.

UTC dùng để so với log server sau khi hiệu chỉnh clock offset. Thời lượng trên cùng thiết bị ưu tiên `elapsed_realtime_ms` trong cùng boot session. Không trừ monotonic timestamp qua reboot. Scheduler logic hoặc một lần force-run không chứng minh chu kỳ tự nhiên chạy đúng mốc; WorkManager chịu quản lý pin/tài nguyên và có thể trì hoãn.

Nguồn cơ chế và phiên bản dependency xem [PERIODIC_FETCH.md](mechanisms/PERIODIC_FETCH.md). Build chưa được chạy trong lần bàn giao này; trạng thái kiểm chứng nằm tại [SEM-31](evidence/SEM-31/CHECKS.md).
