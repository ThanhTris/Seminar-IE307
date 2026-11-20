# SEM-53 — Quy trình tái lập demo

**Tình trạng:** APK debug đã bàn giao ở `release/` (PR #36); còn chờ cấu hình Firebase cho đoạn PUSH và bản quay video. Quy trình dưới đây chuẩn bị cho lần chạy thật trên emulator. Kết quả từng bước ghi tại [CHECKS](CHECKS.md).

## Cài và kiểm tra đầu vào

1. Nhận APK, app/server commit, package/version, SHA-256 và runbook từ SEM-52. Kiểm chữ ký, hash file và hash APK đã cài trên `Medium_Phone_API_37.0`. Ghi profile Firebase theo nguồn bàn giao, giữ token và credential trong vùng lưu riêng.
2. Dùng server loopback với store demo riêng. Kiểm `/health` và GET từ client. Tạo run ID riêng cho mỗi đoạn, đồng bộ baseline bằng MANUAL ngoài đoạn đo, xác minh cache version và đợi work setup kết thúc.
3. Dùng dữ liệu bản tin mẫu của nhóm và chỉ quay UI app, timeline hoặc cửa sổ log đã lọc. Ghi timestamp bắt đầu/kết thúc, target và outcome từ evidence gốc.

## Các đoạn quay

| Đoạn | Bằng chứng cần xuất hiện |
| --- | --- |
| PUSH | Server commit target, FCM data-only normal gửi thật, callback và worker. Có `snapshot_applied` đúng target trước khi mở lại UI đọc cache. |
| PERIODIC | `periodic_registered`, cycle tự nhiên và `snapshot_applied` đúng version. Dùng clip đã ghi, chú thích khoảng thời gian chờ đã cắt. |
| HYBRID | CLI SEM-40 dùng `--skip-push` trên update thật. Log `push_send_skipped` và lần `snapshot_applied` sau đó có source PERIODIC. |

Đóng run và kiểm work đã drain trước khi đổi mode. Gắn nhãn Playback và run ID vào bản dựng. Giữ clip cuối không quá 4 phút và diễn tập đổi sang clip offline sau 30 giây nếu bước live chưa thành công. Ghi riêng phần chưa chạy và báo sai lệch runbook về SEM-52.

## Bàn giao

Rà phụ đề, hình và âm thanh để loại thông tin cá nhân và thông tin truy cập. Tính SHA-256 của video cuối. Upload lên Drive và cấp quyền theo thông báo seminar. Xác minh quyền xem/tải bằng tài khoản được chia sẻ, thử clip offline, rồi điền build, checksum, duration, run links và link Drive vào [VIDEO_MANIFEST](../../../release/VIDEO_MANIFEST.json).

Nguồn: [runbook SEM-52](../../DEMO_RUNBOOK.md), [kịch bản 4 phút](../../PRESENTATION_PLAN.md#kịch-bản-demo-4-phút), [yêu cầu nộp](../../SUBMISSION_REQUIREMENTS.md).
