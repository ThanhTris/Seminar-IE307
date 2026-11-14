# SEM-37 CHECKS — candidate freeze

| Check | Expected | Actual | Status |
|---|---|---|---|
| Candidate APK build | APK from the integrated, pinned app source | Not run; SDK platform 37 and Build Tools 36.0.0 are absent | Not run |
| Candidate identity | App/server commits, config, dependency state, APK SHA-256 | No APK for this branch revision | Not run |
| Required pilot evidence | SEM-36 E05/E06, runtime canonical export and push/token evidence | SEM-36 is Todo; SEM-34 E02 is NOT_RUN due Firebase B1; Android `export-v2` is implemented but not run; SEM-33/38 are Done | Not run |
| Candidate manifest | Manifest points to exact artifact and evidence | `release/CANDIDATE_MANIFEST.json` exists as explicit `NOT_READY` with null artifact/checksum | Pass (honest gate artifact) |

Current branch after rebasing on `main` `c77772e426c00ae464240f00942f8368c638aaa8`: app source pinned as `9e7e55b76c646ff113a152022cc23317a202e533`; server source is unchanged from base. Attempted `:app:testDebugUnitTest :app:assembleDebug :app:assembleDebugAndroidTest` with `ANDROID_HOME=D:\Android\Sdk` and Windows/JDK 17.0.20.1; Gradle stopped before compilation because licenses for `platforms;android-37.0` and `build-tools;36.0.0` are not accepted. No source was compiled.

**Conclusion:** no candidate is ready; keep the release gate false until the exact-branch APK and pilot evidence exist. The candidate manifest pins the current source while leaving artifact/checksum fields empty. This task is owner-assigned to Trung on the live board.
