# SEM-44 — CHECKS và bàn giao kiểm độc lập

- Owner duy nhất: Tâm (`HoaiTam`); ngày kiểm **17/11/2026, UTC+7**.
- Nhánh `codex/SEM-44-independent-audit`, input main **`1475e67c7b65b4ffcaa540d10da76e6d1bfaab00`**; CSV/parser draft **`1a0c667c93391553cd08f054407d7eb04be2d4ef`** chưa merge, source index ghim cohort riêng.
- SEM-41/42 Todo, SEM-45 In Progress khi kiểm Project; SEM-44 hiện cho phép bắt đầu không cần gate, đầu vào thiếu ghi Not run/giới hạn. Đây là audit tài liệu/log/công cụ, không chạy app, build APK, gửi FCM hay tạo run đo. Build/config của dữ liệu thật nằm trong từng manifest và VERIFICATION, không thay bằng commit tool audit.
- Host macOS ARM64, Python 3.13.3; yêu cầu công cụ Python 3.10+. Không có credential/token được dùng.

## Đầu ra có thật

- [AUDIT.md](../../../experiments/AUDIT.md): phạm vi, assertion, inventory, phiếu giới hạn theo nguồn và lệnh tái lập.
- [VERIFICATION.json](VERIFICATION.json): 25 thư mục evidence, per-run build/phase/outcome/validity/counts-all, SHA-256 và so CSV ghim.
- [CSV_REPRODUCTION.json](CSV_REPRODUCTION.json): CSV nháp 12 dòng tái sinh giống từng byte; 0 eligible, rate null trong group summaries.
- [AUDIT_RESULTS.md](../../../experiments/AUDIT_RESULTS.md): kết quả main hiện **NOT_RUN**, 0 main/0 CSV trên main checkout; giữ 2 pilot legacy ở danh sách excluded.
- Auditor main được sửa và có [12 regression tests](../../../experiments/scripts/tests/test_audit_main_runs.py); verifier/reproducer riêng ở `experiments/scripts/`, không sửa source producer.

## Expected / actual

| Check | Expected | Actual | Kết quả |
|---|---|---|---|
| Inventory/provenance | Đúng snapshot, run/build/hash thật | 2 pilot legacy + 20 pilot v2 + 3 development, 0 main; source hashes khớp Git/index | Pass — nguồn/cấu trúc |
| Schema/trigger/correlation | Giữ source và đúng run/device/mode | 224 canonical event (203 pilot + 21 development) đạt schema/context; không gộp control/MANUAL thành main | Pass — giới hạn structural |
| CSV ↔ manifest/log | Metadata/hash/counts khớp ở revision rõ ràng | 12 dòng draft INVALID, 0 mismatch độc lập; không chứa 8 run mới đúng như selection scope công bố | Pass — scope draft, coverage còn thiếu |
| Tái lập CSV | Parser cùng input sinh cùng bytes | CSV SHA-256 `49d4f9e7c533f50f17fd429783fabb4afde15f27ad7a0c1e0e0c3fc3958fe8b0` khớp; template, analyzer và validator đúng revision | Pass — reproducibility |
| Mẫu số/timeout | Giữ INVALID và timeout riêng, không thay null bằng 0 | Draft 12 input/0 eligible/12 excluded/0 complete, 5 TIMEOUT giữ nguyên, group completion rates null | Pass — không suy main statistics |
| Tool regression | Phát hiện lỗi đọc/so sánh và không đè input | **86 tests pass**, gồm 12 mới: blank metadata/hash, counts, dòng trùng, timeout scientific zero/positive, boot null, applied version mới hơn target, output overlap… | Pass — synthetic, không phải outcome thực nghiệm |
| Main auditor chạy thật | Không ký Pass khi input thiếu | Exit 2, `MAIN_RUNS_MISSING`, `RESULTS_CSV_MISSING`; pilot bị loại trước validate main | **NOT_RUN — main/CSV chưa nhận** |
| Timing/window/OPPO/main completeness | Có dữ liệu gốc và certainty phù hợp | Main/OPPO chưa có; canonical boot null và clock uncontrolled giữ nguyên; không tính latency mới hoặc tái ký qualification pilot | **NOT_RUN / không chứng nhận** |
| Bảo toàn nguồn | Không sửa manifests/events/CSV hoặc code task khác | So từng input với Git snapshot và index khớp; diff giới hạn audit docs/tools/reports/tests | Pass |

Đã kiểm source-index ghim dữ liệu12 run bằng exact Git bytes; 8 pilot mới thiếu trong CSV là giới hạn cohort đã công bố, không tự quy là lỗi producer hoặc tự thêm dòng. Tái sinh CSV chạy parser ở thư mục local riêng; phải đặt root và TEMPLATE theo checkout, sau khi xác minh template khớp ref. Đây không phải phép đo runtime mới.

## Bàn giao và việc còn chờ

Hồ sơ đủ đề nghị Review **phần SEM-44 đã thực hiện** theo policy task mới: artifact/assertion/evidence thật có mặt, giới hạn/Not run minh bạch. Không ký Pass cho main, không biến pilot/control/fixture thành main hoặc điền số liệu giả. Phần audit main chỉ chạy lại khi SEM-41/42 bàn giao log và SEM-45 có CSV tương ứng, đúng revision/build/config.

Các nguồn cần tiếp nhận và phiếu A44-01…04 nằm trong AUDIT; nhận phạm vi mới thì chạy lại cả inventory, independent compare và main audit. Các cập nhật report/CLAIMS/SUMMARY thuộc owner của task tương ứng. Bàn giao cho SEM-43/48 qua PR tag trưởng nhóm.

Trạng thái kết thúc làm việc là Review; trưởng nhóm kiểm nhận và merge, không tự chuyển Done. Sau bàn giao chỉ sửa theo comment yêu cầu.
