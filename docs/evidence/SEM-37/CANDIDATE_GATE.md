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
| Android candidate build | Repo owner reports `assembleDebug` and `assembleDebugAndroidTest` passed on review head `051f6b0`; unit tests were 31/32 with one stale assertion, now corrected in a follow-up. Current workstation cannot rerun because platform 37 / Build Tools 36 licenses are not accepted |
| APK and SHA-256 | Not available; no candidate artifact |
| Main-run manifest | Not created; no measurements are being represented as real |

The manifest pins app source `9e7e55b76c646ff113a152022cc23317a202e533` and server source `c77772e426c00ae464240f00942f8368c638aaa8`, but is explicitly `NOT_READY`: no APK/checksum was handed off, the latest unit-test assertion fix has not been rerun, and required run evidence is absent. Do not distribute it as a candidate.
