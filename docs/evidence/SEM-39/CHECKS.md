# SEM-39 CHECKS — Core robustness

## Đầu ra

- Version guard/equal-version handling/bounded retry: Android sync core.
- Case matrix: [CORE_CASES.md](CORE_CASES.md).

| Hạng mục | Expected | Actual | Trạng thái |
|---|---|---|---|
| Cache monotonicity | Apply chỉ khi server version cao hơn cache đọc trong transaction | Code path reviewed; lower/equal branches không thay snapshot | Pass (code review) |
| Idempotence | Version bằng không ghi lại snapshot | Nhánh `snapshot_unchanged` | Pass (code review) |
| Transient retry bound | Dừng sau 3 lượt retry | Guard bằng `runAttemptCount < MAX_RETRY_COUNT` | Pass (code review) |
| Concurrent race | Late stale response không hạ version | Transactional compare after fetch | Pass (code review) |
| Executable logic/build checks | Runtime assertions pass | Chưa build hoặc chạy checks | Not run |

Commit/config: working tree hiện tại; WorkManager 2.12.0, Room 2.8.5; build chưa chạy. Blocker: cần build candidate và luồng test tích hợp; không thêm/chạy tests trong lần này. Event contract v2 instrumentation còn cần khép trước main runs.

**Kết luận:** xử lý code và ma trận case đã bàn giao; acceptance runtime vẫn Not run.
