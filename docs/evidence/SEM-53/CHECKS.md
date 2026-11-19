# SEM-53 — Kiểm tra chuẩn bị tái lập và quay demo

- Base: `9caaf38f3932269bdcdd74aa0bfef0e9fc148271`.
- Kiểm ngày 19/11/2026 (UTC+7) trên Windows. Dùng emulator cho demo.
- Trạng thái video: **NOT_RUN**. [VIDEO_MANIFEST](../../../release/VIDEO_MANIFEST.json) chưa có APK, video, hash hay link Drive.

| Kiểm tra | Expected | Actual | Kết quả |
| --- | --- | --- | --- |
| Bản phát hành SEM-52 | APK và SHA-256 đúng source cùng runbook | Project Done. Build manifest `NOT_BUILT`, APK và hash null. Không có APK bàn giao trong GitHub Releases hoặc Actions. | Blocked |
| Tái lập đúng build | Cài và chạy đúng APK SEM-52 trên emulator | Chưa nhận APK. | Not run |
| PUSH live | FCM thật, có callback và applied của target | Chưa có cấu hình Firebase chuẩn cho workspace và chưa có APK bàn giao. | Not run |
| PERIODIC playback | Có clip từ cycle tự nhiên của build bàn giao | Chưa có ca video đúng build. | Not run |
| HYBRID playback | Có `push_send_skipped` và applied từ PERIODIC | Chưa có ca video đúng build. | Not run |
| Video và Drive | Clip thật ≤4 phút, hash, link kiểm bằng tài khoản được chia sẻ và playback offline | Chưa tạo video hoặc upload. | Not run |

Trong đợt chuẩn bị chung, bản development từ `9caaf38` đã assemble app/test APK và qua 32/32 unit tests. Server build và đạt 22/22 tests trên Windows. Các kiểm tra này chuẩn bị môi trường để tái lập khi nhận đúng artifact SEM-52.

Tài liệu chạy lại: [REPRODUCTION](REPRODUCTION.md). Khi video đủ ba phần và link đã kiểm, bàn giao manifest cho SEM-54/55.
