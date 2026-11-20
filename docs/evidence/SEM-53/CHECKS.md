# SEM-53 — Kiểm tra chuẩn bị tái lập và quay demo

## Kết quả runtime ngày 20/11/2026

Dùng cặp APK debug đã xác minh từ commit app/server `76fece00110e0dba83c59b3e56bdabd2b4b7934e`. E01 được ghi ở pha `pilot`. [Hash hai APK và các bộ dữ liệu](https://github.com/ThanhTris/Seminar-IE307/blob/a7f7d2b4148d97280affd468fbcabdc288868173/docs/evidence/SEM-42/CHECKS.md)

| Hạng mục | Kết quả |
| --- | --- |
| Emulator MANUAL | HTTP 200 và áp dụng v2 trong `demo-manual-76fece0-r2`. |
| Emulator E01 PERIODIC | Cache v2 → v3 trong cửa sổ 90 phút. Quan sát 2 chu kỳ tự nhiên, dưới mục tiêu 3. Android export báo `PARTIAL` với 1 omission `periodic_cancelled`. |
| Đối chiếu trên OPPO Find X9 | Lượt hoàn tất `run-sem42-oppo-e01-03` có 5 chu kỳ tự nhiên trong 90 phút. Cache v4 → v5 khi app ở nền, OPPO cắm USB qua ADB reverse. Lượt `run-sem42-oppo-e01-02` dừng khi app trở lại tiền cảnh và có dữ liệu riêng. |
| E02 silent push | `NOT_RUN`, preflight ghi `FIREBASE_NOT_CONFIGURED`. |
| Video | `NOT_RUN`. Dữ liệu E01 đã có để chuẩn bị đoạn PERIODIC playback. |

[Timeline emulator](https://github.com/ThanhTris/Seminar-IE307/blob/e6a1857da2a25feebd1bed3681d7e43d32d7843c/docs/evidence/SEM-53/EMULATOR_2026-11-20.md)

## Kiểm tra chuẩn bị ngày 19/11/2026

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

Emulator đã cài app/test APK development và đối chiếu SHA-256 của bản cài. Probe GET đạt sau khi mạng emulator ổn định. MANUAL áp dụng v1, lịch PERIODIC đăng ký và hủy được. Export kiểm tra trả `PARTIAL` do một event `periodic_cancelled` chưa được schema v2 hỗ trợ. Phiên thử và server loopback đã dừng.

Tài liệu chạy lại: [REPRODUCTION](REPRODUCTION.md). Khi video đủ ba phần và link đã kiểm, bàn giao manifest cho SEM-54/55.
