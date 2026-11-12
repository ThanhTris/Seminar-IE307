# Demo runbook — SEM-52

**Readiness: NOT READY.** This runbook is prepared, but there is no release APK for this branch. Before using it, complete `release/BUILD_MANIFEST.json`, confirm its source revision and APK SHA-256, and verify the device has that exact APK installed. Never present a `NOT_RUN` slot or fixture as a completed demo result.

## 1. Preconditions

- Windows 11 or macOS ARM64; JDK 17+, Android SDK platform 37 and Build Tools 36.0.0; Node.js 22+; Python 3.10+; Git.
- One Android 17 emulator with Google Play services for FCM work; an OPPO Find X9 only for the OEM comparison.
- The local snapshot server, network access, and a private Firebase configuration/credential only if demonstrating PUSH. Follow [`docs/PUSH.md`](PUSH.md); keep `google-services.json`, service-account credentials, and device token outside Git and the presentation recording.
- The candidate manifest and exact app commit/build/checksum. Current candidate is **not built**; see [`CANDIDATE_GATE.md`](evidence/SEM-37/CANDIDATE_GATE.md).
- A real `run_id`, `device_alias`, and the selected mode from the approved experiment protocol. Do not use the UI's sample/default run as a measured run.

## 2. Build and verify the candidate

From PowerShell at the repository root, set `ANDROID_HOME` to the installed SDK path and build the exact commit listed in the candidate manifest:

```powershell
$env:ANDROID_HOME = 'D:\Android\Sdk'
$env:ANDROID_SDK_ROOT = $env:ANDROID_HOME
cd android
.\gradlew.bat :app:testDebugUnitTest :app:assembleDebug :app:assembleDebugAndroidTest
cd ..
Get-FileHash -Algorithm SHA256 android\app\build\outputs\apk\debug\app-debug.apk
```

Record build output, app commit, server commit, package/version, SDK levels, dependency lock state, and APK SHA-256 in `release/BUILD_MANIFEST.json`. Install only that APK. For SEM-34 instrumentation, install the matching `app-debug-androidTest.apk` as well. On the current workspace, this build has **not run** because the Android platform/build-tools packages and accepted SDK licenses are unavailable.

## 3. Start the snapshot server

In a separate terminal:

```powershell
cd server
npm ci
npm run build
npm test
npm start
```

Check `http://127.0.0.1:3000/health`. For an emulator, the app uses `http://10.0.2.2:3000`; for a USB device, follow the approved `adb reverse tcp:3000 tcp:3000` setup in [`docs/SETUP.md`](SETUP.md). Use a run-scoped server store and record its commit and starting version.

## 4. Select a mode and run

Open the installed app, select the mode, and verify the displayed mode and active run ID before starting. A mode transition that overlaps active work contaminates the measurement window; wait for terminal WorkManager state or mark the run invalid. All three triggers use the same worker/core and Room cache.

### Manual baseline

Issue a new snapshot through the server CLI, tap **Đồng bộ thủ công**, then inspect the timeline. The success sequence is `work_enqueued` → `work_started` → fetch/result → `snapshot_applied`; `work_enqueued` alone is not a sync result. Reopen the app offline to demonstrate Room persistence only when the run protocol calls for it.

### PERIODIC

Select PERIODIC, keep connected-network constraints satisfied, and leave the device idle for the protocol window. The interval is at least 15 minutes and is not a promised dispatch time. Do not force Jobscheduler during a natural run. Record `periodic_registered`, a real `work_started`, and the terminal cache outcome separately. If the worker is not observed, preserve timeout/NOT_RUN; do not claim success from the schedule entry.

### PUSH

Only run when the Firebase config, sender credential, and current device token are available. Verify token fingerprint locally, never record the raw token. Keep the app in Home through the E02 120-second window, use data-only normal-priority payloads, and retain the real sender/callback IDs. A sender acceptance is not device receipt; receipt is not cache application. If Firebase is unavailable, record B1 and stop at preflight; do not substitute a synthetic accepted or applied event.

### HYBRID / E05 / E06

- E05 checks competing/new signals against the shared Room version guard. Use separate request/signal IDs and preserve overlap/race outcomes.
- E06 uses the server's controlled skip-push fault injection, then observes whether an eligible periodic worker later fetches and applies the server version. A skip is not an FCM delivery failure.
- Keep both rows NOT_RUN unless the actual candidate and required services/devices were exercised. For status and current missing inputs, see [`HYBRID_PILOT.md`](evidence/SEM-36/HYBRID_PILOT.md).

## 5. Fallback and 15-minute presentation

If a live operation has not reached the expected state after **30 seconds**, stop waiting in the presentation and switch to the locally available recorded fallback. Say that the live step was not observed; do not imply that the recording is a live result. Keep the fallback clip accessible offline on the presentation machine and test the transition before presenting. The recorded clip itself must be produced and hashed by SEM-53; no clip is currently included here.

Keep the presentation within the 15-minute plan. Do not extend the live wait or force a background job to save the demonstration.

## 6. Cleanup and recovery

1. Close the observation window and save original manifests/events before cleanup.
2. Wait for active work to finish or keep the run marked contaminated; do not clear Room while workers can still write.
3. Restore the agreed app mode/scheduler state, server baseline, network, battery/idle state, and app foreground/stopped state. Verify no unintended periodic or one-time work remains.
4. Stop only the server process/store created for this run. Do not delete shared or private source data needed for evidence.
5. Re-open the app once and confirm the expected cached version/timeline. Return the device to the default presentation state and check notification tray contents.
6. Export and validate logs. Label any raw Room timeline `legacy-room-v1` until the canonical schema-v2 adapter has been verified; do not feed legacy JSONL to the v2 consumer as if it were v2.

For the Android instrumentation export, invoke `PeriodicPilotControl` with `-e sem29_action export-v2 -e sem29_run_id <run-id>`. It writes `events-v2.jsonl` plus `events-v2-export-report.json`; only rows passing the strict v2 checks enter the JSONL. Keep the raw legacy file and omission report with the run. A `PARTIAL` report is not a complete canonical run export.

## 7. Evidence checklist

For every executed run, retain original manifest/events, build and server commits, APK SHA-256, device alias/OS, mode, versions before/target/after, actual observation window, cleanup state, and commands used. Keep serials, IPs, tokens, credentials, and raw private dumps out of the public evidence. Link the run from the task CHECKS and record failures/unknowns without editing the source logs.
