package com.thanhtris.seminarie307.sync

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import androidx.work.workDataOf
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.integration.CorrelationUi
import com.thanhtris.seminarie307.integration.JsonStringArrayCodec
import com.thanhtris.seminarie307.integration.SyncMode
import com.thanhtris.seminarie307.integration.SyncSource
import java.util.UUID

class SyncWorker(
    appContext: Context,
    workerParams: WorkerParameters,
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val source = inputData.getString(KEY_SOURCE)?.let { runCatching { SyncSource.valueOf(it) }.getOrNull() }
            ?: return Result.failure(workDataOf(KEY_OUTCOME to "INVALID_TRIGGER"))
        val mode = inputData.getString(KEY_MODE)?.let { runCatching { SyncMode.valueOf(it) }.getOrNull() }
            ?: return Result.failure(workDataOf(KEY_OUTCOME to "INVALID_TRIGGER"))
        val runId = inputData.getString(KEY_RUN_ID)?.takeIf { isAppId(it) }
            ?: return Result.failure(workDataOf(KEY_OUTCOME to "INVALID_TRIGGER"))
        val deviceAlias = inputData.getString(KEY_DEVICE_ALIAS)?.takeIf { isAppId(it) }
            ?: return Result.failure(workDataOf(KEY_OUTCOME to "INVALID_TRIGGER"))
        val triggerAllowed = when (source) {
            SyncSource.MANUAL -> true
            SyncSource.PERIODIC -> mode == SyncMode.PERIODIC || mode == SyncMode.HYBRID
            SyncSource.PUSH -> mode == SyncMode.PUSH || mode == SyncMode.HYBRID
        }
        if (!triggerAllowed) return Result.failure(workDataOf(KEY_OUTCOME to "MODE_DISABLED"))
        val messageId = inputData.getString(KEY_MESSAGE_ID)
        val rawVersion = inputData.getLong(KEY_VERSION_HINT, -1L)
        val versionHint = rawVersion.takeIf { it >= 0 }
        val rawSignalIds = inputData.getString(KEY_SIGNAL_IDS).orEmpty()
        val signalIds = try {
            when {
                rawSignalIds.isEmpty() -> emptyList()
                rawSignalIds.startsWith("[") -> JsonStringArrayCodec.decode(rawSignalIds)
                else -> rawSignalIds.split(',')
            }
        } catch (_: IllegalArgumentException) {
            return Result.failure(workDataOf(KEY_OUTCOME to "INVALID_TRIGGER"))
        } catch (_: IllegalStateException) {
            return Result.failure(workDataOf(KEY_OUTCOME to "INVALID_TRIGGER"))
        }
        if (signalIds.any { !isAppId(it) }) return Result.failure(workDataOf(KEY_OUTCOME to "INVALID_TRIGGER"))
        val database = AppDatabase.getInstance(applicationContext)
        val suppliedRequestId = inputData.getString(KEY_REQUEST_ID)?.takeIf { it.isNotBlank() }
        val periodicRequestKey = if (source == SyncSource.PERIODIC) periodicRequestIdKey(id.toString()) else null
        val requestId = when {
            suppliedRequestId != null -> suppliedRequestId
            source == SyncSource.PERIODIC -> {
                val key = checkNotNull(periodicRequestKey)
                val existing = if (runAttemptCount > 0) database.metadataDao().getValue(key) else null
                (existing ?: "req-${UUID.randomUUID()}").also {
                    if (existing == null) database.metadataDao().setValue(
                        com.thanhtris.seminarie307.data.local.SyncMetadataEntity(key, it)
                    )
                }
            }
            else -> return Result.failure(workDataOf(KEY_OUTCOME to "INVALID_TRIGGER"))
        }
        if (!isAppId(requestId)) return Result.failure(workDataOf(KEY_OUTCOME to "INVALID_TRIGGER"))

        val input = SyncInput(
            source = source,
            mode = mode,
            runId = runId,
            deviceAlias = deviceAlias,
            versionHint = versionHint,
            workAttempt = runAttemptCount,
            signalIds = signalIds,
            correlation = CorrelationUi(
                requestId = requestId,
                workId = id.toString(),
                messageId = messageId,
            ),
        )

        val repository = SyncRepository(database)

        val result = repository.executeSync(input)
        if (periodicRequestKey != null && result.outcome != SyncOutcomeType.RETRY) {
            database.metadataDao().deleteValue(periodicRequestKey)
        }

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
        const val MAX_RETRY_COUNT = 3
        const val SYNC_WORK_TAG = "com.thanhtris.seminarie307.sync"
        const val ONE_TIME_SYNC_WORK_TAG = "com.thanhtris.seminarie307.sync.one_time"
        private val APP_ID_PATTERN = Regex("^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
        private fun isAppId(value: String) = APP_ID_PATTERN.matches(value)
        private fun periodicRequestIdKey(workId: String) = "periodic_request_id_$workId"
        const val KEY_SOURCE = "source"
        const val KEY_MODE = "mode"
        const val KEY_RUN_ID = "run_id"
        const val KEY_DEVICE_ALIAS = "device_alias"
        const val KEY_SIGNAL_IDS = "signal_ids"
        const val KEY_REQUEST_ID = "request_id"
        const val KEY_MESSAGE_ID = "message_id"
        const val KEY_VERSION_HINT = "version_hint"
        const val KEY_OUTCOME = "outcome"
        const val KEY_VERSION = "version"
    }
}
