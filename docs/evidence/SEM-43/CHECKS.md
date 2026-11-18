# SEM-43 — CHECKS và bàn giao SUMMARY

Vinh (`Vinh5905`), **16/11/2026, UTC+7**. Nhánh `codex/SEM-43-evidence-summary` bắt đầu từ main **`007a1aa31d02d7af47570f4cf7b60a7ed8135a33`**, sau khi PR [SEM-41 #29](https://github.com/ThanhTris/Seminar-IE307/pull/29) merge lúc 08:50:12 UTC+7. Không cần thiết bị hoặc phép đo mới để thực hiện phần tổng hợp này.

## Đầu ra và phạm vi

- [SUMMARY.md](../../../experiments/SUMMARY.md): hypothesis → observation → explanation → limitation cho E01–E06, nguồn run/build, main NOT_RUN, tập bị nhiễu/legacy/control và giới hạn dùng cho report/slide.
- [EVIDENCE_INDEX.json](EVIDENCE_INDEX.json): nguồn snapshot và SHA-256 của 20 lần thử SEM-41, hai pilot legacy, ba control; riêng revision/CSV ở PR SEM-45 chưa merge.
- [VERIFICATION.json](VERIFICATION.json): kết quả kiểm nguồn/hash/schema/link và checksum đầu ra. Đây là kiểm tài liệu/traceability của SEM-43, không phải kiểm độc lập thực nghiệm SEM-44.

Task không thay parser/CSV SEM-45, audit SEM-44, release manifest SEM-37, raw logs, kết quả chạy, app hoặc server. Trạng thái Project trong thẻ là snapshot nguồn; không tự chuyển Project Done từ đầu ra tài liệu. Theo quy định task, đầu vào chưa nhận được ghi NOT_RUN/giới hạn, không chặn chuẩn bị SUMMARY.

## Artifact, build và config đã nhận

| Nguồn | Expected | Actual tại snapshot | Kết quả |
|---|---|---|---|
| SEM-41 pilot mới | Manifest/events/audit và provenance thực | 8 VALID/SUCCESS trên emulator-main, phase pilot, app `9e7e55b`, server `c77772e`, APK `bde050c…` | Pass — mô tả pilot theo producer review |
| SEM-41 các lần thử cũ | Giữ thất bại/timeout và validity sửa theo audit | 12 INVALID: 5 SUCCESS, 5 TIMEOUT, 2 ABORTED/FAILURE; mọi clock/event/outcome nguồn giữ nguyên | Pass — không chọn bỏ riêng timeout |
| Build/config | Không gộp cấu hình hoặc source khác nhau | Android 17/API 37, Google emulator ARM64, Play services 26.43.30; periodic interval/flex 15 phút, CONNECTED, FIREBASE_NOT_CONFIGURED; group theo case/mode/build/config/epoch/intervention/observer | Pass — metadata/limits |
| Emulator main | 27 run trên candidate theo protocol | 27 slot kế hoạch, 0 manifest phase main | NOT_RUN |
| OPPO | 6 main run E01/E02, metadata/CHECKS máy thật | Chưa có artifacts/CHECKS SEM-42 trong main đã nhận | NOT_RUN |
| SEM-45 | CSV/parser đúng nguồn hiện hành | PR #30 vẫn draft, head `1a0c667`, CSV có 12 pilot cũ INVALID, nguồn ghim `42ca000`; không có 8 pilot mới và chưa merge | Chưa nhận vào main; không dùng làm thống kê main |
| SEM-44 | Kiểm độc lập các run/CSV đã nhận | AUDIT_RESULTS lịch sử 03/11 NOT_RUN, 0 run/0 row; chưa ký kiểm bộ dữ liệu mới | NOT_RUN — kiểm độc lập |
| Candidate | Artifact/config freeze và gate thật | Release manifest NOT_READY/gate false. SEM-41 follow-up đã kiểm 32/32 unit tests; không lặp lại lý do fail 31/32 lịch sử như lỗi hiện hành | Chưa freeze; main NOT_RUN |

Nguồn build đầy đủ, APK checksum và từng config fingerprint nằm trong EVIDENCE_INDEX và manifest ở registry SUMMARY. Test công cụ 74/74 và Android unit 32/32 là bằng chứng SEM-41 đã nhận, không phải số sample thực nghiệm hoặc phép kiểm mới của SEM-43.

## Kiểm chứng đầu ra SEM-43

| Hạng mục | Expected | Actual | Kết quả |
|---|---|---|---|
| Source snapshot | Có revision để truy vết | Main `007a1aa…`, đã nhận SEM-41 merged; file nguồn có SHA-256 | Pass |
| Main count | Đọc phase trong manifest | 0 main; hai manifest trong experiments/runs là pilot legacy, không main | Pass — main NOT_RUN |
| Inventory pilot | Mỗi attempt có manifest/events/audit/observation | Đủ 20 SEM-41, đối chiếu validity/execution/outcome và checksum | Pass |
| Schema canonical | Event/manifest 2.0 được validator SEM-24 chấp nhận | Kiểm cả 20 run SEM-41; legacy ghi riêng, không đổi nhãn v1→v2 | Pass |
| Registry mới | Table truy được full run/build, duration/cache/cycle đúng nguồn | Đủ 8 run, cache 15→23; E01 5 cycle; E03 post-idle; E04 apply sau reconnect; E06 deliberate skip | Pass — số do producer ghi, chưa SEM-44 |
| Mẫu số và timeout | Không trộn pilot với main/plan | Main n_complete/n_total=0/0, rate/median null; 12 INVALID vẫn liệt kê outcome gốc | Pass |
| Clock/latency | Không nâng certainty của event | Event boot_session_id null, clock controlled=false; không tính latency median/min–max; duration collector có nhãn riêng | Pass |
| CSV đang review | Đúng revision và phạm vi | Ghim 4 artifact ở head PR #30, CSV 12 INVALID; 8 pilot mới không có trong CSV | Pass — tham chiếu chưa merge |
| Audit/giới hạn | Producer review khác kiểm độc lập | SEM-44 main/CSV chưa chạy; không gọi đây là independent audit pass | Pass — thực nghiệm Not run |
| Link và nội dung dùng lại | Link local/anchor đọc được, bảng đầy đủ | Kiểm bằng script validation; số lượng và hash ở VERIFICATION.json | Pass |
| Bảo toàn đầu vào | Không sửa artifacts hoặc code của owner khác | Diff chỉ SUMMARY, evidence SEM-43, hướng dẫn README và tiến độ task SEM-43 | Pass |

Kết quả validation: **107 file nguồn khớp snapshot, 20 manifest/203 event canonical đạt schema, 8 hàng registry khớp số liệu, 104 link local/3 anchor và 9 bảng Markdown đạt**. Không sửa input hoặc tính thống kê latency.

## Tái kiểm nguồn

Từ root checkout SEM-43, đối chiếu catalog với byte Git tại snapshot đã ghim (không phụ thuộc CRLF của checkout); script chỉ đọc:

```sh
python3 -B - <<'PY'
import hashlib, json, subprocess
from pathlib import Path
index = json.loads(Path('docs/evidence/SEM-43/EVIDENCE_INDEX.json').read_text())
refs = list(index['source_evidence'])
for group in ('legacy_pilots_excluded_from_current_build',
              'development_controls_excluded_from_background_statistics'):
    for run in index[group]:
        refs.extend(run['sources'])
for run in index['sem41_pilot']['attempts_index']:
    refs.extend(run['sources'])
for source in refs:
    raw = subprocess.check_output(['git', 'show', index['source_snapshot_commit'] + ':' + source['path']])
    assert hashlib.sha256(raw).hexdigest() == source['sha256'], source['path']
manifests = [json.loads(p.read_text()) for p in Path('experiments').rglob('manifest.json')]
assert not any(m.get('run_phase') == 'main' for m in manifests)
attempts = index['sem41_pilot']['attempts_index']
assert len(attempts) == 20
assert sum(r['validity'] == 'VALID' for r in attempts) == 8
assert sum(r['validity'] == 'INVALID' for r in attempts) == 12
print('Source hashes and dataset separation PASS')
PY
git diff --check
```

PR SEM-45 được đọc riêng, không merge vào nhánh này. Muốn đối chiếu artifact tham chiếu của nó:

```sh
git fetch origin 1a0c667c93391553cd08f054407d7eb04be2d4ef
git show 1a0c667c93391553cd08f054407d7eb04be2d4ef:docs/evidence/SEM-45/INPUTS.json
git show 1a0c667c93391553cd08f054407d7eb04be2d4ef:experiments/results.csv
```

Không chạy build/ADB/FCM hoặc thu dữ liệu mới cho SEM-43. Không tạo test mô phỏng rồi gọi là run thật. Không cần chạy lại Android/tool unit suite vì phần thay đổi chỉ là tài liệu/catalog; validation tập trung vào nguồn, phép đếm, schema và link.

## Đầu vào còn thiếu và bàn giao

SUMMARY hiện có thể bàn giao cho SEM-48/50/52/55 với nhãn pilot/NOT_RUN nêu trong tài liệu. Chưa có kết luận main, OEM, FCM callback/delivery, E05 race, độ trễ so sánh hoặc tiết kiệm pin.

Khi nhận main emulator/OPPO, parser/CSV và audit đúng revision: cập nhật EVIDENCE_INDEX, registry/mẫu số và phần diễn giải; mọi metric có n_complete/n_total, missing/timeout cùng căn cứ clock. Không đổi phase của dữ liệu cũ để lấp chỗ trống. CSV PR #30 cần nhận bộ pilot mới nếu owner SEM-45 muốn phân tích chúng; việc đó thuộc SEM-45.
