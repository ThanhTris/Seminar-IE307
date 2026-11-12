package com.thanhtris.seminarie307.integration

import android.content.Context
import androidx.room.withTransaction
import androidx.work.WorkManager
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.data.local.SyncMetadataEntity
import com.thanhtris.seminarie307.sync.PeriodicSyncScheduler
import com.thanhtris.seminarie307.sync.SyncWorker
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/** Persists the active run/mode and keeps the unique periodic schedule aligned with it. */
class SyncModeController(
    private val context: Context,
    private val database: AppDatabase = AppDatabase.getInstance(context),
    private val periodicScheduler: PeriodicSyncScheduler = PeriodicSyncScheduler(context, database),
) {
    suspend fun configure(mode: SyncMode, runId: String, deviceAlias: String) = withContext(Dispatchers.IO) {
        require(APP_ID.matches(runId)) { "runId must be a valid experiment run id" }
        require(APP_ID.matches(deviceAlias)) { "deviceAlias must be a valid experiment device alias" }
        check(!hasActiveSyncWork()) {
            "Wait for queued or active sync work to finish before changing mode"
        }

        // WorkManager operations complete before the selected mode is published to the UI.
        if (mode == SyncMode.PERIODIC || mode == SyncMode.HYBRID) {
            checkNotNull(periodicScheduler.schedulePeriodicSync(mode, runId, deviceAlias = deviceAlias)) {
                "WorkManager did not expose an active periodic request after scheduling"
            }
        } else {
            periodicScheduler.cancelPeriodicSync(runId)
            check(!hasActiveSyncWork()) {
                "The periodic worker is still stopping; retry the mode change after it becomes terminal"
            }
        }

        database.withTransaction {
            database.metadataDao().setValue(SyncMetadataEntity(KEY_MODE, mode.name))
            database.metadataDao().setValue(SyncMetadataEntity(KEY_ACTIVE_RUN_ID, runId))
            database.metadataDao().setValue(SyncMetadataEntity(KEY_DEVICE_ALIAS, deviceAlias))
        }
    }

    private fun hasActiveSyncWork(): Boolean =
        WorkManager.getInstance(context.applicationContext).let { workManager ->
            val allSyncWork = workManager.getWorkInfosByTag(SyncWorker.SYNC_WORK_TAG).get()
            val activeOneTime = workManager.getWorkInfosByTag(SyncWorker.ONE_TIME_SYNC_WORK_TAG)
                .get()
                .any { !it.state.isFinished }
            activeOneTime || allSyncWork.any { it.state == androidx.work.WorkInfo.State.RUNNING }
        }

    companion object {
        const val KEY_MODE = "mode"
        const val KEY_ACTIVE_RUN_ID = "activeRunId"
        const val KEY_DEVICE_ALIAS = "deviceAlias"
        private val APP_ID = Regex("^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
    }
}
