package com.thanhtris.seminarie307.sync

import android.content.Context
import android.os.SystemClock
import androidx.work.Constraints
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.workDataOf
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.data.local.TimelineEventEntity
import com.thanhtris.seminarie307.integration.SyncMode
import com.thanhtris.seminarie307.integration.JsonStringArrayCodec
import com.thanhtris.seminarie307.integration.SyncSource
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.time.Instant
import java.util.UUID

/** Shared entry point for one-time MANUAL/PUSH and unique PERIODIC sync work. */
class SyncWorkEnqueuer(
    context: Context,
    private val database: AppDatabase = AppDatabase.getInstance(context),
) {
    private val appContext = context.applicationContext
    private val workManager = WorkManager.getInstance(appContext)

    /** Returns the actual WorkManager ID after the enqueue/registration operation completes. */
    suspend fun enqueue(input: SyncInput, repeatIntervalMinutes: Long = PeriodicSyncScheduler.MIN_REPEAT_INTERVAL_MINUTES): UUID? =
        withContext(Dispatchers.IO) {
            require(APP_ID.matches(input.runId)) { "runId must be a valid experiment run id" }
            require(APP_ID.matches(input.deviceAlias)) { "deviceAlias must be a valid experiment device alias" }
            require(modeAllows(input.source, input.mode)) { "Trigger is disabled in the requested mode" }

            if (input.source == SyncSource.PERIODIC) {
                return@withContext PeriodicSyncScheduler(appContext, database)
                    .schedulePeriodicSync(input.mode, input.runId, input.deviceAlias, repeatIntervalMinutes)
            }

            val requestId = input.correlation.requestId
                ?.takeIf { APP_ID.matches(it) }
                ?: throw IllegalArgumentException("MANUAL/PUSH sync requires a valid request ID")
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()
            val request = OneTimeWorkRequestBuilder<SyncWorker>()
                .setConstraints(constraints)
                .addTag(SyncWorker.SYNC_WORK_TAG)
                .addTag(SyncWorker.ONE_TIME_SYNC_WORK_TAG)
                .setInputData(
                    workDataOf(
                        SyncWorker.KEY_SOURCE to input.source.name,
                        SyncWorker.KEY_MODE to input.mode.name,
                        SyncWorker.KEY_RUN_ID to input.runId,
                        SyncWorker.KEY_DEVICE_ALIAS to input.deviceAlias,
                        SyncWorker.KEY_SIGNAL_IDS to input.signalIds.joinToString(","),
                        SyncWorker.KEY_REQUEST_ID to requestId,
                        SyncWorker.KEY_MESSAGE_ID to input.correlation.messageId,
                        SyncWorker.KEY_VERSION_HINT to (input.versionHint ?: -1L),
                    )
                )
                .build()

            workManager.enqueue(request).result.get()
            val now = Instant.now()
            database.timelineDao().insert(
                TimelineEventEntity(
                    eventId = UUID.randomUUID().toString(),
                    source = input.source.name,
                    eventType = "work_enqueued",
                    occurredAtEpochMillis = now.toEpochMilli(),
                    occurredAtUtc = now.toString(),
                    runId = input.runId,
                    version = null,
                    outcome = "enqueued",
                    reason = null,
                    requestId = requestId,
                    workId = request.id.toString(),
                    messageId = input.correlation.messageId,
                    elapsedRealtimeMillis = SystemClock.elapsedRealtime(),
                    mode = input.mode.name,
                    deviceAlias = input.deviceAlias,
                    cachedVersion = database.metadataDao().getValue("cachedVersion")?.toLongOrNull(),
                    versionHint = input.versionHint,
                    signalIdsJson = JsonStringArrayCodec.encode(input.signalIds),
                )
            )
            request.id
        }

    private fun modeAllows(source: SyncSource, mode: SyncMode): Boolean = when (source) {
        SyncSource.MANUAL -> true
        SyncSource.PERIODIC -> mode == SyncMode.PERIODIC || mode == SyncMode.HYBRID
        SyncSource.PUSH -> mode == SyncMode.PUSH || mode == SyncMode.HYBRID
    }

    companion object {
        private val APP_ID = Regex("^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
    }
}
