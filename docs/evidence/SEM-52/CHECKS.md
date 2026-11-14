# SEM-52 CHECKS — APK and demo runbook handoff

**Status: IN PROGRESS / NOT COMPLETE.** The runbook is prepared. No APK exists for this branch revision, so a release build manifest cannot claim a built artifact.

SEM-52 has no start gate in the latest task definition. SEM-37 remains Todo and its candidate manifest is `NOT_READY`; SEM-43 is Todo, SEM-50 is In Progress, and SEM-51 is Todo. These handoff inputs are recorded as pending, not treated as evidence. The runbook documents the current mode/run/device configuration and re-registering PERIODIC after an app upgrade.

| Check | Expected | Actual | Status |
|---|---|---|---|
| Candidate input | Exact candidate manifest and build gate | SEM-37 artifact is explicitly `NOT_READY` | Not run |
| Build APK | APK from the pinned candidate source with SHA-256 | Not built; current host has no `ANDROID_HOME` and no SDK at `%LOCALAPPDATA%\Android\Sdk`; Gradle cannot locate SDK before compilation | Not run |
| Demo runbook | Setup, mode, live/fallback, cleanup and 30-second switch threshold | [DEMO_RUNBOOK.md](../../DEMO_RUNBOOK.md) drafted; candidate-specific values clearly gated on manifest | Pass (document prepared) |
| Build manifest | Exact source/config/checksum for built APK | `release/BUILD_MANIFEST.json` pins source `5fb52bbbf45c165b2168237b9fb1fbe04bc80d5d`, status `NOT_BUILT`, with null artifact fields | Pass (honest gate artifact) |
| Final handoff | SUMMARY, report/claims, and deck/PDF/notes are available | SEM-43 Todo, SEM-50 In Progress, SEM-51 Todo on live Project | Not run |

No APK or checksum is claimed. Build the candidate, populate the manifest, and complete final handoff after the Android SDK/build and upstream evidence are available.
