package com.thanhtris.seminarie307.fcm

import android.util.Log
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * FCM Service handling incoming data-only push notifications for background sync.
 *
 * Implements SEM-15 / SEM-32 requirements:
 * 1. Strictly processes data-only messages (silent push), discarding messages with notification blocks.
 * 2. Immediately delegates payload extraction and validation to [PushSyncEnqueueAdapter],
 *    preventing long-running network operations directly within the callback.
 * 3. Enforces normal priority push handling without displaying any foreground/tray notification.
 * 4. Preserves correlation IDs (run_id, request_id, version_hint, message_id).
 *
 * SEM-33: [onNewToken] delegates to [FcmTokenManager], which stores the refreshed token and
 * never logs its raw value.
 */
class BulletinFirebaseMessagingService : FirebaseMessagingService() {

    private val adapter by lazy {
        PushSyncEnqueueAdapter(applicationContext)
    }

    private val tokenManager by lazy {
        FcmTokenManager(applicationContext)
    }

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)

        val hasNotification = remoteMessage.notification != null
        val data = remoteMessage.data
        val messageId = remoteMessage.messageId

        Log.d(TAG, "FCM message received: messageId=$messageId, dataKeys=${data.keys}, hasNotification=$hasNotification")

        // Offload payload processing to background IO scope to exit callback immediately (< 50ms)
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val result = adapter.processPushPayload(
                    data = data,
                    messageId = messageId,
                    hasNotificationPayload = hasNotification,
                )
                Log.i(TAG, "Processed FCM push message: outcome=$result")
            } catch (e: Exception) {
                Log.e(TAG, "Unhandled error in FCM push callback processing", e)
            }
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        // SEM-33: never log the raw token; FcmTokenManager logs only its fingerprint.
        CoroutineScope(Dispatchers.IO).launch {
            try {
                tokenManager.onTokenAvailable(token, FcmTokenSource.ON_NEW_TOKEN)
            } catch (e: Exception) {
                Log.e(TAG, "Failed to store refreshed FCM token", e)
            }
        }
    }

    companion object {
        private const val TAG = "BulletinFCM"
    }
}
