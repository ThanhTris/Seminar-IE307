# SEM-37 — Candidate gate

**Status: NOT READY / NOT RUN.** This file does not declare a release candidate. See [`release/CANDIDATE_MANIFEST.json`](../../../release/CANDIDATE_MANIFEST.json) for the machine-readable gate result.

## Required before candidate freeze

- SEM-36 completed, including E05/E06 pilot evidence.
- SEM-33 token lifecycle handoff and SEM-38 push policy handoff (both Done on the live board).
- Build the exact candidate APK, record app/server commits and dependency/config state, then calculate APK SHA-256.
- Run the required pilot checks against that exact candidate and archive the original artifacts.

## Current state

| Requirement | State |
|---|---|
| SEM-36 integration/pilot | Todo; mode code/docs and strict schema-v2 serializer prepared; E05/E06 pilots and runtime export Not run |
| SEM-33 token lifecycle | Done on live board |
| SEM-38 push policy | Done on live board |
| Android build | `:app:testDebugUnitTest`, `:app:assembleDebug`, and `:app:assembleDebugAndroidTest` pass on `321aa7d7a44381cbceeb441d97913f498023730f`; 34/34 unit tests pass |
| Debug APK and SHA-256 | `release/app-debug.apk`; `DBAAD0492E14FC872C66BF7F118704A404EEF6C553F043AE5CA1FE59E6D69414` |
| Device verification | Not run; `adb devices` returned no devices, so OPPO USB route is documented but not confirmed from the app |
| Main-run manifest | Not created; no measurements are being represented as real |

The manifest records app source `321aa7d7a44381cbceeb441d97913f498023730f` and server source `c77772e426c00ae464240f00942f8368c638aaa8`. A debug APK and checksum now exist, but candidate status remains `NOT_READY` until device verification, Firebase/PUSH availability, E05/E06 pilots, and required run evidence are addressed. Do not present this debug build as a completed candidate.
