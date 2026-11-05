# SEM-21 — Bài 2: Lập lịch tác vụ nền Android

## Nguồn và lý do chọn

Alberto González-Pérez, Miguel Matey-Sanz, Carlos Granell và Sven Casteleyn, “Using mobile devices as scientific measurement instruments: Reliable android task scheduling”, *Pervasive and Mobile Computing*, tập 81, bài 101550, tháng 4/2022. [DOI: 10.1016/j.pmcj.2022.101550](https://doi.org/10.1016/j.pmcj.2022.101550); [trang nhà xuất bản](https://www.sciencedirect.com/science/article/pii/S1574119222000074); [hồ sơ kho Đại học Jaume I](https://repositori.uji.es/handle/10234/196827); [toàn văn PDF tại kho trường](https://repositori.uji.es/bitstreams/369ca302-bfdc-4c69-901d-30b374277ba9/download). PDF 19 trang ghi xuất bản trực tuyến ngày 29/01/2022 và giấy phép CC BY 4.0. Metadata trích dẫn riêng: [paper-2.bib](../metadata/paper-2.bib). [Crossref](https://api.crossref.org/works/10.1016%2Fj.pmcj.2022.101550) ghi kỳ tháng 4/2022; 101550 là mã bài, không phải số trang. Đối chiếu ngày 04/11/2026.

Bài phù hợp vì kiểm tra tính đầy đủ và thời điểm chạy tác vụ nền Android trên nhiều thiết bị, có số liệu gốc, môi trường và giới hạn rõ; nó hỗ trợ lập luận rằng lịch dự kiến cần được đối chiếu với thực tế. Đây không phải nghiên cứu đồng bộ snapshot hay FCM. Bản nghiên cứu bài 1 đang có trên [nhánh SEM-20](https://github.com/ThanhTris/Seminar-IE307/blob/bb12ee63ebfca2136c6f3a4602ecfb7d25c6a56d/research/notes/PAPER_1.md) khảo sát đồng bộ vi sai và năng lượng trên iOS; bài Android này bổ sung góc độ lập lịch. SEM-20 chưa được xác nhận bàn giao/Done tại thời điểm đối chiếu, nên lựa chọn bài 1 còn có thể thay đổi.

## Câu hỏi và phương pháp của tác giả

- Mục tiêu: thu thập dữ liệu khoa học định kỳ đáng tin cậy trên thiết bị Android, đánh giá tính đầy đủ, độ chính xác thời gian và mức dùng pin (§1, §4).
- Tác giả mô tả cách dùng AlarmManager, broadcast receiver, wake lock và thư viện NativeScript Task Dispatcher (NTD), trong đó có watchdog; có các bước cấu hình tiết kiệm pin/khởi động tùy thiết bị (§2–3). Đây là thiết kế của bài, **không phải thiết kế được phép sao chép vào demo**: [SCOPE](../../docs/SCOPE.md) chọn WorkManager/FCM, loại scheduler riêng, foreground service và alarm để né chính sách.
- **Thí nghiệm 0** (§4.1, bảng 1–2, tr. 13): alarm lặp mỗi phút trong 48 giờ trên Nvidia Shield Tablet Android 7, BQ Aquaris V Plus Android 8.1, Xiaomi Mi A1 và Honor 9 Android 9. Phần §4.1 nói không tắt tiết kiệm pin ở thí nghiệm này; phần mở đầu §4 lại mô tả chung là tắt tiết kiệm pin. Cần giữ ngoại lệ và bất nhất này khi diễn giải.
- **Thí nghiệm 1** (§4.2, hình 4 và bảng 3, tr. 13–15): hai ứng dụng chạy tác vụ đơn giản mỗi phút trong hai tuần trên bốn thiết bị trên: app Java ad-hoc không có watchdog và app NativeScript dùng NTD có watchdog. Tác giả lưu timestamp vào CSV; completeness là phần trăm lượt thực hiện thiếu so với số dự kiến. Chỉ số delay trong hình 4 là khoảng giữa hai lần chạy liên tiếp trừ 60 giây, **khác** độ trễ từ alarm đến bắt đầu tác vụ trong bảng 3. Đây cũng không tự đồng nhất với khoảng enqueue → worker start hoặc server update → cache applied của demo.
- **Thí nghiệm 2** (§4.3, bảng 4, tr. 16–17): dữ liệu ghi trên BQ khoảng 45 phút được làm sạch/chuẩn hóa rồi phát lại trong mô phỏng đồ thị tác vụ trị liệu; mỗi máy thực hiện 470 lượt trong hai tuần. Các máy là Nvidia, BQ, Honor 9 và Poco F2 Pro Android 11. Đây không phải thử nghiệm lâm sàng trên 470 bệnh nhân.
- Tác giả chia sẻ [mã và dữ liệu tái lập trên Zenodo](https://zenodo.org/records/5032028) (DOI `10.5281/zenodo.5032028`, khác DOI bài báo). SEM-21 chỉ đọc và đối chiếu, chưa chạy lại gói này.

## Kết quả gốc cần đọc cùng điều kiện

| Quan sát của bài | Giới hạn diễn giải |
|---|---|
| Thí nghiệm 0: số lượt thiếu trên bốn máy là 88,24%, 94,45%, 59,67% và 93,72%; trung bình khoảng 84% (bảng 2). | Alarm mỗi phút trong 48 giờ, trong điều kiện §4.1 mô tả; không phải tỷ lệ mất của WorkManager hay FCM. |
| Thí nghiệm 1: NTD thiếu 0,39–1,24% lượt tùy máy; app ad-hoc dừng sớm trên Nvidia và Xiaomi, tương ứng khoảng 82,59% và 46,66% lượt thiếu theo phần văn bản (§4.2). | Không suy NTD luôn tốt hơn trên mọi thiết bị. Hình 4 ghi Xiaomi 46,55%, khác 46,66% trong văn bản; báo rõ bất nhất. Với hai app dừng sớm, phân bố thời gian chỉ có dữ liệu trước khi dừng. |
| Tác giả thu 138.653 giá trị; hình 4 bỏ 77 ngoại lệ để dễ đọc, gồm một khoảng hơn 3 giờ và một khoảng gần 2 giờ. | Không dùng hình đã lược ngoại lệ làm bằng chứng mọi lượt đều gần đúng hạn. |
| Trên BQ và Honor 9 gộp, trung vị từ alarm đến bắt đầu tác vụ là 45 ms với ad-hoc và 84 ms với NTD, chênh 39 ms (bảng 3). | Hai ứng dụng hoàn tất trên hai máy này; đây không phải độ trễ end-to-end của sync và không ngoại suy sang thiết bị khác. |
| Trong mô phỏng, tỷ lệ thiếu sự kiện `exposureFinished` là 1,70%, 2,13%, 0,42% và 9,36% tương ứng Nvidia, BQ, Honor và Poco (bảng 4). | Đây là sự kiện trong workload mô phỏng, không phải tỷ lệ mất dữ liệu FCM. Tác giả nêu phiên bản OS và việc dùng máy cá nhân là những khả năng giải thích, chưa chứng minh quan hệ nhân quả. |

Tác giả còn so sánh mức giảm phần trăm pin theo giờ trên BQ khi chạy hai ứng dụng riêng (§4.2, hình 5). Phép đo này bao gồm hoạt động hệ điều hành và chỉ dựa trên một máy trong so sánh đó; [phạm vi nhóm](../../docs/SCOPE.md) không có benchmark pin, nên không chuyển các giá trị thành kết quả hay cam kết tiết kiệm pin của demo.

## Giới hạn và liên hệ project

- Bài kiểm tra các thiết bị Android 7–11 trong các bảng kết quả; phần thiết kế đề cập nhiều phiên bản Android hơn. Không có OPPO/ColorOS trong mẫu. Không khái quát số liệu sang Android 17 hay chính sách OEM hiện nay.
- Cơ chế alarm/NTD, chu kỳ một phút, workload, cách lấy mẫu và miễn trừ pin khác WorkManager của demo. Những kết quả này là động lực thiết kế phép đo, không phải dự báo định lượng cho demo.
- [SEM-11](../../docs/evidence/SEM-11/CHECKS.md) chốt phạm vi/build; [SEM-12](../../docs/evidence/SEM-12/CHECKS.md) ghi emulator Android 17/API 37 đã kiểm cấu hình, chưa có OPPO để kiểm và chưa kiểm nhận FCM thật. Các case dưới đây là **giả thuyết/kế hoạch, chưa phải kết quả SEM-21**.
- Khi diễn giải hành vi WorkManager/Doze hiện tại, đối chiếu [tài liệu WorkManager](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work) và [Doze](https://developer.android.com/training/monitoring-device-state/doze-standby), cùng version, trạng thái và log thật của mỗi run. Không lấy mô tả hệ điều hành năm 2022 làm kết luận cho mọi phiên bản.

## Giả thuyết và case đề xuất cho nhóm

Theo [protocol hiện hành](../../docs/EXPERIMENT_PROTOCOL.md), giữ nguyên số lượt/cửa sổ và không ép chạy để tạo kết quả:

1. **H1 — E01 periodic:** lịch đã đăng ký không đảm bảo thời điểm worker chạy chính xác; quan sát lần chạy tự nhiên, khoảng thời gian thực, trigger và version/cache, ghi cả lượt thiếu trong phiên 90 phút/máy. Không xem công thức khoảng giữa hai lần chạy của bài là độ trễ end-to-end.
2. **H2 — E03 Doze:** trạng thái hệ thống có thể ảnh hưởng thời điểm nhận/chạy; xác nhận trạng thái Doze, ghi sự kiện trước/trong/sau và tách periodic/push theo protocol. Hai lượt mỗi trigger chỉ cho quan sát có điều kiện, không đủ khẳng định quy luật chung.
3. **H3 — E04 mất mạng:** có thể quan sát sự khác nhau giữa tín hiệu, thời điểm chạy và áp dụng snapshot sau khi mạng trở lại. Đây là mở rộng từ nhu cầu phân biệt các mốc, **không phải kết quả mạng của bài**; ghi cấu hình, cửa sổ và các lượt không hoàn tất.
4. **H4 — E01/E03 đối chiếu thiết bị:** ghi Android/API, OEM, cấu hình tiết kiệm pin và lifecycle thật; không mặc định emulator đại diện OPPO. Chỉ so sánh khi có log thực và nêu giới hạn số mẫu.

Bàn giao nội dung nguồn và các giới hạn cho SEM-22, SEM-49, SEM-50; việc chốt claim, đối chiếu API và chạy thực nghiệm thuộc các task tương ứng.
