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
| Android candidate build | Not run on source `5fb52bbbf45c165b2168237b9fb1fbe04bc80d5d`: Gradle stopped before compilation because `ANDROID_HOME` is unset and `%LOCALAPPDATA%\Android\Sdk` is absent |
| APK and SHA-256 | Not available; no candidate artifact |
| Main-run manifest | Not created; no measurements are being represented as real |

The manifest pins app source `5fb52bbbf45c165b2168237b9fb1fbe04bc80d5d` and server source `c77772e426c00ae464240f00942f8368c638aaa8`, but is explicitly `NOT_READY` with no APK path/hash. Do not distribute it as a candidate. Populate the fields only after an exact-revision build and required run evidence are available.
