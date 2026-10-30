# SEM-14 — CHECKS and handoff

- Owner: Trí (`ThanhTris`).
- Evidence recorded: 30/10/2026 19:34:58 (UTC+7).
- Scheduled deadline: 30/10/2026 14:00 (UTC+7); deadline field retained as assigned.
- Base: `f95548d935cb0d78a0fabbeae03ccc021e85ce3b` (`main`, includes merged SEM-11 PR #1).
- Branch: `codex/SEM-14-shared-sync`.
- Contract artifact commit: `3bf7dcfc9ced0bd7df1a0db0dc5d59f00b1c5c74`.
- Project status: Todo → In Progress → Review → Done; final snapshot check passed.

## Acceptance checks

| Check | Expected | Actual / evidence | Result |
|---|---|---|---|
| Scope/build inputs | SEM-11 scope and Android baseline define the accepted demo | Read `docs/SCOPE.md`, `docs/environment/ANDROID_BUILD.md`, and `docs/PLAN.md`; the package, modes, API 37, WorkManager, and Room baseline agree with this contract | Pass |
| Three triggers share sync core | MANUAL, PERIODIC, and PUSH lead to one worker/repository; scheduling adapters remain distinct | Component and sequence diagrams show one `SyncWorker` and `SyncRepository`; one-time work serves MANUAL/PUSH and periodic registration invokes the same worker | Pass (design contract; runtime not exercised) |
| Shared input and correlation | source, mode, run_id, version hint, and IDs have distinct meanings | Tables and Kotlin pseudocode define `SyncInput`, `Correlation`, `EnqueueReceipt`, and `SyncOutcome`; periodic request IDs differ by cycle and FCM `message_id` may be null | Pass (design contract) |
| Cache/version behavior | UI reads local cache; stale responses cannot roll back cache; applied is visible after commit | GET is outside the Room transaction; current version is reread inside the transaction; apply event and cache update commit together | Pass (design contract; runtime not exercised) |
| Trigger/mode transitions | New requests are preserved; old work is not attributed to a new run | Contract defines rejection of disabled/stale inputs, drain-or-contaminate transition behavior, and preservation of signals arriving during active work | Pass (requirements handed off; runtime not exercised) |
| Failure outcomes | Enqueue, worker start, applied, unchanged, retry, and failure are not conflated | Contract separates accepted enqueue from completed sync; transient failures map to RETRY, permanent contract/data failures to FAILURE | Pass (design contract; runtime not exercised) |
| Responsibility boundary | Each next task has a clear ownership area and handoff | Ownership table covers SEM-23/25/26/27/30/32/36/38/39; direct consumers SEM-19/26/46 are linked | Pass |
| Mermaid diagrams | Component and sequence diagrams parse and render | Mermaid CLI `12.0.0` rendered both diagrams with Chrome; SVGs were visually inspected in ignored `.local/sem14/` | Pass |
| Internal links and content | Local Markdown links resolve and task acceptance is covered | Relative-link scan found 16 valid internal links in `SHARED_SYNC.md` and 4 in this CHECKS file. Scenario review covered all six acceptance cases | Pass (document review) |
| Whitespace and secrets | No whitespace errors or credentials in deliverables | Trailing whitespace check passed for both files; credential-shaped pattern scan had no matches | Pass |
| Android runtime / device / FCM | Real implementation run is evidenced | No Android scaffold exists in SEM-14; no build, emulator, physical device, or FCM request was run. SEM-23/25/30/32 and downstream owners perform those checks | Not run (downstream tasks) |
| Final staged diff | No whitespace errors in committed artifacts | `git diff --cached --check` after staging CHECKS and generated task snapshot | Pass |
| Project snapshot | Done and generated snapshot agree with Project | `--apply` refreshed generated project/task docs; `--check` verified 45 tasks, 2 Done/43 Todo, 9 ready/8 prep/28 waiting, one owner per task, and no dependency cycle | Pass |

## Scenario review — document contract only

| Scenario | Expected contract behavior | Result |
|---|---|---|
| MANUAL, PERIODIC, PUSH | All reach one worker/core with source retained; MANUAL is labeled separately | Pass |
| Reopen UI while offline | Screen reads Room cache and creates no GET or implicit sync | Pass |
| Server version newer/equal/older than cache | Apply newer; unchanged on equal; preserve cache on older | Pass |
| New push arrives during active worker | Keep the new signal and its correlation for a subsequent sync | Pass (implementation delegated to SEM-38/39) |
| Network or permanent API/data error | Transient returns RETRY; permanent failure returns FAILURE; neither claims applied | Pass (retry details delegated to SEM-26/39) |
| Mode/run changes with old work pending | Do not relabel; drain old work or mark run contaminated | Pass (integration delegated to SEM-36) |

## Validation record

The two Mermaid diagrams were extracted from `docs/mechanisms/SHARED_SYNC.md` and rendered as ignored review artifacts under `.local/sem14/`. The local Markdown link scan ignores web URLs and confirms every relative target exists. No Android build or runtime claim is made by these document checks.

After Project status changed to Done, I ran:

```powershell
python scripts/update_task_snapshot.py --apply
python scripts/update_task_snapshot.py --check
git diff --check
```

Snapshot result: `--check` verified 45 tasks with 2 Done and 43 Todo, input status 9 ready / 8 prep / 28 waiting, one owner per task, and no dependency cycle. `git diff --check` passed.

## Handoff

- **[SEM-19](../../../tasks/backlog/SEM-19.md):** use the trigger-to-cache flow and distinguish accepted, received, started, and applied.
- **[SEM-26](../../../tasks/backlog/SEM-26.md):** define endpoint, payload, error details, and canonical event fields from the logical input/correlation meanings.
- **[SEM-46](../../../tasks/backlog/SEM-46.md):** use the architecture flow for the opening explanation and align claims with the SEM-37 candidate.
- **SEM-23/25/30/32/36/38/39:** use the ownership table and implementation boundaries in `docs/mechanisms/SHARED_SYNC.md`.

No credentials, Firebase config, device serial, or local properties are included. Contract behavior above is a specification; runtime outcomes remain Not run until their owning tasks implement and execute the flow.
