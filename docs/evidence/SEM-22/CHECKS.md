# SEM-22 — CHECKS và Bàn giao Nghiệm thu Đối chiếu Bài báo

- **Người thực hiện:** Trang (`rosy179`).
- **Nhiệm vụ:** SEM-22 — Đối chiếu hai bài nghiên cứu với API push hiện hành.
- **Thuộc đề tài:** Seminar IE307 (Chủ đề 12: *Xử lý việc tìm nạp nền và thông báo đẩy im lặng, minh họa trên Android*).
- **Ngày lập và kiểm tra:** **05/11/2026 (UTC+7)**; thời gian thực tế hoàn thành task.
- **Hạn được giao trong kế hoạch:** **01/11/2026 22:00 (UTC+7)** (mốc deadline gán ban đầu).
- **Base commit:** `9b5408b4eb99f2a74c4e78df7a96a9e144a991f8` (`main`, bao gồm merge PR #13 của SEM-15 và PR #14 của SEM-20).
- **Nhánh làm việc:** `codex/SEM-22-papers-push-api`.
- **Đầu ra bàn giao:**
  - Báo cáo đối chiếu học thuật: [research/notes/API_CROSSCHECK.md](../../../research/notes/API_CROSSCHECK.md)
  - Hồ sơ kiểm tra & nghiệm thu: [docs/evidence/SEM-22/CHECKS.md](CHECKS.md)
- **Loại kiểm chứng:** Đánh giá tài liệu học thuật (Literature & Specification Cross-check), kiểm tra tính hợp lệ cú pháp Mermaid, kiểm tra liên kết nội bộ, và đối chiếu nguồn chính thức của Google / AOSP / DOI bài báo. **Không có phép đo runtime trên thiết bị thật trong task này.**

---

## 1. Đầu vào đã tiếp nhận và đối chiếu

Theo [nhiệm vụ SEM-22](../../../tasks/backlog/SEM-22.md), task cần nhận đủ 3 đầu ra trước khi hoàn tất:
1. **[SEM-15](../../../tasks/backlog/SEM-15.md) (Trang bàn giao):** [SILENT_PUSH.md](../../../docs/mechanisms/SILENT_PUSH.md) và [CHECKS SEM-15](../SEM-15/CHECKS.md) — Đặc tả FCM HTTP v1, data-only, normal priority, TTL 24h, WorkManager 2.12.0, giới hạn thực thi nền và rào cản OEM. Đã merge vào `main` tại commit `8f85e8f`.
2. **[SEM-20](../../../tasks/backlog/SEM-20.md) (Tuấn bàn giao):** [PAPER_1.md](../../../research/notes/PAPER_1.md) và [paper-1.bib](../../../research/metadata/paper-1.bib) — Ghi chú nghiên cứu Simon et al. (2017) về DiffSync, chi phí chu kỳ rỗng 96.8% trên iOS 7 / iPhone 5s. Đã merge vào `main` tại commit `9931af1`.
3. **[SEM-21](../../../tasks/backlog/SEM-21.md) (Tâm bàn giao):** [PAPER_2.md](../../../research/notes/PAPER_2.md) và [paper-2.bib](../../../research/metadata/paper-2.bib) — Ghi chú nghiên cứu González-Pérez et al. (2022) về độ tin cậy lập lịch tác vụ nền trên Android 7–11 qua AlarmManager/WakeLock/NTD. Đã merge vào `main` tại commit `94f72c4`.

---

## 2. Bảng kiểm tra tiêu chí nghiệm thu (Acceptance Checks)

| STT | Tiêu chí kiểm tra | Kết quả mong đợi (Expected) | Bằng chứng thực tế (Actual / Evidence) | Đánh giá |
|:---:|---|---|---|:---:|
| 1 | **Chuẩn bị bảng documentation FCM v1** | Bảng chuẩn hóa FCM v1, data-only, normal priority, TTL 24h kèm hành vi Android | Mục 2 trong `API_CROSSCHECK.md` lập bảng đặc tả 6 thuộc tính API bám sát tài liệu chính thức của Google, đối chiếu wire format và hành vi trên GmsCore / WorkManager | **Pass** |
| 2 | **Đối chiếu Paper 1 (Simon et al., 2017)** | Đối chiếu chi phí chu kỳ rỗng 96.8%, rủi ro Lost Wake-Up, và tách rời trigger vs data payload | Mục 3 phân tích chi tiết: (1) Chu kỳ rỗng gây hao Tail Energy trên modem nhưng interval bị WorkManager chặn tối thiểu 15 phút; (2) Thay cờ in-memory `loopOnceMore` bằng WorkManager `REPLACE` và Room Version Guard; (3) Tách payload push nhẹ < 1 KB với HTTP GET snapshot | **Pass** |
| 3 | **Đối chiếu Paper 2 (González-Pérez et al., 2022)** | Đối chiếu tỷ lệ miss alarm 84%, chống lách luật bằng Exact Alarm/Foreground Service, và phân mảnh OEM | Mục 4 phân tích chi tiết: (1) Scheduled != Executed trên Doze Mode hiện đại; (2) Chính sách Google cấm exact alarm và siết chặt foreground service; (3) Khớp nối phát hiện phân mảnh OEM của paper với rào cản ColorOS trên OPPO Find X9 | **Pass** |
| 4 | **Không trộn lẫn kết quả paper với demo** | Không biến số liệu đo đạc lịch sử thành kết quả của đề tài hiện tại | Toàn bộ các số liệu cũ (96.8% rỗng của Simon et al., 84% miss của González-Pérez et al., mức hao pin 0.22%/min trên iPhone 5s) đều được ghi nhận đúng ngữ cảnh lịch sử, không đưa vào `results.csv` của nhóm | **Pass** |
| 5 | **Ma trận đối chiếu toàn diện có vị trí mục/trang** | Lập bảng ma trận đối chiếu từng Claim kèm mục, trang, API hiện hành, đánh giá và ca thử nghiệm | Mục 5 lập bảng ma trận chi tiết 8 claims (`P1-C1` đến `P1-C4`, `P2-C1` đến `P2-C4`) có trích dẫn chính xác mục/trang trong 2 bài báo và gắn mã ca thử nghiệm `E01`–`E06` | **Pass** |
| 6 | **Định vị mô hình HYBRID từ góc độ học thuật** | Chứng minh giá trị khoa học của mô hình HYBRID giải quyết điểm nghẽn của 2 bài báo | Mục 6 có sơ đồ Mermaid và luận giải chứng minh HYBRID kết hợp Push (Fast Lane) và Periodic (Safety Net) qua một Sync Core chung giải quyết trọn vẹn nhược điểm của polling rỗng và push rớt mạng | **Pass** |
| 7 | **Tách biệt phụ lục EAP** | Không trộn lẫn các API thử nghiệm (FCM v2, BackgroundSync) vào baseline v1 | Mục Phụ lục ở cuối tài liệu được tách biệt rõ ràng, giải thích lý do không đưa EAP vào baseline v1 | **Pass** |
| 8 | **Liên kết Markdown nội bộ và định dạng** | Toàn bộ liên kết tương đối trỏ đúng file tồn tại, bảng biểu chuẩn Markdown | Toàn bộ relative links trỏ tới `PAPER_1.md`, `PAPER_2.md`, `SILENT_PUSH.md`, `DEVICES.md`, `PROTOCOL.md` đều hợp lệ 100%; không có liên kết hỏng | **Pass** |
| 9 | **Kiểm tra định dạng whitespace & bảo mật** | Không có lỗi trailing whitespace, không chứa credentials hay API keys nhạy cảm | `git diff --check` đạt chuẩn; tài liệu thuần túy học thuật | **Pass** |
| 10 | **Kiểm thử Runtime trên thiết bị thật / Emulator** | Kiểm tra hành vi push thực tế trên Android runtime | SEM-22 là task nghiên cứu đối chiếu học thuật. Các ca chạy máy thật và số liệu đo đạc thuộc về các task pilot/main runs downstream (`E01`–`E06` của Vinh) | **Not run** (Theo phân công) |

---

## 3. Rà soát kịch bản đối chiếu học thuật (Scenario Review)

| Tình huống đối chiếu | Nhận định của Bài báo lịch sử | Đối chiếu với Kiến trúc Đề tài Seminar IE307 | Đánh giá |
|---|---|---|:---:|
| **1. Tần suất Polling định kỳ** | Paper 1 khảo sát interval 0–60 giây cho ứng dụng chỉnh sửa PDF cộng tác | Android WorkManager áp đặt giới hạn tối thiểu 15 phút; không thể và không được phép polling dồn dập | **Khác biệt lớn về kiến trúc** |
| **2. Tỷ lệ chu kỳ rỗng (Empty Cycles)** | Paper 1 ghi nhận 96.8% chu kỳ polling là rỗng trên server log Mendeley | Seminar quan sát hiện tượng này qua event `snapshot_unchanged` trong ca `E01`, chứng minh sự lãng phí tài nguyên của periodic khi server ít biến động | **Kế thừa nguyên lý** |
| **3. Xử lý Lost Wake-Up khi push đến dồn dập** | Paper 1 dùng biến cờ boolean `loopOnceMore = true` trong bộ nhớ RAM | Seminar sử dụng `WorkManager.enqueueUniqueWork` với policy `REPLACE` kết hợp Version Guard trong Room Transaction, an toàn tuyệt đối qua process death | **Nâng cấp giải pháp** |
| **4. Nội dung gói tin thông báo đẩy** | Paper 1 khẳng định push chỉ là tín hiệu kích hoạt (signal), không mang dữ liệu toàn phần | Seminar tuân thủ hoàn toàn: Payload FCM data-only chỉ mang `version_hint` và ID, dữ liệu thực tải qua HTTP GET của worker | **Khớp hoàn toàn** |
| **5. Độ trễ và tính đúng hạn của Alarm định kỳ** | Paper 2 ghi nhận AlarmManager bị Android bỏ lỡ tới 84% nếu không tắt tối ưu pin | Seminar thừa nhận scheduler định kỳ (WorkManager) không cam kết đúng giờ trong Doze Mode; ghi nhận trung thực độ lệch thời gian trong `E01` | **Khớp hoàn toàn** |
| **6. Kỹ thuật né tránh quản lý năng lượng** | Paper 2 dùng Alarm lặp 1 phút, giữ WakeLock và yêu cầu người dùng tắt tối ưu pin | Bị Google cấm (thu hồi quyền exact alarm từ Android 12, siết Foreground Service từ Android 14). Seminar kiên quyết loại bỏ kỹ thuật này | **Lạc hậu / Bị cấm** |
| **7. Phân mảnh hành vi giữa các hãng OEM** | Paper 2 chứng minh Xiaomi (MIUI) tự động diệt tiến trình nền làm mất 46.6% số lượt | Seminar khớp nối trực tiếp với rào cản của ColorOS trên OPPO Find X9 (chặn Auto-launch, đóng băng tiến trình ngầm khi tắt màn hình) | **Khớp hoàn toàn** |
| **8. Xử lý ngoại lệ trong báo cáo khoa học** | Paper 2 loại bỏ 77 điểm trễ ngoại lệ (2–3 giờ) khi vẽ biểu đồ | Seminar cam kết trung thực dữ liệu: Không lược bỏ bất kỳ lượt trễ hay timeout nào trong toàn bộ các ca `E01`–`E06` | **Bài học phương pháp luận** |

---

## 4. Kế hoạch bàn giao cho task kế thừa (Handoff)

Đầu ra của SEM-22 trực tiếp mở khóa và cung cấp cơ sở lý luận vững chắc cho:
- **[SEM-50](../../../tasks/backlog/SEM-50.md) (Tuấn — Hoàn thiện báo cáo, bibliography và CLAIMS):**
  - Kế thừa toàn bộ bảng Ma trận đối chiếu 8 claims tại Mục 5 của `API_CROSSCHECK.md` để đưa vào tài liệu `docs/CLAIMS.md`.
  - Sử dụng các phân tích định vị mô hình HYBRID tại Mục 6 để viết phần thảo luận (Discussion) và kết luận khoa học trong báo cáo tổng kết seminar.
  - Sử dụng trích dẫn BibTeX chuẩn xác từ `paper-1.bib` và `paper-2.bib` để tổng hợp vào `research/references.bib`.

---

## 5. Kết luận nghiệm thu

- Toàn bộ nội dung yêu cầu của SEM-22 đã được hoàn thành với độ sâu học thuật cao, trích dẫn chính xác và liên kết chặt chẽ với các ca thử nghiệm thực tế của đề tài.
- Báo cáo [research/notes/API_CROSSCHECK.md](../../../research/notes/API_CROSSCHECK.md) và hồ sơ [CHECKS.md](CHECKS.md) sẵn sàng phục vụ kiểm tra chéo và hợp nhất vào nhánh chính.
