# SEM-07 — Tích hợp hybrid và tính đúng của đồng bộ

- Status: backlog
- Lịch mục tiêu: 04–05/11/2026
- Công sức: 10/100 — Thực hành
- Owner/reviewer: chưa phân công
- Điều kiện bắt đầu: SEM-05, SEM-06 đã có đầu ra cần dùng
- Điều kiện hoàn tất bổ sung: không ngoài điều kiện bắt đầu

## Đầu vào

Hai trigger chạy độc lập, repository/schema chung và dữ liệu pilot.

## Việc cần làm

1. Bật mode HYBRID và làm sạch lịch khi chuyển mode; worker còn chạy phải kết thúc hoặc đánh dấu ca bị nhiễu.
2. Dùng transaction/version guard để không áp dụng snapshot cũ hoặc ghi trùng.
3. Xử lý tín hiệu đến trong lúc worker đang kết thúc; chọn cơ chế queue/coalesce có ca test race.
4. Định nghĩa retry/backoff hữu hạn cho lỗi transient; lỗi permanent trả failure có lý do.
5. Thêm khả năng cập nhật server mà bỏ gửi push có chủ ý để thử periodic phục hồi.

## Đầu ra bắt buộc

- android/ và server/ — ba mode, đồng bộ an toàn khi cạnh tranh, retry và fault injection có nhãn.
- docs/SYNC.md — quy tắc version, concurrency, mode transition, retry và giới hạn phục hồi.
- Test logic cho snapshot cũ, trigger trùng, trigger đến khi sync đang chạy và lỗi mạng.
- docs/evidence/SEM-07/CHECKS.md — commit, môi trường, bước kiểm tra, expected/actual, link bằng chứng, hạn chế và phần bàn giao.

## Tiêu chí nghiệm thu

- [ ] Các test logic quan trọng pass; không viết test chỉ kiểm tra tên hàm hoặc scaffold.
- [ ] E05 pilot không giảm version/ghi trùng, không bỏ mất version mới ở race.
- [ ] E06 pilot thể hiện cập nhật từ PERIODIC khi cố ý không gửi push; không gọi là vượt Doze/force-stop.
- [ ] Có đủ đầu ra và CHECKS.md; người làm giải thích được kết quả, reviewer hoặc người thực hiện tự review được ghi rõ.

## Trạng thái bàn giao

Chưa thực hiện. Tên file ở trên là đầu ra phải tạo khi làm task, không phải bằng chứng đã tồn tại. Cập nhật task và task board cùng lúc khi đổi trạng thái.
