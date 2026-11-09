package com.thanhtris.seminarie307.fcm

import android.content.Context
import android.content.pm.ApplicationInfo
import android.util.Log
import com.google.firebase.FirebaseApp
import com.google.firebase.messaging.FirebaseMessaging
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.data.local.SyncMetadataDao
import com.thanhtris.seminarie307.data.local.SyncMetadataEntity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.io.File
import java.security.MessageDigest
import java.time.Instant

/** Keys in `sync_metadata` used by the FCM registration-token lifecycle (SEM-33). */
object FcmTokenKeys {
    const val TOKEN = "fcmToken"
    const val FINGERPRINT = "fcmTokenFingerprint"
    const val PREVIOUS_FINGERPRINT = "fcmTokenPreviousFingerprint"
    const val UPDATED_AT_UTC = "fcmTokenUpdatedAtUtc"
    const val SOURCE = "fcmTokenSource"
    const val REFRESH_COUNT = "fcmTokenRefreshCount"
    const val STATUS = "fcmTokenStatus"
}

/** Where a token value came from. Stored as a safe code, never the token itself. */
enum class FcmTokenSource { STARTUP, ON_NEW_TOKEN }

/** Safe, token-free status codes shown in docs/CHECKS and metadata. */
enum class FcmTokenStatus { READY, FIREBASE_NOT_CONFIGURED, FETCH_FAILED, INVALID_TOKEN }

sealed interface TokenUpdateResult {
    /** [changed] is false when the token equals the stored one (no rotation). */
    data class Stored(val changed: Boolean, val fingerprint: String) : TokenUpdateResult
    data class Rejected(val status: FcmTokenStatus) : TokenUpdateResult
}

/**
 * Owns the local FCM registration-token lifecycle: validates and stores the token in Room,
 * tracks rotation via a SHA-256 fingerprint, and records safe status codes when Firebase is
 * not configured or token retrieval fails.
 *
 * The raw token is never logged and never put in the timeline/export; only the 16-hex-char
 * [fingerprint] is safe to quote in logs and CHECKS. The sender (SEM-35) reads the token from
 * `FCM_TOKEN_FILE`, see `docs/PUSH.md` for how the debug build exposes it without Logcat.
 */
class FcmTokenManager(
    private val metadataDao: SyncMetadataDao,
    private val nowUtc: () -> Instant = { Instant.now() },
    /** Optional side channel for the developer token file; must not log or throw the token. */
    private val exportToken: (String) -> Unit = {},
) {
    constructor(context: Context) : this(
        metadataDao = AppDatabase.getInstance(context).metadataDao(),
        exportToken = DebugTokenFile(context)::write,
    )

    /** Validates and stores [token]. Returns whether it differs from the previously stored token. */
    suspend fun onTokenAvailable(token: String?, source: FcmTokenSource): TokenUpdateResult {
        if (!isValidToken(token)) {
            metadataDao.setValue(SyncMetadataEntity(FcmTokenKeys.STATUS, FcmTokenStatus.INVALID_TOKEN.name))
            return TokenUpdateResult.Rejected(FcmTokenStatus.INVALID_TOKEN)
        }
        val newToken = token!!
        val newFingerprint = fingerprint(newToken)
        val previousToken = metadataDao.getValue(FcmTokenKeys.TOKEN)
        val previousFingerprint = previousToken?.takeIf { isValidToken(it) }?.let(::fingerprint)
        val changed = previousFingerprint != newFingerprint

        if (changed) {
            metadataDao.setValue(SyncMetadataEntity(FcmTokenKeys.TOKEN, newToken))
            metadataDao.setValue(SyncMetadataEntity(FcmTokenKeys.FINGERPRINT, newFingerprint))
            if (previousFingerprint != null) {
                metadataDao.setValue(SyncMetadataEntity(FcmTokenKeys.PREVIOUS_FINGERPRINT, previousFingerprint))
                val count = metadataDao.getValue(FcmTokenKeys.REFRESH_COUNT)?.toIntOrNull() ?: 0
                metadataDao.setValue(SyncMetadataEntity(FcmTokenKeys.REFRESH_COUNT, (count + 1).toString()))
            }
            metadataDao.setValue(SyncMetadataEntity(FcmTokenKeys.UPDATED_AT_UTC, nowUtc().toString()))
        }
        metadataDao.setValue(SyncMetadataEntity(FcmTokenKeys.SOURCE, source.name))
        metadataDao.setValue(SyncMetadataEntity(FcmTokenKeys.STATUS, FcmTokenStatus.READY.name))
        runCatching { exportToken(newToken) }
        Log.i(TAG, "FCM token stored: source=$source, changed=$changed, fingerprint=$newFingerprint")
        return TokenUpdateResult.Stored(changed, newFingerprint)
    }

    /**
     * Records that no token could be obtained ([FcmTokenStatus.FIREBASE_NOT_CONFIGURED] or
     * [FcmTokenStatus.FETCH_FAILED]). An older stored token is kept but its status becomes
     * non-READY so evidence cannot claim it is the current registration.
     */
    suspend fun onTokenUnavailable(status: FcmTokenStatus) {
        require(status != FcmTokenStatus.READY)
        metadataDao.setValue(SyncMetadataEntity(FcmTokenKeys.STATUS, status.name))
        Log.w(TAG, "FCM token unavailable: status=$status")
    }

    companion object {
        private const val TAG = "FcmTokenManager"
        private const val MAX_TOKEN_LENGTH = 8192

        /** Same shape the sender (`prepareFirebase`) accepts: non-empty, no whitespace, <= 8192 chars. */
        fun isValidToken(token: String?): Boolean =
            !token.isNullOrEmpty() && token.length <= MAX_TOKEN_LENGTH && token.none { it.isWhitespace() }

        /** First 8 bytes of SHA-256 as 16 lowercase hex chars; safe to log, not reversible to the token. */
        fun fingerprint(token: String): String =
            MessageDigest.getInstance("SHA-256")
                .digest(token.toByteArray(Charsets.UTF_8))
                .take(8)
                .joinToString("") { "%02x".format(it) }

        /**
         * Startup path: ask Firebase for the current token. Without `google-services.json`
         * (plugin not applied) Firebase is not initialised and the status is recorded as
         * [FcmTokenStatus.FIREBASE_NOT_CONFIGURED] instead of crashing or using a hardcoded token.
         */
        fun refreshFromFirebase(context: Context) {
            val appContext = context.applicationContext
            val manager = FcmTokenManager(appContext)
            val scope = CoroutineScope(Dispatchers.IO)
            val firebaseApp = runCatching {
                FirebaseApp.getApps(appContext).firstOrNull() ?: FirebaseApp.initializeApp(appContext)
            }.getOrNull()
            if (firebaseApp == null) {
                scope.launch { manager.onTokenUnavailable(FcmTokenStatus.FIREBASE_NOT_CONFIGURED) }
                return
            }
            runCatching {
                FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
                    scope.launch {
                        if (task.isSuccessful) {
                            manager.onTokenAvailable(task.result, FcmTokenSource.STARTUP)
                        } else {
                            // Only a safe code is kept; the exception message may be provider text.
                            manager.onTokenUnavailable(FcmTokenStatus.FETCH_FAILED)
                        }
                    }
                }
            }.onFailure {
                scope.launch { manager.onTokenUnavailable(FcmTokenStatus.FETCH_FAILED) }
            }
        }
    }
}

/**
 * Debug-only developer hand-off of the current token to app-private storage
 * (`files/fcm/device-token.txt`), so a developer can copy it with `adb exec-out run-as` into the
 * git-ignored `FCM_TOKEN_FILE` without ever printing it to Logcat. Release builds never write it
 * and delete any leftover file.
 */
internal class DebugTokenFile(private val context: Context) {
    private val file: File get() = File(File(context.filesDir, "fcm"), FILE_NAME)

    fun write(token: String) {
        val debuggable = (context.applicationInfo.flags and ApplicationInfo.FLAG_DEBUGGABLE) != 0
        if (!debuggable) {
            file.delete()
            return
        }
        file.parentFile?.mkdirs()
        val tmp = File(file.parentFile, "$FILE_NAME.tmp")
        tmp.writeText(token)
        if (!tmp.renameTo(file)) {
            file.delete()
            check(tmp.renameTo(file)) { "token file rename failed" }
        }
    }

    companion object {
        const val FILE_NAME = "device-token.txt"
    }
}
