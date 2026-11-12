# SEM-36 CHECKS — mode integration and hybrid pilot

## Deliverables in this checkout

- Mode controller and UI mode selection: `android/app/src/main/java/com/thanhtris/seminarie307/integration/SyncModeController.kt` and `ui/BulletinScreen.kt`. The UI requires a supplied run ID and device alias; it does not invent run/device values. Changes wait for one-time work to finish and refuse mode transitions while any worker is running.
- MANUAL/PUSH/PERIODIC all reach the shared worker: manual uses `integration/RealBulletinUiGateway.kt`, FCM uses the SEM-38 `PushSyncEnqueueAdapter`, and periodic uses `PeriodicSyncScheduler`.
- Integration notes: [SYNC.md](../../SYNC.md).
- Pilot run sheet: [HYBRID_PILOT.md](HYBRID_PILOT.md).
- Canonical Android event serializer/export action: `CanonicalTimelineExporter` and SEM-29 instrumentation action `export-v2`; legacy rows and unsupported event types are listed in a separate export report, never relabeled.

SEM-34's live push pilot remains **NOT_RUN** because Firebase project/credential/token are not configured (B1); see [PR #26 review and preflight](https://github.com/ThanhTris/Seminar-IE307/pull/26). The PR owner explicitly says keep SEM-34 Todo until a real E02 run. SEM-36 records this state and does not claim a push result.

## Verification

| Check | Expected | Actual | Status |
|---|---|---|---|
| Static integration review | Mode transition updates/cancels the unique periodic request; MANUAL/PUSH/PERIODIC route to the shared worker | Source paths align: mode controller, shared enqueuer, periodic scheduler, and SEM-38 push adapter | Pass (source review) |
| Android build and unit tests | Build/tests pass for this exact working tree | Attempted `:app:testDebugUnitTest :app:assembleDebug :app:assembleDebugAndroidTest`; Gradle stopped before task execution because Android SDK Platform 37 and Build Tools 36.0.0 licenses are not accepted | Blocked before execution |
| E05 race pilot | Same core/cache handles competing PERIODIC/PUSH; no rollback or duplicate write | No E05 hybrid run artifacts or candidate build | Not run |
| E06 recovery pilot | Controlled push skip followed by periodic apply | No E06 run artifacts or candidate build; Firebase B1 means a real push path cannot be established here | Not run |
| Mode transition on device | Mode transition waits for active work to finish; required schedule is aligned | Guard is present in source; no emulator/ADB in this environment | Not run |
| Canonical event export | Android observations can be consumed as schema 2.0 without inventing missing fields | Room v2 migration captures new provenance fields; strict serializer emits the schema 2.0 key set and instrumentation `export-v2` produces JSONL plus an omission report. Legacy rows and `periodic_cancelled` remain explicitly unexportable | Implemented; runtime export not run |

Build command attempted after the schema-2 work began: `android\gradlew.bat :app:testDebugUnitTest :app:assembleDebug :app:assembleDebugAndroidTest` with `ANDROID_HOME=D:\Android\Sdk`. Gradle reported the licenses for `build-tools;36.0.0` and `platforms;android-37.0` are not accepted and stopped before compilation. Follow-up source edits after that attempt mean the current PR head has no successful build verification. `adb`/emulator remain unavailable.

**Conclusion:** mode integration, Room schema-2 provenance, strict serializer, and export action are implemented. Device E05/E06, exact-branch build, and runtime export remain Not run; legacy Room rows and unsupported cleanup events are reported as omissions. Keep these limitations visible and do not mark SEM-36 Done as if the pilots passed. The live board assigns this item to Trung; SEM-34 is a missing input that can be recorded NOT_RUN due B1, not a start gate.
