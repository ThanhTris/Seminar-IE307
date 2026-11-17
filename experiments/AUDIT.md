# SEM-44 — Kiểm độc lập evidence và phép tính

**Ngày kiểm: 17/11/2026 (UTC+7). Main audit: NOT_RUN.** Đã kiểm độc lập cấu trúc/provenance của evidence hiện có và CSV pilot nháp được ghim; chưa có run `main` hoặc `experiments/results.csv` trên main để ký kiểm thực nghiệm cuối. Kết quả công cụ đạt không có nghĩa các phép đo main đã Pass.

## 1. Snapshot và phạm vi

- Owner: Tâm (`HoaiTam`). Input main ghim tại **`1475e67c7b65b4ffcaa540d10da76e6d1bfaab00`**, sau PR SEM-41 #29 và SEM-43 #31.
- Đầu vào đọc: [SEM-41 CHECKS](../docs/evidence/SEM-41/CHECKS.md), [SEM-43 EVIDENCE_INDEX](../docs/evidence/SEM-43/EVIDENCE_INDEX.json), manifest/events theo run, protocol, schema và candidate manifest. Các artifact đi qua verifier có SHA-256 trong [VERIFICATION.json](../docs/evidence/SEM-44/VERIFICATION.json).
- CSV/parser SEM-45 **chưa merge**, chỉ đọc và tái lập bản nháp tại **`1a0c667c93391553cd08f054407d7eb04be2d4ef`**, [PR #30](https://github.com/ThanhTris/Seminar-IE307/pull/30). Không chép CSV lên main hoặc sửa nguồn của Tuấn.
- Theo yêu cầu task cập nhật, có thể bàn giao công cụ/AUDIT/CHECKS khi input còn thiếu, với Not run/giới hạn. Việc chốt Done/merge vẫn để trưởng nhóm thực hiện theo quy trình đã thống nhất.

## 2. Inventory đã kiểm

| Tập | Artifacts | Kết luận phạm vi |
|---|---:|---|
| Main emulator/OPPO | 0 run | NOT_RUN; không có mẫu để tính completion rate hoặc latency main |
| Pilot SEM-41 canonical v2 | 20 attempts, 203 event | 8 run do producer ghi VALID/SUCCESS; 12 INVALID vẫn giữ outcome: 5 SUCCESS, 5 TIMEOUT, 2 FAILURE/ABORTED |
| Pilot SEM-29 legacy | 2 manifest | Giữ riêng `legacy-room-v1`, không tự nâng schema hoặc nhập vào mẫu main |
| Development/CONTROL | 3 run, 21 event v2 | MANUAL/control/dispatch diagnostic; loại khỏi thống kê nền main |
| CSV draft SEM-45 | 12 dòng pilot cũ, 12 INVALID | Khớp nguồn ghim; không đại diện cả 20 attempts mới nhất và không phải CSV main |

Đã rà toàn bộ manifest trong `experiments/runs`, `experiments/pilots`, `experiments/development` ở snapshot: **25 thư mục**, không có phase main. Không lấy tên thư mục `runs` làm chứng cứ phase. 33 slot kế hoạch của hai máy không phải 33 run đã đo, cũng không phải mẫu số success rate.

20 pilot/3 control có 224 event canonical khớp schema và context run/device/mode; không có event ID trùng trong mỗi file. Đây là kiểm cấu trúc, không tái xác nhận điều kiện vật lý, collector hoặc qualification của producer. 12 INVALID không được chuyển VALID vì parser đọc được file.

## 3. Assertion, expected và actual

| Hạng mục | Expected | Actual / assertion | Kết luận |
|---|---|---|---|
| Source/hash | Byte đầu vào khớp commit và sổ nguồn | `verify_sem44.py`: 0 snapshot mismatch, 0 hash mismatch so với SEM-43 index; hash manifest/events CSV cũng khớp | Đạt trong snapshot |
| Metadata CSV | Run/case/device/mode/phase/outcome/validity/build khớp manifest | 12/12 dòng draft đối chiếu các trường và SHA-256, 0 mismatch, 0 trùng run | Đạt trong scope draft |
| Trigger/counts | Event type/source đúng schema; đếm từ log, không coi accepted là applied | Đếm lại mọi cột `*_event_count_all` có trong CSV; 0 mismatch; development/control ghi nguồn riêng, không nhập background main | Đạt về cấu trúc/counts-all |
| Applied/unchanged | Giữ tên outcome theo event; applied cache/data version khớp | Kiểm schema canonical và so cặp applied version/cache; không ép mọi applied bằng target vì snapshot mới hơn có thể hợp lệ | Đạt cấu trúc; sequence/window audit main NOT_RUN |
| CSV tái lập | Cùng parser/source index cho cùng byte CSV | Tái sinh 12 dòng bằng parser/validator đúng revision; byte khớp, SHA-256 `49d4f9e7c533f50f17fd429783fabb4afde15f27ad7a0c1e0e0c3fc3958fe8b0` | Đạt tính tái lập draft |
| Mẫu số draft | INVALID loại khỏi tập đủ điều kiện, giữ timeout/lỗi | Parser group totals: 12 input, 0 eligible, 12 excluded, 0 complete; tất cả completion rate null | Không báo “0% thành công” hoặc suy tỷ lệ main |
| Coverage CSV | Chỉ kết luận cho run được chọn | CSV source-index cố ý giữ cohort cũ; thiếu 8 ID pilot mới liệt kê trong VERIFICATION | Giới hạn coverage, không coi là lỗi số đo |
| Clock/boot/window | Duration monotonic chỉ khi chứng minh cùng boot; UTC liên máy có offset | Event Android của pilot mới còn boot ID null; clock controlled=false; CSV giữ window unverified và không tạo completion latency cho timeout | Kiểm timing main NOT_RUN; không tự điền boot hoặc offset |
| Main/OPPO/candidate | Nhận run phase main và CSV từ bản freeze | Không có main/OPPO; candidate nguồn vẫn NOT_READY/gate false dù task source có thể Done | NOT_RUN, không tự ký Pass |

`CSV_REPRODUCTION.json` ghi byte/hash và tổng mẫu số draft. Tái chạy parser chỉ kiểm tính tái lập; phần đối chiếu độc lập dùng `verify_sem44.py` đếm trực tiếp từ log và không gọi công thức analyzer.

## 4. Phiếu giới hạn và bàn giao về nguồn

| ID | Nguồn cụ thể / expected → actual | Hướng xử lý khi có đợt dữ liệu mới |
|---|---|---|
| A44-01 | CSV `1a0c667`: scope 12 pilot cũ; inventory snapshot có 20. Ví dụ `run-sem41-pilot-e01-1-20261115-575a7a` và `run-sem41-pilot-e06-2-20261116-8f734c` chưa có dòng CSV | SEM-45/Tuấn giữ nhãn cohort cũ hoặc phát hành batch mới có INPUTS/hash rõ; không tự thêm/sửa dòng CSV trong SEM-44 |
| A44-02 | `run-sem41-pilot-e01-1-20261115-575a7a`: app `9e7e55b`, server `c77772e`; manifest có collector boot nhưng canonical Android boot null. Expected timing cùng boot → actual chưa đủ bằng chứng trong canonical | Producer tích hợp/SEM-41 giữ raw/collector và bổ sung bằng chứng đúng nguồn ở run mới. SEM-44 không gán collector boot vào event hoặc tính latency thay producer |
| A44-03 | Tất cả 8 source-VALID pilot r6 vẫn `run_phase=pilot`, candidate gate false; 0 emulator/OPPO main | SEM-37/41/42 chốt artifact và run thực theo protocol; sau đó SEM-45 phát hành CSV. Tái audit theo build/config mới; không đổi phase cho pilot |
| A44-04 | Auditor cũ có thể đếm pilot như main, bỏ qua metadata trống/cột count mới, so monotonic khác boot và ép applied bằng target | Đã sửa trong công cụ audit do SEM-44 sở hữu, kèm 12 test hồi quy synthetic. Không sửa log hay validity nguồn |

Các mục trên là phiếu giới hạn trong hồ sơ bàn giao; trạng thái và phần sửa nguồn do owner của task tương ứng xử lý. Không yêu cầu sửa dữ liệu để khớp giả thuyết. Source VALID/SUCCESS của 8 pilot chỉ là qualification đã nhận; SEM-44 chưa chứng nhận lại các window hoặc ký Pass cho tập main.

## 5. Công cụ và cách tái lập

Từ root repo, Python 3.10+. Các lệnh chỉ đọc inputs; script ghi report/evidence của SEM-44. Không cần Android, Firebase, credential hay network. Object Git của revision draft cần đã có trong clone.

```sh
python3 -B -m unittest discover -s experiments/scripts/tests -v
python3 -B experiments/scripts/verify_sem44.py --source-ref 1475e67c7b65b4ffcaa540d10da76e6d1bfaab00 --draft-ref 1a0c667c93391553cd08f054407d7eb04be2d4ef
python3 -B experiments/scripts/reproduce_sem45_csv.py --ref 1a0c667c93391553cd08f054407d7eb04be2d4ef
python3 -B experiments/scripts/audit_main_runs.py
```

- **86/86 test công cụ đạt**, gồm 12 test audit mới; fixture trong thư mục tạm không phải run đo thật.
- Verifier exit 0 nghĩa các kiểm tra giới hạn đã khớp; trường `main_status=NOT_RUN` vẫn giữ nguyên.
- `audit_main_runs.py` hiện exit **2** có chủ ý: `MAIN_RUNS_MISSING`, `RESULTS_CSV_MISSING`; [AUDIT_RESULTS.md](AUDIT_RESULTS.md) ghi 0 main/0 CSV, 2 pilot được loại đúng scope. Không coi mã 2 này là Pass hoặc lỗi crash công cụ.
- Main auditor kiểm schema/correlation, exact metadata/hash, dòng trùng, event count, timeout latency và boot trước so monotonic. Cột count hỗ trợ tên cũ và `*_event_count_all`; hai count cốt lõi là bắt buộc. Nó không tự tính lại mọi metric, clock uncertainty hoặc chứng nhận quy trình vật lý. `AUDIT_READY` chỉ là cấu trúc đã qua các check đang hỗ trợ, vẫn cần review đầy đủ.
- `--output` của main auditor không được trùng CSV hoặc nằm trong thư mục inputs. Verifier chỉ ghi trong `docs/evidence/SEM-44`. Reproducer tách code ghim vào `.local/sem44/producer`, đặt root/template đúng checkout sau khi kiểm template khớp revision; không checkout/chỉnh nhánh SEM-45 hoặc thực hiện thí nghiệm mới.

Ở Windows, dùng executable Python 3.10+ phù hợp (`python`/`py`). Lần kiểm này chạy macOS; không tuyên bố đã chạy native Windows. Không sửa các byte JSON/JSONL/CSV nguồn; nếu checkout có thay đổi EOL/hash, xem lại artifact trước khi diễn giải mismatch.

[CHECKS SEM-44](../docs/evidence/SEM-44/CHECKS.md) ghi nhận đầu vào/expected/actual và phạm vi đề nghị Review theo quy định mới của task.
