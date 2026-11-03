package com.thanhtris.seminarie307.sync

import android.content.Context
import android.os.SystemClock
import androidx.work.Constraints
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.workDataOf
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.data.local.TimelineEventEntity
import com.thanhtris.seminarie307.integration.SyncMode
import com.thanhtris.seminarie307.integration.SyncSource
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.withContext
import java.time.Instant
import java.util.UUID
import java.util.concurrent.TimeUnit

class PeriodicSyncScheduler(
    context: Context,
    private val database: AppDatabase = AppDatabase.getInstance(context),
) {
    private val workManager = WorkManager.getInstance(context.applicationContext)

    /** Returns the WorkManager ID only after unique registration is accepted and observable. */
    suspend fun schedulePeriodicSync(
        mode: SyncMode = SyncMode.PERIODIC,
        runId: String = "periodic-run",
        repeatIntervalMinutes: Long = MIN_REPEAT_INTERVAL_MINUTES,
    ): UUID? = withContext(Dispatchers.IO) {
        require(repeatIntervalMinutes >= MIN_REPEAT_INTERVAL_MINUTES) {
            "WorkManager periodic interval must be at least $MIN_REPEAT_INTERVAL_MINUTES minutes"
        }
        require(APP_ID.matches(runId)) { "runId must be a valid experiment run id" }
        require(mode == SyncMode.PERIODIC || mode == SyncMode.HYBRID) {
            "Periodic work is only valid in PERIODIC or HYBRID mode"
        }

        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
        val request = PeriodicWorkRequestBuilder<SyncWorker>(repeatIntervalMinutes, TimeUnit.MINUTES)
            .setConstraints(constraints)
            .setInputData(
                workDataOf(
                    SyncWorker.KEY_SOURCE to SyncSource.PERIODIC.name,
                    SyncWorker.KEY_MODE to mode.name,
                    SyncWorker.KEY_RUN_ID to runId,
                )
            )
            .build()

        workManager.enqueueUniquePeriodicWork(
            PERIODIC_WORK_NAME,
            ExistingPeriodicWorkPolicy.UPDATE,
            request,
        ).result.get()

        val workInfo = workManager.getWorkInfosForUniqueWork(PERIODIC_WORK_NAME)
            .get()
            .firstOrNull { !it.state.isFinished }
            ?: return@withContext null

        recordEvent(
            runId = runId,
            workId = workInfo.id.toString(),
            eventType = "periodic_registered",
            outcome = "registered",
            reason = null,
        )
        workInfo.id
    }

    suspend fun cancelPeriodicSync(runId: String? = null) = withContext(Dispatchers.IO) {
        val workInfo = workManager.getWorkInfosForUniqueWork(PERIODIC_WORK_NAME)
            .get()
            .firstOrNull { !it.state.isFinished }
        workManager.cancelUniqueWork(PERIODIC_WORK_NAME).result.get()
        recordEvent(
            runId = runId,
            workId = workInfo?.id?.toString(),
            eventType = "periodic_cancelled",
            outcome = "cancelled",
            reason = null,
        )
    }

    fun isPeriodicScheduledFlow(): Flow<Boolean> =
        workManager.getWorkInfosForUniqueWorkFlow(PERIODIC_WORK_NAME).map { list ->
            list.any { !it.state.isFinished }
        }

    private suspend fun recordEvent(
        runId: String?,
        workId: String?,
        eventType: String,
        outcome: String,
        reason: String?,
    ) {
        val now = Instant.now()
        database.timelineDao().insert(
            TimelineEventEntity(
                eventId = UUID.randomUUID().toString(),
                source = SyncSource.PERIODIC.name,
                eventType = eventType,
                occurredAtEpochMillis = now.toEpochMilli(),
                occurredAtUtc = now.toString(),
                runId = runId,
                version = null,
                outcome = outcome,
                reason = reason,
                requestId = null,
                workId = workId,
                messageId = null,
                elapsedRealtimeMillis = SystemClock.elapsedRealtime(),
            )
        )
    }

    companion object {
        const val PERIODIC_WORK_NAME = "periodic_bulletin_sync"
        const val MIN_REPEAT_INTERVAL_MINUTES = 15L
        private val APP_ID = Regex("^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
    }
}
