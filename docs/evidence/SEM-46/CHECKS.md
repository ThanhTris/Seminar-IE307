# WIP — SEM-46 chưa hoàn thành, chưa đủ điều kiện merge

- Người soạn Tuấn (`mtuan2491`), ngày 09/11/2026 theo yêu cầu thực hiện SEM-46 của người dùng.
- Nhánh `codex/SEM-46-opening-demo` tạo riêng từ main `54d48c2ed48588b59b16cc652a8d1b77912c15b7`.
- Người nói mở bài và thao tác thiết bị là Trí theo PRESENTATION_PLAN. Việc soạn của Tuấn và vai nói của Trí được ghi riêng để người nhận dùng đúng file TRI.md.
- Trạng thái tổng thể **CHƯA HOÀN THÀNH, CHỜ SEM-37**. Candidate manifest, candidate gate và CHECKS đang chờ bàn giao. Nhóm trưởng chỉ review phần chuẩn bị, chờ cập nhật hoàn tất trước khi merge task.

## Ba bước thực hiện

| Bước | Đầu ra | Trạng thái |
|---|---|---|
| 1. Soạn mở bài và mốc cơ chế | TRI.md có ngân sách 45 giây, câu chuyển người và mốc trigger-to-cache | **Hoàn tất phần soạn, `acf341e`** |
| 2. Soạn khung thao tác và phương án dự phòng | Setup/mode/reset, lịch demo 4 phút, nhãn live/playback, bảng chờ candidate và kiểm bàn giao | **Hoàn tất phần dự thảo độc lập, commit bước 2** |
| 3. Chốt trên candidate thật | Nhận SEM-37, điền commit/APK/config/công cụ thật, kiểm live/playback rồi chốt input cho SEM-51 | **Chờ SEM-37, Not run** |

Mỗi bước thực hiện xong được commit riêng. Dùng `git log --oneline -- docs/evidence/SEM-46/CHECKS.md` để truy các commit.

## Nguồn đã đọc

| Nguồn | Artifact / kiểm chứng | Cách dùng |
|---|---|---|
| SEM-14, Done | [SHARED_SYNC](../../mechanisms/SHARED_SYNC.md), [CHECKS](../SEM-14/CHECKS.md) | Luồng trigger, worker, repository, Room và UI |
| Kế hoạch | [SCOPE](../../SCOPE.md), [PRESENTATION_PLAN](../../PRESENTATION_PLAN.md) | Mở bài 45 giây, demo 4 phút, Trí thao tác và Trang dẫn |
| SEM-19 | [MECHANISMS](../../MECHANISMS.md), [QUESTIONS](../../QUESTIONS.md) | Cách diễn giải event, giới hạn và nguồn |
| SEM-37, Todo tại main nền | [Yêu cầu candidate](../../../tasks/backlog/SEM-37.md) | Đang chờ `release/CANDIDATE_MANIFEST.json`, CANDIDATE_GATE và CHECKS |

## Kiểm chứng bước 1

| Check | Expected | Actual | Kết quả |
|---|---|---|---|
| Scope và câu mở | Bám bảng tin nền, shared core và version/cache | Lời dẫn đặt câu hỏi trigger-to-cache, bảng event tách accepted/received/enqueued/started/applied | Đã review nội dung |
| Phân vai và thời lượng | Theo khung mở bài hiện hành | Trí nói 40 giây dự kiến, 5 giây chuyển Trung trong tổng 45 giây | Pass cho kế hoạch, chưa bấm giờ |
| Candidate/runtime | Chốt sau khi nhận build/config thật | Đang chờ SEM-37 | **Not run** |

Artifact đang soạn là [TRI.md](../../../slides/inputs/TRI.md). Kiểm tĩnh bước 1 đạt 14 link nội bộ trong 2 file, nhãn WIP và whitespace hợp lệ. Ngân sách mở bài cộng chuyển người bằng 45 giây.

## Kiểm chứng bước 2 và bàn giao bản làm trước

| Check | Expected | Actual | Kết quả |
|---|---|---|---|
| Thao tác / mode / reset | Có trình tự để đối chiếu candidate | Phiếu pin build/config/công cụ đang chờ, setup MANUAL ngoài window, run mới, drain và Home trước live | Pass cho dự thảo tài liệu |
| Live / playback | Có nhãn, mốc chuyển và metadata | Khung 30+30+30+60+60+30 = 240 giây, chuyển playback sau 30 giây từ send, bảng câu dẫn theo event | Pass cho kế hoạch, chưa diễn tập |
| Phân vai / chuyển người | Khớp kế hoạch toàn bài | Trí thao tác, Trang dẫn demo, chuyển Vinh ở cuối 4 phút | Pass cho đối chiếu tài liệu |
| Candidate và thực hiện thiết bị | Được kiểm trên candidate thật khi nhận | Manifest/gate/CHECKS SEM-37 còn chờ, các trường pin được ghi CHỜ | **Not run** |
| Kiểm file và liên kết | Bản draft đọc được, các link nguồn có thật | 3 file, 30 link nội bộ và 11 bảng đạt kiểm cấu trúc/whitespace, ngân sách mở bài 45 giây và demo 240 giây | Pass cho kiểm tĩnh |

SEM-51 có thể nhận bản này để chuẩn bị bố cục và notes. Trước merge SEM-46 cần chốt bước 3 cùng candidate thật và cập nhật CHECKS. Status tổng thể vẫn WIP, đang chờ SEM-37.
