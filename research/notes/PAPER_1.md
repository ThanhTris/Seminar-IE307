# PAPER_1 - Đồng bộ theo thay đổi và chi phí của chu kỳ rỗng

Tuấn (`mtuan2491`), đọc ngày **03/11/2026 (UTC+7)**. Đây là **phần nghiên cứu độc lập của SEM-20**, chưa phải kết quả thực nghiệm của seminar. Số liệu bên dưới thuộc bài gốc; các liên hệ với demo được ghi riêng là đề xuất của người đọc.

## 1. Bài được chọn và metadata đã xác minh

| Trường | Giá trị |
|---|---|
| Tên | Analysis of Differential Synchronisation's Energy Consumption on Mobile Devices |
| Tác giả | Jörg Simon; Peter Schmidt; Viktoria Pammer-Schindler |
| Tạp chí | EAI Endorsed Transactions on Collaborative Computing |
| Xuất bản | 30/06/2017; volume 3, issue 11, article e2; PDF 9 trang |
| DOI bản xuất bản | `10.4108/eai.30-6-2017.152756` |
| Citation key | `Simon2017DiffsyncEnergy` |
| Metadata riêng | [paper-1.bib](../metadata/paper-1.bib) |

Nguồn gốc: [trang nhà xuất bản EUDL](https://eudl.eu/doi/10.4108/eai.30-6-2017.152756), [PDF bản xuất bản](https://eudl.eu/pdf/10.4108/eai.30-6-2017.152756), [record Crossref](https://api.crossref.org/works/10.4108%2Feai.30-6-2017.152756). Tên tác giả có dấu lấy từ trang đầu PDF; metadata Crossref/nhà xuất bản có chỗ dùng `Jorg`.

Có [preprint arXiv 1601.01539v1](https://arxiv.org/abs/1601.01539v1), nộp 07/01/2016. Đây là bản tác giả của cùng nghiên cứu, **không tính là bài thứ hai** và không lấy năm 2016 thay năm xuất bản 2017. Volume 3 lấy từ BibTeX nhà xuất bản, Crossref và footer PDF; không lấy chuỗi hiển thị `cc 17 (11)` làm volume 17. Trường `page=152756` trong Crossref là dữ liệu đăng ký, không được biến thành khoảng trang; BibTeX dùng article `e2`.

## 2. Vì sao chọn cho seminar này?

Bài bàn trực tiếp về việc kích hoạt đồng bộ theo thay đổi thay vì thực hiện đều đặn cả khi không có thay đổi. Đó là cơ sở để đặt câu hỏi về lượng công việc của polling/push, cũng như bảo toàn tín hiệu mới đến khi sync đang chạy. Hai hướng này phù hợp chủ đề của [SEM-20](../../tasks/backlog/SEM-20.md) mà không cần chờ APK, backend hoặc log của thành viên khác.

Giới hạn lựa chọn: đây là nghiên cứu về **differential synchronisation trong cộng tác chỉnh sửa**, không phải benchmark WorkManager/FCM trên Android. Demo bảng tin dùng snapshot/version, không được gọi là hiện thực diffsync hoặc bản tái lập Mendeley. Bài còn lại của nhóm nên bổ sung scheduling/giới hạn OS hoặc bằng chứng trên nền tảng mới; đây là gợi ý lựa chọn, chưa quyết định thay SEM-21.

## 3. Câu hỏi nghiên cứu và cơ chế đề xuất

Tác giả khảo sát chi phí của diffsync khi chu kỳ rỗng, interval và độ phức tạp thay đổi khác nhau, rồi đề xuất kích hoạt sync lúc khởi tạo/kết nối, có sửa đổi local hoặc nhận thông báo server. Một push chỉ yêu cầu chạy chu kỳ đồng bộ; nó không tự thay dữ liệu đã đồng bộ. Nguồn: mục 4-6, trang 3-7 của [bản xuất bản](https://eudl.eu/pdf/10.4108/eai.30-6-2017.152756).

Trong triển khai Mendeley, tác giả chỉ cho một cycle chạy tại một thời điểm; tín hiệu đến trong cycle đặt cờ `loopOnceMore` để chạy thêm. Đây là ý tưởng để thảo luận vấn đề lost wake-up, không phải một chứng minh rằng chép một biến boolean là đủ an toàn trong hệ thống worker đa luồng của nhóm. Nguồn: mục 7.1, trang 7.

## 4. Phương pháp và môi trường của bài

| Hạng mục | Bài thực sự sử dụng | Điều cần chú ý khi đọc |
|---|---|---|
| Bối cảnh | Annotation PDF cộng tác trong Mendeley iOS; server action mô phỏng dựa trên usage data | Không phải đo ứng dụng Android chạy nền. |
| Thiết bị | Một iPhone 5s cài mới iOS 7 | Một thiết bị, không phải mẫu đa OEM. |
| Mạng | GSM, 3G, WLAN; khảo sát các interval 0-60 giây trong thiết kế của bài | Interval giây của diffsync khác scheduler nền của demo. |
| Công cụ | Software battery monitor, API báo mức pin theo bước 1%; chạy đến khi hao 20% cho các thí nghiệm liên quan | Đơn vị báo cáo là `%/min`, không phải phép đo Joule hoặc mAh trực tiếp. |
| Dữ liệu runner | Hơn 60.000 cycle, khoảng 1.000 cycle/experiment | Khác tập server log được dùng tính tỷ lệ empty cycle. |
| Dữ liệu sử dụng | Usage data bốn tuần trong tháng 05/2014; phân tích 100.000 cycle từ server log | Không diễn giải 100.000 là số người dùng, cũng không gộp vào runner thành một cỡ mẫu duy nhất. |

Nguồn: mục 5.4, trang 4-6 và mục 7.2, trang 7-8. Đã đọc cả phần kết luận và tài liệu tham khảo; không chỉ dựa abstract. [PDF bản xuất bản](https://eudl.eu/pdf/10.4108/eai.30-6-2017.152756).

## 5. Kết quả gốc và loại bằng chứng

| Phát hiện được ghi trong bài | Vị trí | Cách hiểu đúng |
|---|---|---|
| 96.792/100.000 cycle rỗng, xấp xỉ 96,8% | Mục 7.2, trang 8 | Thống kê server log của workload Mendeley; không phải tỷ lệ của PERIODIC trong demo. |
| Cycle rỗng ở cấu hình thí nghiệm được báo 0,22%/min; worst-case trên item khoảng 7.000 byte là 0,34%/min | Mục 5.4, trang 5 | Hai số đo cấu hình cụ thể trên thiết bị bài dùng; không chuyển sang mAh hay pin OPPO. |
| Ví dụ phiên 7 phút trên 3G: bản gốc 1,729% pin, push-based 0,084% | Mục 7.3, trang 8 | Tác giả định lượng từ mức tiêu thụ và giả định usage/cycle rỗng; không phải A/B trial trên nhóm người dùng Android hiện tại. |

Các số trên chỉ phục vụ kiểm tra việc đọc bài, **không nhập vào `experiments/results.csv`** của nhóm. Không lấy chúng để khẳng định một phần trăm tiết kiệm pin cho seminar. Bài cũng nêu overhead của nhận push khi thay đổi liên tục; vì vậy không rút ra mệnh đề “push luôn tốt hơn polling”. Nguồn: mục 6, trang 6-7 và mục 7.3, trang 8.

## 6. Phản biện và giới hạn áp dụng

Đây là nhận xét của người đọc dựa trên phương pháp nêu trong bài:

- Một thiết bị, OS và mạng đời cũ không đủ xác nhận hành vi trên thiết bị Android/ColorOS hoặc mạng hiện đại. Phần khái quát hóa của tác giả ở trang 6 là lập luận của bài, không phải run Android mới.
- Battery level theo bước 1% có độ phân giải thô. Không suy “hai cấu hình hoàn toàn tương đương” từ trường hợp phần mềm không đo thấy chênh lệch, và không đổi số đo sang năng lượng tuyệt đối nếu thiếu phép đo phù hợp.
- Server action mô phỏng và phân tích usage data cần phân biệt với thí nghiệm triển khai end-to-end ngoài thực tế. Các số ở mục 7.3 phụ thuộc giả định về workload và kết nối.
- Trong Mendeley, diffsync được bật khi mở PDF và tắt khi đóng PDF (mục 7.1). Bối cảnh đó không chứng minh silent push đánh thức app hay được OS cấp thời gian chạy trong ca background/Doze của nhóm.
- Đề nghị interval khoảng 6 giây và quan sát notification dưới 2 giây trong bài là kết quả theo bối cảnh của tác giả. Không dùng chúng làm interval WorkManager hay quy tắc FCM bắt buộc cho mọi thiết bị.
- Snapshot/version của bảng tin và diff/patch hai chiều với shadow copy giải quyết các bài toán khác nhau. Chỉ chuyển giao ý tưởng kích hoạt/bảo toàn tín hiệu và cách đặt giả thuyết; không chuyển giao nguyên bảo đảm hội tụ.

## 7. Liên hệ thiết kế và case đề xuất cho demo

**Các dòng sau là đề xuất của Tuấn cho seminar, chưa phải kết quả của bài hoặc phép đo nhóm đã chạy.** Case ID tham chiếu [thiết kế kiểm thử hiện có](../../docs/EXPERIMENT_PROTOCOL.md); không thêm ca bắt buộc hoặc thay scope của owner khác.

| ID đề xuất | Ý tưởng có thể dùng | Case / quyết định liên quan | Evidence cần có sau này |
|---|---|---|---|
| P1-H1 | Quan sát phần công việc không tạo snapshot mới khi server ít đổi | E01/E02; đếm GET và applied/unchanged theo từng mode | Run hợp lệ, source/version, số GET đã instrument và cấu hình update; không dùng dữ liệu hai ca thiếu kiểm soát để kết luận hơn kém. |
| P1-H2 | Giữ cập nhật mới đến lúc một worker đang chạy hoặc kết thúc | E05-C; shared core và race handling | Tạo overlap có chứng cứ, target version cuối, test logic và event đúng request; cờ minh họa trong paper không thay test. |
| P1-H3 | Tách tín hiệu yêu cầu sync với dữ liệu đã áp dụng | E02/E04; event received/start/applied riêng | Log có correlation, cache commit trước mở UI; không chỉ dùng accepted. |
| P1-H4 | Thảo luận đánh đổi lượng công việc và độ mới dữ liệu | E01/E02/E06; periodic/push/hybrid | Giữ các cửa sổ, phase, build và trigger rõ ràng; không lấy E01/E02 hiện có làm phép so latency ngang điều kiện. |

P1-H1 chỉ là hướng quan sát lượng công việc, không phải benchmark pin. P1-H2 là liên hệ trực tiếp nhất với quyết định không bỏ tín hiệu khi worker bận; đây là phần có thể dùng trong lập luận dù chưa nhận số liệu thực nghiệm.

## 8. Phần đã làm và phần bổ sung sau

Đã làm độc lập: chọn bài, đọc toàn văn bản xuất bản qua nguồn nhà xuất bản, kiểm metadata bằng Crossref, ghi phương pháp/kết quả/giới hạn, tạo BibTeX riêng và đề xuất claim/case. Không cần nhận runtime output từ SEM-21/22 hoặc các task code để thực hiện phần này.

Bổ sung ở bước chốt: đối chiếu các đề xuất với đúng artifact/config thiết bị và bản demo được bàn giao; nhận kết quả API cross-check của SEM-22 khi có và dẫn run thật nếu dùng trong báo cáo. Không chờ các phần đó để viết ghi chú đọc bài, cũng không coi việc chưa có run là lỗi của một task nghiên cứu. Không sửa bibliography tổng, CLAIMS, báo cáo hoặc bài thứ hai trong nhánh này.

## 9. Quyền truy cập và phiên bản đã đọc

Trang EUDL và trang đầu bản xuất bản ghi **CC BY 3.0**, tác giả Simon et al., 2017. Chỉ commit ghi chú/BibTeX, giữ link tới bản gốc. Không sao chép PDF hoặc hình của bài vào repo trong bước này.

Đường tải EUDL trực tiếp bằng CLI trả HTTP 403; bản xuất bản 9 trang vẫn đọc được qua liên kết Download và nội dung PDF trong công cụ duyệt web. Bản preprint v1 được tải vào `.local/sem20/` và render trang 5/8 để hỗ trợ kiểm bố cục; đó không phải file final publisher đã tải thành công. Metadata và các vị trí trang/kết quả ở trên được đối chiếu lại với **bản xuất bản**, không gán DOI 2017 cho file preprint. Xem [CHECKS](../../docs/evidence/SEM-20/CHECKS.md) để phân biệt nguồn và loại kiểm tra.
