# SEM-37 CHECKS — candidate freeze

| Check | Expected | Actual | Status |
|---|---|---|---|
| Candidate APK build | APK from the integrated, pinned app source | Repo owner reports `assembleDebug` and `assembleDebugAndroidTest` passed at review head `051f6b0`; latest unit-test fix has not been rerun. No APK/checksum was handed off | Partial; candidate not ready |
| Candidate identity | App/server commits, config, dependency state, APK SHA-256 | No APK for this branch revision | Not run |
| Required pilot evidence | SEM-36 E05/E06, runtime canonical export and push/token evidence | SEM-36 is Todo; SEM-34 E02 is NOT_RUN due Firebase B1; Android `export-v2` is implemented but not run; SEM-33/38 are Done | Not run |
| Candidate manifest | Manifest points to exact artifact and evidence | `release/CANDIDATE_MANIFEST.json` exists as explicit `NOT_READY` with null artifact/checksum | Pass (honest gate artifact) |

Current branch after rebasing on `main` `c77772e426c00ae464240f00942f8368c638aaa8`: app source pinned as `9e7e55b76c646ff113a152022cc23317a202e533`; server source is unchanged from base. Repo owner reports `:app:assembleDebug` and `:app:assembleDebugAndroidTest` passed on review head `051f6b0`, while unit tests were 31/32. This follow-up corrects the stale request-ID assertion; the final unit suite has not been rerun. A local attempt with `ANDROID_HOME=D:\Android\Sdk` and Windows/JDK 17.0.20.1 stops before compilation because licenses for `platforms;android-37.0` and `build-tools;36.0.0` are not accepted. No APK/checksum was handed off.

**Conclusion:** no candidate is ready; keep the release gate false until the exact-branch APK and pilot evidence exist. The candidate manifest pins the current source while leaving artifact/checksum fields empty. This task is owner-assigned to Trung on the live board.
