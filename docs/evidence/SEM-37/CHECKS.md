# SEM-37 CHECKS — candidate freeze

| Check | Expected | Actual | Status |
|---|---|---|---|
| Candidate APK build | APK from the integrated, pinned app source | Not run; SDK platform 37 and Build Tools 36.0.0 are absent | Not run |
| Candidate identity | App/server commits, config, dependency state, APK SHA-256 | No APK for this branch revision | Not run |
| Required pilot evidence | SEM-36 E05/E06, runtime canonical export and push/token evidence | SEM-36 is Todo; SEM-34 E02 is NOT_RUN due Firebase B1; Android `export-v2` is implemented but not run; SEM-33/38 are Done | Not run |
| Candidate manifest | Manifest points to exact artifact and evidence | `release/CANDIDATE_MANIFEST.json` exists as explicit `NOT_READY` with null artifact/checksum | Pass (honest gate artifact) |

**Conclusion:** no candidate is ready; keep the release gate false until the exact-branch APK and pilot evidence exist. This task is owner-assigned to Trung on the live board.
