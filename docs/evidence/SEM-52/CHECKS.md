# SEM-52 CHECKS — APK and demo runbook handoff

**Status: IN PROGRESS / NOT COMPLETE.** The runbook and automatic emulator/USB server routing are prepared. A debug APK and test APK were built with hashes, but device verification and release-candidate gates remain open.

SEM-52 has no start gate in the latest task definition. SEM-37 remains Todo and its candidate manifest is `NOT_READY`; SEM-43 is Todo, SEM-50 is In Progress, and SEM-51 is Todo. These handoff inputs are recorded as pending, not treated as evidence. The runbook documents the current mode/run/device configuration and re-registering PERIODIC after an app upgrade.

| Check | Expected | Actual | Status |
|---|---|---|---|
| Candidate input | Exact candidate manifest and build gate | SEM-37 artifact is explicitly `NOT_READY` | Not run |
| Build and tests | Exact app source build succeeds; unit suite passes | On `321aa7d7a44381cbceeb441d97913f498023730f`, `:app:testDebugUnitTest`, `:app:assembleDebug`, and `:app:assembleDebugAndroidTest` succeeded; 34 tests, 0 failures/errors/skips | Pass |
| APK artifacts | App and instrumentation APKs have recorded SHA-256 and expected package metadata | App: `release/app-debug.apk`, SHA-256 `DBAAD0492E14FC872C66BF7F118704A404EEF6C553F043AE5CA1FE59E6D69414`. Test APK: `release/app-debug-androidTest.apk`, SHA-256 `E0618FB2F41DE1E70F3C0C5A27A10157BA5411314394BC2DB4D03EE80EF7DF75`. App package/version `com.thanhtris.seminarie307` / `0.1.0 (1)`, target SDK 37; APK v2 signature verified | Pass (local build artifacts) |
| Emulator/USB endpoint | Same APK uses emulator host gateway or device loopback behind `adb reverse` | Runtime endpoint selection and unit cases are included in source commit; app uses `10.0.2.2:3000` on emulator and `127.0.0.1:3000` on physical devices | Pass (unit/build); device not run |
| USB GET from app | OPPO timeline shows a successful snapshot GET/apply after `adb reverse` | No `adb` executable, connected device, or OPPO is available in this environment; docs now specify the exact setup and event to verify | Not run |
| Firebase PUSH | Configured build/token and real PUSH flow | `android/app/google-services.json` is absent; no token/credential was read or supplied | Not run (B1) |
| Demo runbook | Setup, mode, live/fallback, cleanup and 30-second switch threshold | [DEMO_RUNBOOK.md](../../DEMO_RUNBOOK.md) documents the endpoint selection and on-device GET verification; candidate-specific values remain gated on manifest | Pass (document prepared) |
| Build manifest | Exact source/config/checksum for built APK | `release/BUILD_MANIFEST.json` records source `321aa7d7a44381cbceeb441d97913f498023730f`, build status, APK paths/hashes, and verification results | Pass |
| Final handoff | SUMMARY, report/claims, and deck/PDF/notes are available | SEM-43 Todo, SEM-50 In Progress, SEM-51 Todo on live Project | Not run |

The local app APK and instrumentation APK are available at `release/app-debug.apk` and `release/app-debug-androidTest.apk`; no GitHub Release or Drive upload was performed. `adb devices` returned no connected device, so the OPPO reverse tunnel and app-originated GET remain unverified. Firebase PUSH remains NOT_RUN because `android/app/google-services.json` is absent; E05/E06 and runtime schema-v2 export are also pending.
