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
| Executable logic/build checks | Runtime assertions pass | Build assembleDebug và testDebugUnitTest PASS 100% | Pass (host review) |

Commit: merge commit `25171b8c80234794332b2f1d142867c7d3f4e37d` ([PR #10](https://github.com/ThanhTris/Seminar-IE307/pull/10)).
WorkManager 2.12.0, Room 2.8.5.
Trạng thái task SEM-39 trên GitHub Project 3 đã được cập nhật sang **Done** (item `PVTI_lAHOCnL5Fs4BpUDUzhEiXUA`).

**Kết luận:** Xử lý version guard, idempotence, bounded retry và ma trận CORE_CASES.md đã hoàn tất, build Android pass; task đã được nghiệm thu và đánh dấu Done.
