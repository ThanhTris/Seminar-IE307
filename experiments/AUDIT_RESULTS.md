# SEM-44 — Automated main-run audit

- Audit status: **NOT_RUN**
- Runs inspected: 0
- CSV rows: 0
- Valid events parsed: 0
- Background worker starts (PERIODIC/PUSH): 0
- Manual worker starts (excluded from background count): 0
- Generated at UTC: 2026-11-03T05:53:31Z

The report reads input artifacts and does not rewrite logs or CSV. `AUDIT_READY` means structural cross-checks found no listed issue; it does not certify the physical procedure or replace owner review.

## Runs

| Run | Device | Mode | Phase | Outcome | Event count | Issues |
|---|---|---|---|---|---:|---|

## Audit issues

- `RESULTS_CSV_MISSING`
- `RUNS_DIRECTORY_MISSING`

## Interpretation

- A `work_started` with source `MANUAL` is reported separately and must not enter background success rates.
- A `push_send_accepted` does not count as receipt or application; only `snapshot_applied` confirms cache application.
- Missing events remain unobserved; this audit never infers delivery or success from event absence.
- Timeout latency must remain blank/null, not zero.
- This script does not calculate latency across devices. Apply clock-offset uncertainty and same-boot monotonic rules from `docs/EXPERIMENT_PROTOCOL.md`.
- Record run-specific producer corrections without editing original event data; rerun the audit after source artifacts change.
