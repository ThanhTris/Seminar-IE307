package com.thanhtris.seminarie307.integration

import android.content.Context
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.sync.SyncInput
import com.thanhtris.seminarie307.sync.SyncWorkEnqueuer
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import java.util.UUID

class RealBulletinUiGateway(
    private val context: Context,
    private val database: AppDatabase = AppDatabase.getInstance(context),
    private val enqueuer: SyncWorkEnqueuer = SyncWorkEnqueuer(context, database),
) : BulletinUiGateway {

    private val bulletinDao = database.bulletinDao()
    private val timelineDao = database.timelineDao()
    private val metadataDao = database.metadataDao()

    private val baseState: Flow<BulletinUiState> = combine(
        bulletinDao.observeAll(),
        timelineDao.observeAll(),
        metadataDao.observeValue("cachedVersion"),
        metadataDao.observeValue("lastSyncAtUtc"),
        metadataDao.observeValue(SyncModeController.KEY_MODE),
    ) { items, events, cachedVersionStr, lastSyncAtUtc, modeStr ->
        val version = cachedVersionStr?.toLongOrNull() ?: items.firstOrNull()?.version
        val mode = modeStr?.let { runCatching { SyncMode.valueOf(it) }.getOrNull() }

        BulletinUiState(
            cachedVersion = version,
            mode = mode,
            lastSyncAtUtc = lastSyncAtUtc,
            snapshot = items.map { it.toBulletinItem() },
            timeline = events.map { it.toTimelineEvent() },
            manualAvailable = true,
        )
    }

    override val state: Flow<BulletinUiState> = baseState.combine(
        metadataDao.observeValue(SyncModeController.KEY_ACTIVE_RUN_ID),
    ) { current, activeRunId ->
        current.copy(activeRunId = activeRunId?.takeIf(String::isNotBlank))
    }

    override suspend fun enqueueManual(context: ManualSyncContext): ManualEnqueueResult {
        val requestId = "req-${UUID.randomUUID()}"
        return try {
            val workId = enqueuer.enqueue(
                SyncInput(
                    source = SyncSource.MANUAL,
                    mode = context.mode,
                    runId = context.runId,
                    correlation = CorrelationUi(requestId = requestId),
                )
            )
            if (workId != null) {
                ManualEnqueueResult.Accepted
            } else {
                ManualEnqueueResult.Rejected("Không thể xếp lịch WorkManager")
            }
        } catch (e: Exception) {
            ManualEnqueueResult.Rejected(e.message ?: "Lỗi xếp lịch manual sync")
        }
    }

    override suspend fun configureMode(mode: SyncMode, runId: String) {
        SyncModeController(context, database).configure(mode, runId)
    }
}
