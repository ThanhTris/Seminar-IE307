# SEM-39 Core cases

Các case dưới là tiêu chí cần chạy trên runtime/build candidate. Không có kết quả chạy được giả lập trong tài liệu này.

| Case | Input | Expected/assertion | Actual | Trạng thái |
|---|---|---|---|---|
| Version mới | Cache v4, response v5 | Transaction thay snapshot, cachedVersion=5, một applied event | Chưa chạy | Not run |
| Version bằng | Cache v5, response v5 | Items không bị ghi lại; unchanged; cache vẫn v5 | Chưa chạy | Not run |
| Response cũ | Cache v5, response v4 | Stale; cache không giảm | Chưa chạy | Not run |
| Empty snapshot | Cache metadata v0 và bảng items rỗng, response v1 | So version từ metadata; apply v1 | Chưa chạy | Not run |
| Trigger trùng/race | Hai worker nhận response v6 và v7; v7 commit trước | Transaction đọc version mới nhất; không ghi đè v7 bằng v6 | Chưa chạy | Not run |
| Retry transient | Timeout/5xx liên tiếp | Cùng worker dùng retry hữu hạn; tối đa 3 retries, sau đó sync_failed/RETRY_EXHAUSTED | Chưa chạy | Not run |
| Lỗi permanent | HTTP 4xx hoặc payload không hợp lệ | Không retry tự động vô hạn; failure | Chưa chạy | Not run |

`SyncRepository` kiểm version trong transaction sau fetch, nên response đến muộn không thể hạ version đã commit. Đây là phân tích code, chưa xác nhận race bằng chạy đồng thời. `SyncWorker` sử dụng `runAttemptCount`; semantics retry phải được xác nhận trên WorkManager 2.12.0 khi có build/device.
