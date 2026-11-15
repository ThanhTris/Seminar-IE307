# SEM-36 — Hybrid pilot record

**Status: NOT RUN.** This file is a run sheet, not evidence of a pilot. SEM-34's preflight found Firebase blocker B1; its owner PR records five E02 slots as NOT_RUN and no accepted/received/applied event. That is relevant status, not a substitute hybrid pilot.

## Required inputs

- SEM-34 PUSH pilot manifest/events and CHECKS (still Todo; board marks input status Sẵn sàng).
- SEM-38 duplicate/version-hint implementation and CHECKS (Done; local implementation and unit-test report are available).
- Built candidate APK, app/server commits, device aliases, and a new run ID.
- A server version change and SEM-40 controlled skip-push procedure for E06.

The SEM-34 E02 run was not completed because Firebase is not configured. No E05/E06 hybrid run was performed on this workspace. Do not infer device behavior from source code or fixtures.

## E05 — competing triggers / race

| Field | Planned value |
|---|---|
| Expected | PERIODIC and PUSH enter the same worker/core; the Room transaction preserves the newest version, with equal-version work recorded unchanged. |
| Assertions | No cache version decrease; no duplicate snapshot write; correlate request/work/message IDs; record each trigger and terminal outcome separately. |
| Actual | Not run; no current hybrid run artifacts. |
| Result | **NOT RUN** |

## E06 — missed push / periodic recovery

| Field | Planned value |
|---|---|
| Expected | Controlled push skip is identified as intentional; a later eligible PERIODIC worker can fetch and apply the current server version. |
| Assertions | No `push_send_accepted` for the intentionally skipped send; no claim of FCM delivery failure; recovery is counted only on `snapshot_applied`. |
| Actual | Not run; no current E06 run artifacts or candidate build. |
| Result | **NOT RUN** |

When executed, attach original `manifest.json` and `events.jsonl`, plus device/build details and the command sequence. Do not edit the original logs to repair a failed assertion.
