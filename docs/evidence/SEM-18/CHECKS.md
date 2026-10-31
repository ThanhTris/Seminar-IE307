# SEM-18 — CHECKS và bàn giao review

- Người thực hiện: Tâm (`HoaiTam`).
- Ngày đối chiếu/kiểm tra: **31/10/2026 (UTC+7)**; không ghi lùi thời gian theo deadline.
- Hạn được giao: **30/10/2026 18:00 (UTC+7)**, giữ nguyên.
- Base: `730d5ddca974b7551166d874a80050aeb2c28794` (`origin/main`, đã fetch trước khi tạo nhánh).
- Nhánh: `codex/SEM-18-server-fcm`.
- Đầu ra: [SERVER_FCM.md](../../mechanisms/SERVER_FCM.md) và CHECKS này; commit artifact ban đầu `22c393f4323510339547e849986393fff3834010`. CHECKS/snapshot được cập nhật thêm khi bàn giao Review.
- Loại bằng chứng: review tài liệu/nguồn và kiểm cấu trúc ví dụ. **Không có run FCM, Android hoặc phép đo runtime trong SEM-18.**

## Đầu vào đã đọc

[Yêu cầu SEM-18](../../../tasks/backlog/SEM-18.md) không có gate bắt đầu hoặc gate hoàn tất. Đã đọc [PLAN](../../PLAN.md), [SHARED_SYNC của SEM-14](../../mechanisms/SHARED_SYNC.md), [protocol](../../EXPERIMENT_PROTOCOL.md), [nguồn nghiên cứu](../../../research/README.md) và [hồ sơ môi trường SEM-13](../../environment/SERVER_FIREBASE.md). Chỉ dùng các tài liệu này làm cơ sở thiết kế, không suy rằng runtime đã tồn tại/đã chạy.

## Acceptance và kiểm chứng

| Check | Expected | Actual / evidence | Kết quả |
|---|---|---|---|
| Bốn mốc cơ chế tách riêng | Không đồng nhất accepted, received, started, applied | `SERVER_FCM.md` có luồng 8 bước và bảng bằng chứng riêng cho `push_send_accepted`, `push_received`, `work_started`, `snapshot_applied`, thêm update/enqueue để làm rõ các ranh giới | Pass — review tài liệu |
| Persist và send độc lập | Version đã commit không bị rollback chỉ vì push lỗi | Mô tả persist trước send, giữ snapshot cho GET/periodic, phân biệt skip-push có chủ ý với delivery failure | Pass — thiết kế, chưa chạy server |
| ID thật và nullable | Không bịa message ID, accepted không thành delivered | Không có response FCM giả; minh họa định dạng được gắn nhãn; ID chưa biết là null; callback ID opaque; signal/attempt ID tách riêng khỏi FCM ID | Pass — review tài liệu |
| Correlation | Nối được event mà không trộn run/request/work/message | Bảng nêu ai tạo ID, phạm vi, request giữ qua retry, periodic cycle có request ID mới, quan hệ nhiều signal → work, không join chỉ bằng UTC/version | Pass — đề xuất cho SEM-26 |
| Baseline và payload | V1 data-only normal, không có notification hoặc EAP | Parse được một JSON fixture; chỉ có token placeholder/data/android, data đều string; mode/source PUSH, hint không âm; HTTP priority NORMAL, TTL 600s; Admin tương ứng normal/600000ms | Pass — fixture offline |
| TTL và trạng thái chưa biết | Không xem TTL là deadline worker hoặc timeout là FCM rejection | Nêu phạm vi/default/TTL 0 theo Firebase; ví dụ 600s chưa là cấu hình run; response mất thì unknown, callback chưa có thì chưa quan sát được | Pass — đối chiếu nguồn |
| Đồng hồ | UTC liên máy khác monotonic nội bộ Android | Ghi clock offset, elapsedRealtime có deep sleep, cùng boot/session; không trừ hai monotonic khác máy hoặc báo latency chính xác khi clock offset chưa kiểm soát | Pass — đối chiếu nguồn |
| Lỗi và retry | Không gộp local validation, provider error và mất response | Bảng tách các nhóm, dùng mã HTTP v1, giữ mã SDK thật, Retry-After/backoff theo từng lỗi, không retry vô hạn/token invalid | Pass — review tài liệu |
| Ranh giới task | Không chốt wire schema hoặc viết sender thay task sau | signal_id/send_attempt_id/outcome bổ sung ghi rõ là đề xuất cho SEM-26; code sender và test thật thuộc SEM-35, các phần cache/worker theo shared contract | Pass |
| Runtime / quyền gửi | Chỉ nhận kết quả có run thật | Chưa gửi push, không có response message ID; callback/worker/Room/Doze chưa chạy. Không kiểm lại quyền bằng lệnh gửi trong task giải thích | **Not run** |

Nguồn chính thức được mở và đối chiếu ngày 31/10/2026, đặt cạnh luận điểm trong artifact: HTTP v1 send, Admin Messaging.send, AndroidConfig REST/Node, message lifespan, nhận message/priority, RemoteMessage, error codes và SystemClock. Tra cứu API SystemClock trực tiếp bị timeout; đã đối chiếu nội dung từ kết quả tìm kiếm chính thức Android Developers. Không dùng blog bên thứ ba để chốt hành vi API.

## Tình huống đã review trên tài liệu

Đây là kiểm logic giải thích, không phải chạy các ca E01–E06 và không đưa vào `experiments/results.csv`.

| Tình huống | Kết luận đúng theo tài liệu | Kết quả review |
|---|---|---|
| Persist thành công, gửi thất bại | Snapshot vẫn có để GET; chưa có bằng chứng push tới app | Pass |
| FCM trả ID, chưa có callback trong cửa sổ | Chỉ accepted; không tự tạo received/applied hoặc kết luận FCM mất tin | Pass |
| Callback được log trước response send | Nối bằng signal ID của ứng dụng; không áp đặt thứ tự UTC liên máy | Pass |
| Callback không có FCM ID | Giữ message_id null; không thay bằng signal/request/work ID | Pass |
| Timeout sau khi đã gửi request | Outcome unknown; retry có thể trùng; mỗi send attempt được phân biệt | Pass |
| Payload lỗi local hoặc token unregistered | Phân biệt validate trước RPC với provider rejection; sửa nguyên nhân, không retry mù | Pass |
| Hai tín hiệu trùng hoặc hint cũ | Shared core dùng GET/version guard; không đòi mỗi push tạo một cache write | Pass |
| Server đã có version mới hơn hint | GET lấy snapshot hiện hành, hint không có quyền ghi đè cache | Pass |
| TTL hết/chưa nhận/worker đã enqueue | Không suy TTL hết chỉ từ log thiếu; TTL không hủy worker đã enqueue | Pass |
| Clock lệch hoặc reboot | Không tính latency giả từ UTC/monotonic không cùng hệ quy chiếu | Pass |
| Send dry-run | Chỉ validation, không gọi đó là accepted của phân phối thật | Pass |

## Kiểm tra cấu trúc và chất lượng

Đã parse JSON trong Markdown bằng Python `json.loads`, kiểm placeholder, data string, source/mode/version, data-only, priority và đơn vị TTL. Đây là kiểm cấu trúc fixture, không phải FCM validate-only API hoặc xác nhận Firebase nhận payload.

Kiểm tra hai artifact: **13 link nội bộ** tồn tại, newline cuối, không trailing whitespace, code fence cân bằng và không có mẫu private key/API key/GitHub token. Các ví dụ không chứa credential hoặc token thật. `git diff --cached --check` Pass trước commit. Không cần build app/server vì không sửa code/config runtime.

## Workflow và giới hạn quyền thực hiện

Đã tạo nhánh từ main, chuyển riêng SEM-18 **Todo → In Progress → Review** và tạo [PR #5](https://github.com/ThanhTris/Seminar-IE307/pull/5). Snapshot đồng bộ lúc **31/10/2026 20:26:56 (UTC+7)** bằng script chính thức:

```sh
python3 scripts/update_task_snapshot.py --apply
python3 scripts/update_task_snapshot.py --check
```

Cả hai lệnh **Pass**: 45 task, **4 Done / 40 Todo / 1 Review**; đầu vào **10 Sẵn sàng / 8 Chuẩn bị trước / 27 Chờ đầu vào**; một assignee khớp owner mỗi task, dependency không có vòng lặp. Ngoài hai artifact, script cập nhật 48 file snapshot. Đối chiếu diff xác nhận chỉ workflow status SEM-18 đổi từ Todo sang Review; không đổi scope/owner/deadline/dependency/công sức hoặc acceptance checklist. SEM-35/49 vẫn chờ đầu vào, không được mở gate vì SEM-18 còn Review.

Theo yêu cầu của HoaiTam, **dừng ở Review**: nhóm trưởng kiểm nhận và quyết định merge/Done. Không tự merge, không tự chuyển Done, không coi review của tác giả ở bảng trên là chấp thuận của nhóm trưởng. Chỉ sửa tiếp khi có comment yêu cầu fix từ nhóm trưởng. Checklist nghiệm thu trên task được để nhóm trưởng kiểm nhận, không dùng để vượt gate phụ thuộc khi trạng thái còn Review.

## Bàn giao cho các task nhận đầu ra

- **SEM-19 — Tuấn:** dùng luồng server/FCM/shared sync, bảng event và khoảng chưa biết. Nhận đúng revision sau khi nhóm trưởng chấp thuận; không cùng sửa file tổng hợp của Tuấn.
- **SEM-35 — Tâm:** dùng baseline data-only/normal, quy tắc accepted/rejected/unknown và nullable IDs; phải nhận thêm SEM-13/27, cấu hình local và token thật trước test sender.
- **SEM-49 — Tâm:** dùng phần kiến trúc và giới hạn accepted/delivered; nội dung slide cuối phải đối chiếu runtime và các input hoàn tất riêng.
- **SEM-26 — Tâm:** có thể tham khảo đề xuất correlation để chốt schema; chưa tự thêm bắt buộc signal/attempt fields cho core của thành viên khác.

Blocker runtime còn từ SEM-13: chưa xác nhận Firebase project/quyền/credential và thiết bị/ADB; code server/sender thuộc task sau. Các mục này không chặn việc soạn và review tài liệu SEM-18 nhưng vẫn chặn tuyên bố gửi/nhận/sync thành công. Giữ **Not run**, không tạo log thực nghiệm thay thế.
