# Sync modes and integration — SEM-36

## Shared execution path

`SyncRepository` is the single place that fetches and applies snapshots. Manual and FCM requests use `SyncWorkEnqueuer`; periodic work uses `PeriodicSyncScheduler`. All three sources reach the same `SyncWorker`, Room cache, and transactional version guard. The SEM-38 `PushSyncEnqueueAdapter` checks the persisted device mode and deduplicates exact redelivery by run-scoped signal/message IDs. Older/equal `version_hint` values still enqueue so the core fetch and version guard decide the outcome.

## Selecting a mode

The mode buttons in the app call `SyncModeController.configure(mode, runId)`:

- `PERIODIC`: register/update the unique connected-network periodic request; the worker rejects PUSH triggers in this mode.
- `PUSH`: cancel the unique periodic request; the worker rejects PERIODIC triggers in this mode.
- `HYBRID`: keep the unique periodic request and allow PUSH; both paths use `SyncWorker`/`SyncRepository`.

Mode and active run ID are persisted together after the WorkManager operation completes. Mode changes are refused while a tagged sync worker is running; retry after it reaches a terminal state. The registered periodic request is not evidence that it has started. If the schedule/run is changed during an observation window, mark that run as contaminated before collecting results.

## Interpretation limits

Hybrid is a fallback arrangement, not a promise to bypass Doze, force-stop, OEM policy, or network constraints. Periodic work remains best-effort and can be delayed. A push send acceptance is not device receipt; receipt is not worker start; worker start is not snapshot application. Use the local event timeline and the run manifest to distinguish these outcomes.

## Pilot status

The code path is prepared and SEM-38's messaging handoff is complete, but no E05/E06 hybrid pilot is recorded in this checkout. SEM-34 remains Todo with Firebase blocker B1; its missing pilot can be recorded as NOT_RUN and does not block starting or completing SEM-36 when the task's own outputs and checks are present. See [SEM-36 checks](evidence/SEM-36/CHECKS.md) and [pilot record](evidence/SEM-36/HYBRID_PILOT.md).
