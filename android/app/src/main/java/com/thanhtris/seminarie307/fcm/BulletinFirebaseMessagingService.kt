package com.thanhtris.seminarie307.fcm

import android.util.Log
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.workDataOf
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.data.local.SyncMetadataEntity
import com.thanhtris.seminarie307.data.local.TimelineEventEntity
import com.thanhtris.seminarie307.integration.SyncMode
import com.thanhtris.seminarie307.integration.SyncSource
import com.thanhtris.seminarie307.sync.SyncWorker
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.time.Instant
import java.util.UUID

class BulletinFirebaseMessagingService : FirebaseMessagingService() {

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)

        val data = remoteMessage.data
        val messageId = remoteMessage.messageId
        val runId = data["run_id"] ?: "push-run-default"
        val requestId = data["request_id"] ?: "req-${UUID.randomUUID()}"
        val modeStr = data["mode"] ?: SyncMode.PUSH.name
        val versionHintStr = data["version_hint"]
        val versionHint = versionHintStr?.toLongOrNull()

        val mode = runCatching { SyncMode.valueOf(modeStr) }.getOrDefault(SyncMode.PUSH)
        val now = Instant.now()
        val database = AppDatabase.getInstance(applicationContext)
        val timelineDao = database.timelineDao()

        // 1. Record push_received event immediately
        CoroutineScope(Dispatchers.IO).launch {
            timelineDao.insert(
                TimelineEventEntity(
                    eventId = UUID.randomUUID().toString(),
                    source = SyncSource.PUSH.name,
                    eventType = "push_received",
                    occurredAtEpochMillis = now.toEpochMilli(),
                    occurredAtUtc = now.toString(),
                    runId = runId,
                    version = versionHint,
                    outcome = "received",
                    reason = "Đã nhận silent push data-only qua FCM callback",
                    requestId = requestId,
                    workId = null,
                    messageId = messageId,
                )
            )

            // 2. Enqueue WorkManager SyncWorker (do not run long sync in callback)
            val workRequest = OneTimeWorkRequestBuilder<SyncWorker>()
                .setInputData(
                    workDataOf(
                        SyncWorker.KEY_SOURCE to SyncSource.PUSH.name,
                        SyncWorker.KEY_MODE to mode.name,
                        SyncWorker.KEY_RUN_ID to runId,
                        SyncWorker.KEY_REQUEST_ID to requestId,
                        SyncWorker.KEY_MESSAGE_ID to messageId,
                        SyncWorker.KEY_VERSION_HINT to (versionHint ?: -1L),
                    )
                )
                .build()

            // 3. Record work_enqueued event
            val enqueuedNow = Instant.now()
            timelineDao.insert(
                TimelineEventEntity(
                    eventId = UUID.randomUUID().toString(),
                    source = SyncSource.PUSH.name,
                    eventType = "work_enqueued",
                    occurredAtEpochMillis = enqueuedNow.toEpochMilli(),
                    occurredAtUtc = enqueuedNow.toString(),
                    runId = runId,
                    version = versionHint,
                    outcome = "accepted",
                    reason = "Đã xếp lịch OneTimeWorkRequest cho PUSH sync",
                    requestId = requestId,
                    workId = workRequest.id.toString(),
                    messageId = messageId,
                )
            )

            WorkManager.getInstance(applicationContext).enqueue(workRequest)
        }
    }

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.i(TAG, "New FCM Token received: $token")
        val database = AppDatabase.getInstance(applicationContext)
        CoroutineScope(Dispatchers.IO).launch {
            database.metadataDao().setValue(SyncMetadataEntity("fcmToken", token))
        }
    }

    companion object {
        private const val TAG = "BulletinFCM"
    }
}
