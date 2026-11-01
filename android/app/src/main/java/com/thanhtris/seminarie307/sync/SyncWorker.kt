package com.thanhtris.seminarie307.sync

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import androidx.work.workDataOf
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.integration.CorrelationUi
import com.thanhtris.seminarie307.integration.SyncMode
import com.thanhtris.seminarie307.integration.SyncSource

class SyncWorker(
    appContext: Context,
    workerParams: WorkerParameters,
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val sourceStr = inputData.getString(KEY_SOURCE) ?: SyncSource.MANUAL.name
        val modeStr = inputData.getString(KEY_MODE) ?: SyncMode.HYBRID.name
        val runId = inputData.getString(KEY_RUN_ID) ?: "default-run"
        val requestId = inputData.getString(KEY_REQUEST_ID)
        val messageId = inputData.getString(KEY_MESSAGE_ID)
        val rawVersion = inputData.getLong(KEY_VERSION_HINT, -1L)
        val versionHint = rawVersion.takeIf { it >= 0 }

        val source = runCatching { SyncSource.valueOf(sourceStr) }.getOrDefault(SyncSource.MANUAL)
        val mode = runCatching { SyncMode.valueOf(modeStr) }.getOrDefault(SyncMode.HYBRID)

        val input = SyncInput(
            source = source,
            mode = mode,
            runId = runId,
            versionHint = versionHint,
            correlation = CorrelationUi(
                requestId = requestId,
                workId = id.toString(),
                messageId = messageId,
            ),
        )

        val database = AppDatabase.getInstance(applicationContext)
        val repository = SyncRepository(database)

        val result = repository.executeSync(input)

        return when (result.outcome) {
            SyncOutcomeType.APPLIED,
            SyncOutcomeType.UNCHANGED,
            SyncOutcomeType.STALE -> {
                Result.success(
                    workDataOf(
                        KEY_OUTCOME to result.outcome.name,
                        KEY_VERSION to (result.version ?: -1L),
                    )
                )
            }
            SyncOutcomeType.RETRY -> Result.retry()
            SyncOutcomeType.FAILURE -> Result.failure(
                workDataOf(KEY_OUTCOME to result.outcome.name)
            )
        }
    }

    companion object {
        const val KEY_SOURCE = "source"
        const val KEY_MODE = "mode"
        const val KEY_RUN_ID = "run_id"
        const val KEY_REQUEST_ID = "request_id"
        const val KEY_MESSAGE_ID = "message_id"
        const val KEY_VERSION_HINT = "version_hint"
        const val KEY_OUTCOME = "outcome"
        const val KEY_VERSION = "version"
    }
}
