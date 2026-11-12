# SEM-15 — Giải thích cơ chế silent push và giới hạn FCM

- Trạng thái: **Done** (Project).
- Trạng thái đầu vào: **Đã hoàn thành**.
- Còn chờ: Không.
- Đối chiếu Project: 2026-11-12 14:11:12 UTC.
- Người thực hiện duy nhất: **Trang** (`rosy179`).
- Hạn: **30/10/2026 18:00 (UTC+7)**.
- Công sức: 3/100 — Cơ chế/thực hành.
- Tách từ nhóm cũ: [SEM-02](SEM-02.md); nhóm cũ chỉ còn lưu lịch sử.

## Dependency — bấm mã task để mở yêu cầu

- **Bắt đầu sau:** Không có.
- **Hoàn tất còn cần:** Không có.

Không có gate bắt đầu nghĩa là làm được ngay. Mục Hoàn tất còn cần là đầu vào nên dùng nếu đã có, không chặn chuyển Done: owner chuyển Done khi đầu ra và CHECKS của chính task có thật; đầu vào chưa có thì ghi Not run/giới hạn trong CHECKS. Bản nháp/fixture phải ghi đúng nhãn, không được gọi là kết quả chạy thật.

<!-- task-inputs:start -->
## Đầu vào cần nhận

Tài liệu nền đã có: [Kế hoạch/phạm vi](../../docs/PLAN.md) · [Nguồn kỹ thuật và nghiên cứu](../../research/README.md).

Không cần nhận đầu ra từ task khác để bắt đầu. Owner thực hiện từ tài liệu nền và tự ghi các blocker môi trường/quyền truy cập trong CHECKS của task này.

Status nguồn được đối chiếu Project lúc **2026-11-12 14:11:12 UTC**; mở link task nguồn để xem cập nhật mới hơn.
<!-- task-inputs:end -->


## Việc Trang cần làm

1. Viết luồng server → FCM → callback → worker và giới hạn thực thi nền.
2. Phân biệt notification/data/mixed, normal priority và FCM accepted với app received.
3. Gắn nguồn chính thức và version áp dụng; EAP chỉ ghi phụ lục, không trộn với baseline v1.

## Đầu ra bắt buộc

- `docs/mechanisms/SILENT_PUSH.md`
- `docs/evidence/SEM-15/CHECKS.md`: commit/build/config, thao tác, expected/actual, Pass/Fail/Not run, evidence, blocker và đầu ra đã bàn giao.

## Tiêu chí hoàn thành

- [x] Có thể giải thích vì sao data-only không đồng nghĩa một thông báo bị tắt tiếng.
- [x] Chỉ ra trường hợp trì hoãn/không nhận và không hứa push tức thì.
- [x] Đầu ra và CHECKS có thật, link đọc được; chưa chạy phải ghi Not run, không tự chuyển Done từ kế hoạch.

## Đầu ra đã soát ngày 05/11/2026

[SILENT_PUSH 1.0.0](../../docs/mechanisms/SILENT_PUSH.md) · [CHECKS SEM-15](../../docs/evidence/SEM-15/CHECKS.md).

Đã hoàn thiện tài liệu nghiên cứu chuyên sâu và hồ sơ kiểm tra:
1. Phân biệt kiến trúc Data-only vs Muted Notification và bảng đối chiếu 3 dạng payload FCM.
2. Phân tích hạ tầng kết nối GmsCore MCS Socket (port 5228), chu kỳ Heartbeat và máy trạng thái RRC của modem di động (Tail Energy).
3. Luồng dữ liệu end-to-end 10 bước (Server -> FCM -> GmsCore -> Callback -> WorkManager -> GET API -> Room Version Guard -> Compose UI).
4. Giới hạn thực thi nền của Service (cửa sổ 10-20s, rủi ro ANR/SIGKILL) và nguyên tắc Ingest & Offload sang WorkManager (< 100ms).
5. Phân tích Normal vs High Priority, cơ chế Doze gom cụm và chính sách phạt giáng cấp (Deprioritization).
6. Phân tích chuyên sâu 8 rào cản kỹ thuật gây trễ/mất push: Doze/Standby, TTL 24h, Queue 100 tin, Force-Stop (FLAG_EXCLUDE_STOPPED_PACKAGES), OEM Killers (ColorOS trên OPPO Find X9), Silent Socket Drop/NAT, Rate Limits, Token Invalidation.
7. Ma trận phân định ranh giới nhận thức sự kiện theo EVENT_SCHEMA 2.0.0.
8. Cung cấp Code Blueprints hoàn chỉnh: Kotlin FirebaseMessagingService cho Trang (SEM-32) và Node.js Admin SDK cho Tâm (SEM-35).
9. Cung cấp trọn bộ 10 câu hỏi phản biện chuyên sâu kèm đáp án chi tiết cho Tuấn (SEM-19).
10. Thư viện 9 nguồn tài liệu chính thức từ Google/Android/AOSP.

Đây là bàn giao nghiên cứu cơ chế và hợp đồng thiết kế của SEM-15; các ca đo thực nghiệm vẫn **Not run** để bàn giao cho các task pilot/main runs downstream. Checklist này không tự chuyển Status Project sang Done; các trường Project phía trên vẫn là snapshot hiện hành.

## Task được mở khóa

- [SEM-19](SEM-19.md) cần đầu ra này để **hoàn tất**.
- [SEM-22](SEM-22.md) cần đầu ra này để **hoàn tất**.
- [SEM-32](SEM-32.md) cần đầu ra này để **bắt đầu**.
- [SEM-47](SEM-47.md) cần đầu ra này để **bắt đầu**.

## Ranh giới thực hiện

Một task chỉ có Trang thực hiện và cập nhật phần việc này. Người nhận đầu ra làm task riêng được liên kết ở trên; không có đồng thực hiện hay reviewer được gán thêm vào thẻ. Lỗi thuộc đầu ra này trả về task này ở Needs Update. Không sửa phần do task khác sở hữu mà chưa cập nhật ranh giới/bàn giao.
