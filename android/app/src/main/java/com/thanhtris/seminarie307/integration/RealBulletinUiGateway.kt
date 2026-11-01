package com.thanhtris.seminarie307.integration

import android.content.Context
import android.os.SystemClock
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.workDataOf
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.data.local.SyncMetadataEntity
import com.thanhtris.seminarie307.data.local.TimelineEventEntity
import com.thanhtris.seminarie307.sync.SyncWorker
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import java.time.Instant
import java.util.UUID

class RealBulletinUiGateway(
    private val context: Context,
    private val database: AppDatabase = AppDatabase.getInstance(context),
) : BulletinUiGateway {

    private val bulletinDao = database.bulletinDao()
    private val timelineDao = database.timelineDao()
    private val metadataDao = database.metadataDao()

    override val state: Flow<BulletinUiState> = combine(
        bulletinDao.observeAll(),
        timelineDao.observeAll(),
        metadataDao.observeValue("cachedVersion"),
        metadataDao.observeValue("lastSyncAtUtc"),
        metadataDao.observeValue("mode"),
    ) { items, events, cachedVersionStr, lastSyncAtUtc, modeStr ->
        val version = cachedVersionStr?.toLongOrNull() ?: items.firstOrNull()?.version
        val mode = modeStr?.let { runCatching { SyncMode.valueOf(it) }.getOrNull() } ?: SyncMode.HYBRID
        val activeRun = "run-manual-live"

        BulletinUiState(
            cachedVersion = version,
            mode = mode,
            activeRunId = activeRun,
            lastSyncAtUtc = lastSyncAtUtc,
            snapshot = items.map { it.toBulletinItem() },
            timeline = events.map { it.toTimelineEvent() },
            manualAvailable = true,
        )
    }

    override suspend fun enqueueManual(context: ManualSyncContext): ManualEnqueueResult {
        val requestId = "req-${UUID.randomUUID()}"
        val workRequest = OneTimeWorkRequestBuilder<SyncWorker>()
            .setInputData(
                workDataOf(
                    SyncWorker.KEY_SOURCE to SyncSource.MANUAL.name,
                    SyncWorker.KEY_MODE to context.mode.name,
                    SyncWorker.KEY_RUN_ID to context.runId,
                    SyncWorker.KEY_REQUEST_ID to requestId,
                )
            )
            .build()

        // 1. Record work_enqueued event before or at enqueue
        val now = Instant.now()
        val elapsedRealtime = SystemClock.elapsedRealtime()
        timelineDao.insert(
            TimelineEventEntity(
                eventId = UUID.randomUUID().toString(),
                source = SyncSource.MANUAL.name,
                eventType = "work_enqueued",
                occurredAtEpochMillis = now.toEpochMilli(),
                occurredAtUtc = now.toString(),
                runId = context.runId,
                version = bulletinDao.getLatestVersion(),
                outcome = "accepted",
                reason = "Đã xếp lịch OneTimeWorkRequest cho MANUAL sync",
                requestId = requestId,
                workId = workRequest.id.toString(),
                messageId = null,
                elapsedRealtimeMillis = elapsedRealtime,
            )
        )

        // 2. Enqueue via WorkManager
        WorkManager.getInstance(this.context).enqueue(workRequest)

        return ManualEnqueueResult.Accepted
    }

    suspend fun setMode(mode: SyncMode) {
        metadataDao.setValue(SyncMetadataEntity("mode", mode.name))
    }
}
