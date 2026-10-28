# SEM-03 — Đọc hai nghiên cứu và lập bảng lập luận

- Status: backlog
- Lịch mục tiêu: 29/10–01/11/2026
- Công sức: 10/100 — Nghiên cứu
- Owner/reviewer: chưa phân công
- Điều kiện bắt đầu: có thể chuẩn bị từ kế hoạch đã chốt
- Điều kiện hoàn tất bổ sung: SEM-01 đã bàn giao

## Đầu vào

Phạm vi Android đã xác nhận, các câu hỏi trong PLAN và protocol; bổ sung cơ chế từ SEM-02 khi có.

## Việc cần làm

1. Tìm và chọn 2 nghiên cứu phù hợp về scheduling/push-polling/đồng bộ mobile; đọc phương pháp và giới hạn, không chỉ abstract.
2. Ghi tác giả, năm, DOI/URL, môi trường thử, kết luận và điều có thể/không thể áp dụng cho demo.
3. Gắn từng nguồn với giả thuyết hoặc quyết định thí nghiệm; documentation và bài nghiên cứu là hai loại nguồn riêng.
4. Lưu PDF khi có bản được phép chia sẻ; nếu không, lưu metadata/link và ghi chú, không bắt buộc có PDF trong repo.

## Đầu ra bắt buộc

- research/notes/<paper-id>.md — 2 ghi chú, mỗi ghi chú có phương pháp, kết quả trong bối cảnh gốc, hạn chế và liên hệ demo.
- research/references.bib — metadata kiểm chứng cho các bài được sử dụng.
- docs/CLAIMS.md — bảng claim → nguồn/vị trí → case_id → evidence còn thiếu → trạng thái giả thuyết.
- docs/evidence/SEM-03/CHECKS.md — commit, môi trường, bước kiểm tra, expected/actual, link bằng chứng, hạn chế và phần bàn giao.

## Tiêu chí nghiệm thu

- [ ] DOI/URL, tên và tác giả khớp bản gốc; nguồn không liên quan phải bị loại.
- [ ] Ít nhất một lập luận ảnh hưởng trực tiếp cách thử hoặc giải thích trade-off; không nhét paper chỉ để tăng số trích dẫn.
- [ ] Không dùng kết quả nghiên cứu cũ làm số đo trên OPPO; giữ công sức nghiên cứu trong 20%.
- [ ] Có đủ đầu ra và CHECKS.md; người làm giải thích được kết quả, reviewer hoặc người thực hiện tự review được ghi rõ.

## Trạng thái bàn giao

Chưa thực hiện. Tên file ở trên là đầu ra phải tạo khi làm task, không phải bằng chứng đã tồn tại. Cập nhật task và task board cùng lúc khi đổi trạng thái.
