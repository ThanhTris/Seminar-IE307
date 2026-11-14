package com.thanhtris.seminarie307.fcm

import android.content.Context
import android.os.SystemClock
import android.util.Log
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.data.local.SyncMetadataDao
import com.thanhtris.seminarie307.data.local.SyncMetadataEntity
import com.thanhtris.seminarie307.data.local.TimelineDao
import com.thanhtris.seminarie307.data.local.TimelineEventEntity
import com.thanhtris.seminarie307.integration.CorrelationUi
import com.thanhtris.seminarie307.integration.JsonStringArrayCodec
import com.thanhtris.seminarie307.integration.SyncMode
import com.thanhtris.seminarie307.integration.SyncModeController
import com.thanhtris.seminarie307.integration.SyncSource
import com.thanhtris.seminarie307.sync.SyncInput
import com.thanhtris.seminarie307.sync.SyncWorkEnqueuer
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import java.time.Instant
import java.util.UUID

sealed interface PushProcessingResult {
    data class Enqueued(val workId: String, val requestId: String, val runId: String) : PushProcessingResult
    data class Rejected(val reason: String, val runId: String? = null) : PushProcessingResult
    data class Ignored(val reason: String) : PushProcessingResult
}

/**
 * Adapter that processes FCM incoming push payloads, enforces the silent push (data-only)
 * contract, records observed push receipt and validation outcomes, and delegates work scheduling
 * to the shared [SyncWorkEnqueuer].
 */
class PushSyncEnqueueAdapter(
    private val timelineDao: TimelineDao,
    private val metadataDao: SyncMetadataDao,
    private val enqueueWork: suspend (SyncInput) -> UUID?,
) {
    /** Secondary constructor using [AppDatabase] and [SyncWorkEnqueuer]. */
    constructor(
        database: AppDatabase,
        enqueuer: SyncWorkEnqueuer,
    ) : this(
        timelineDao = database.timelineDao(),
        metadataDao = database.metadataDao(),
        enqueueWork = { input -> enqueuer.enqueue(input) },
    )

    /** Convenient Android [Context] constructor for runtime service injection. */
    constructor(context: Context) : this(
        AppDatabase.getInstance(context),
        SyncWorkEnqueuer(context),
    )

    /**
     * Parses, validates, and dispatches an incoming push notification payload.
     *
     * In accordance with SEM-15, SEM-32 and SEM-38:
     * 1. Data-only enforcement: Rejects payloads with notification blocks (not silent push).
     * 2. Rejects empty payload maps.
     * 3. Validates correlation IDs (run_id, request_id, version_hint). Missing/invalid run_id
     *    is rejected without creating false experiment run events.
     * 4. Always records [push_received] in Room when runId is valid.
     * 5. Checks mode compatibility: If current device mode disables push (e.g. PERIODIC mode),
     *    records [trigger_rejected] with reason "MODE_DISABLED" and halts.
     * 6. Input policy ([PushInputPolicy]): an exact redelivery (same run + signal_id or FCM
     *    message_id already enqueued) records [trigger_rejected] with reason "DUPLICATE_SIGNAL"
     *    and does not enqueue again. An old/equal/lower version_hint is NOT a reason to drop:
     *    the worker still fetches the current snapshot and the core version guard decides.
     *    A new signal while a worker is running is always enqueued.
     * 7. Offloads actual fetch work to WorkManager via [enqueueWork], returning immediately.
     */
    suspend fun processPushPayload(
        data: Map<String, String>,
        messageId: String? = null,
        hasNotificationPayload: Boolean = false,
    ): PushProcessingResult = withContext(Dispatchers.IO) {
        // 1. Strict silent push check: Must be data-only
        if (hasNotificationPayload) {
            Log.w(TAG, "Rejecting push message: contains UI notification payload, violating silent push contract.")
            return@withContext PushProcessingResult.Ignored("NOTIFICATION_PAYLOAD_NOT_ALLOWED")
        }

        // 2. Data payload cannot be empty
        if (data.isEmpty()) {
            Log.w(TAG, "Ignoring push message: payload data is empty.")
            return@withContext PushProcessingResult.Ignored("EMPTY_DATA_PAYLOAD")
        }

        // 3. Extract and validate run_id
        val runId = data["run_id"]
        if (runId.isNullOrBlank() || !APP_ID_PATTERN.matches(runId)) {
            Log.w(TAG, "Rejecting push message: missing or invalid run_id: '$runId'")
            return@withContext PushProcessingResult.Rejected("INVALID_PAYLOAD", runId = null)
        }

        // 4. Parse correlation fields
        val versionHint = data["version_hint"]?.toLongOrNull()?.takeIf { it >= 0 }
        val rawRequestId = data["request_id"]
        val requestId = if (!rawRequestId.isNullOrBlank() && APP_ID_PATTERN.matches(rawRequestId)) {
            rawRequestId
        } else {
            "req-${UUID.randomUUID()}"
        }

        val now = Instant.now()
        val elapsedRealtime = SystemClock.elapsedRealtime()
        val currentDeviceMode = metadataDao.getValue(SyncModeController.KEY_MODE)
            ?.let { runCatching { SyncMode.valueOf(it) }.getOrNull() }
        val payloadMode = data["mode"]?.let { runCatching { SyncMode.valueOf(it) }.getOrNull() }
        val deviceAlias = metadataDao.getValue(SyncModeController.KEY_DEVICE_ALIAS)?.takeIf(APP_ID_PATTERN::matches)
        val signalId = data["signal_id"]?.takeIf(APP_ID_PATTERN::matches)
        val cachedVersion = metadataDao.getValue("cachedVersion")?.toLongOrNull()

        if (currentDeviceMode == null || deviceAlias == null) {
            recordTriggerRejected(
                runId = runId,
                versionHint = versionHint,
                requestId = requestId,
                messageId = messageId,
                reason = "RUN_CONFIG_NOT_READY",
                mode = currentDeviceMode,
                deviceAlias = deviceAlias,
                signalIds = listOfNotNull(signalId),
            )
            return@withContext PushProcessingResult.Rejected("RUN_CONFIG_NOT_READY", runId = runId)
        }

        val targetMode = if (payloadMode == SyncMode.PUSH || payloadMode == SyncMode.HYBRID) {
            payloadMode
        } else {
            currentDeviceMode
        }

        // 5. Record observed push_received event in Room (also for duplicates: the callback did happen)
        timelineDao.insert(
            TimelineEventEntity(
                eventId = UUID.randomUUID().toString(),
                source = SyncSource.PUSH.name,
                eventType = "push_received",
                occurredAtEpochMillis = now.toEpochMilli(),
                occurredAtUtc = now.toString(),
                runId = runId,
                version = null,
                outcome = "received",
                reason = null,
                requestId = null,
                workId = null,
                messageId = messageId,
                elapsedRealtimeMillis = elapsedRealtime,
                mode = targetMode.name,
                deviceAlias = deviceAlias,
                cachedVersion = cachedVersion,
                versionHint = versionHint,
                signalIdsJson = JsonStringArrayCodec.encode(listOfNotNull(signalId)),
            )
        )

        // 6. Check active mode allowance
        val pushAllowed = currentDeviceMode == SyncMode.PUSH || currentDeviceMode == SyncMode.HYBRID
        if (!pushAllowed) {
            Log.w(TAG, "Trigger rejected: push is disabled in active mode $currentDeviceMode for run $runId")
            recordTriggerRejected(runId, versionHint, requestId, messageId, "MODE_DISABLED", targetMode, deviceAlias, listOfNotNull(signalId))
            return@withContext PushProcessingResult.Rejected("MODE_DISABLED", runId = runId)
        }

        // 7. Enqueue one-time SyncWorker with network constraint via shared enqueuer
        val syncInput = SyncInput(
            source = SyncSource.PUSH,
            mode = targetMode,
            runId = runId,
            deviceAlias = deviceAlias,
            versionHint = versionHint,
            signalIds = listOfNotNull(signalId),
            correlation = CorrelationUi(
                requestId = requestId,
                messageId = messageId,
            ),
        )

        // SEM-38 input policy. The lock covers "check ledger -> enqueue -> record ledger" so two
        // concurrent callbacks for the same signal cannot both enqueue; different signals only
        // wait for the short ledger/enqueue step, never for a running worker.
        val dedupeKeys = PushInputPolicy.keysFor(runId, signalId, messageId)
        return@withContext ledgerLock.withLock {
            val ledger = PushInputPolicy.parseLedger(metadataDao.getValue(PushInputPolicy.LEDGER_KEY))
            if (PushInputPolicy.isDuplicate(ledger, dedupeKeys)) {
                Log.i(TAG, "Duplicate push signal for run $runId: not enqueued again")
                recordTriggerRejected(
                    runId, versionHint, requestId, messageId, PushInputPolicy.REASON_DUPLICATE_SIGNAL,
                    targetMode, deviceAlias, listOfNotNull(signalId),
                )
                return@withLock PushProcessingResult.Rejected(PushInputPolicy.REASON_DUPLICATE_SIGNAL, runId = runId)
            }

            try {
                val workId = enqueueWork(syncInput)
                if (workId != null) {
                    // Only a successful enqueue is remembered, so a failed one can be retried with the same signal_id.
                    if (dedupeKeys.isNotEmpty()) {
                        metadataDao.setValue(
                            SyncMetadataEntity(PushInputPolicy.LEDGER_KEY, PushInputPolicy.record(ledger, dedupeKeys))
                        )
                    }
                    Log.i(TAG, "Push sync successfully enqueued: workId=$workId, requestId=$requestId, runId=$runId")
                    PushProcessingResult.Enqueued(workId.toString(), requestId, runId)
                } else {
                    Log.e(TAG, "WorkManager failed to enqueue push sync request for run $runId")
                    PushProcessingResult.Rejected("WORK_ENQUEUE_FAILED", runId = runId)
                }
            } catch (e: Exception) {
                Log.e(TAG, "Exception while enqueuing push sync for run $runId", e)
                PushProcessingResult.Rejected(e.message ?: "ENQUEUE_EXCEPTION", runId = runId)
            }
        }
    }

    private suspend fun recordTriggerRejected(
        runId: String,
        versionHint: Long?,
        requestId: String?,
        messageId: String?,
        reason: String,
        mode: SyncMode?,
        deviceAlias: String?,
        signalIds: List<String> = emptyList(),
    ) {
        val rejectNow = Instant.now()
        timelineDao.insert(
            TimelineEventEntity(
                eventId = UUID.randomUUID().toString(),
                source = SyncSource.PUSH.name,
                eventType = "trigger_rejected",
                occurredAtEpochMillis = rejectNow.toEpochMilli(),
                occurredAtUtc = rejectNow.toString(),
                runId = runId,
                version = null,
                outcome = "rejected",
                reason = reason,
                requestId = requestId,
                workId = null,
                messageId = messageId,
                elapsedRealtimeMillis = SystemClock.elapsedRealtime(),
                mode = mode?.name,
                deviceAlias = deviceAlias,
                cachedVersion = metadataDao.getValue("cachedVersion")?.toLongOrNull(),
                versionHint = versionHint,
                signalIdsJson = JsonStringArrayCodec.encode(signalIds),
            )
        )
    }

    companion object {
        private const val TAG = "PushSyncEnqueueAdapter"
        val APP_ID_PATTERN = Regex("^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")

        /** Shared by all adapter instances in the process; the ledger itself is persisted in Room. */
        private val ledgerLock = Mutex()
    }
}
