package com.thanhtris.seminarie307.sync

import android.content.Context
import androidx.work.Constraints
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkInfo
import androidx.work.WorkManager
import androidx.work.workDataOf
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.data.local.TimelineEventEntity
import com.thanhtris.seminarie307.integration.SyncMode
import com.thanhtris.seminarie307.integration.SyncSource
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.time.Instant
import java.util.UUID
import java.util.concurrent.TimeUnit

class PeriodicSyncScheduler(
    private val context: Context,
    private val database: AppDatabase = AppDatabase.getInstance(context),
) {
    private val workManager = WorkManager.getInstance(context)

    fun schedulePeriodicSync(
        mode: SyncMode = SyncMode.PERIODIC,
        runId: String = "periodic-run",
        repeatIntervalMinutes: Long = 15L,
    ) {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        val periodicRequest = PeriodicWorkRequestBuilder<SyncWorker>(
            repeatIntervalMinutes,
            TimeUnit.MINUTES,
        )
            .setConstraints(constraints)
            .setInputData(
                workDataOf(
                    SyncWorker.KEY_SOURCE to SyncSource.PERIODIC.name,
                    SyncWorker.KEY_MODE to mode.name,
                    SyncWorker.KEY_RUN_ID to runId,
                )
            )
            .build()

        // 1. Enqueue unique periodic work
        workManager.enqueueUniquePeriodicWork(
            PERIODIC_WORK_NAME,
            ExistingPeriodicWorkPolicy.UPDATE,
            periodicRequest,
        )

        // 2. Record schedule event in local timeline
        val now = Instant.now()
        val timelineDao = database.timelineDao()
        kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).run {
            val event = TimelineEventEntity(
                eventId = UUID.randomUUID().toString(),
                source = SyncSource.PERIODIC.name,
                eventType = "periodic_scheduled",
                occurredAtEpochMillis = now.toEpochMilli(),
                occurredAtUtc = now.toString(),
                runId = runId,
                version = null,
                outcome = "scheduled",
                reason = "Đã xếp lịch PeriodicWorkRequest (${repeatIntervalMinutes} phút)",
                requestId = null,
                workId = periodicRequest.id.toString(),
                messageId = null,
            )
            kotlinx.coroutines.runBlocking {
                timelineDao.insert(event)
            }
        }
    }

    fun cancelPeriodicSync() {
        workManager.cancelUniqueWork(PERIODIC_WORK_NAME)

        val now = Instant.now()
        val timelineDao = database.timelineDao()
        kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).run {
            val event = TimelineEventEntity(
                eventId = UUID.randomUUID().toString(),
                source = SyncSource.PERIODIC.name,
                eventType = "periodic_cancelled",
                occurredAtEpochMillis = now.toEpochMilli(),
                occurredAtUtc = now.toString(),
                runId = null,
                version = null,
                outcome = "cancelled",
                reason = "Đã hủy lịch PeriodicWorkRequest",
                requestId = null,
                workId = null,
                messageId = null,
            )
            kotlinx.coroutines.runBlocking {
                timelineDao.insert(event)
            }
        }
    }

    fun isPeriodicScheduledFlow(): Flow<Boolean> {
        return workManager.getWorkInfosForUniqueWorkFlow(PERIODIC_WORK_NAME).map { list ->
            list.any { !it.state.isFinished }
        }
    }

    companion object {
        const val PERIODIC_WORK_NAME = "periodic_bulletin_sync"
    }
}
