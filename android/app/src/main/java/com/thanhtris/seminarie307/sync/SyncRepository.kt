package com.thanhtris.seminarie307.sync

import android.os.SystemClock
import androidx.room.withTransaction
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.data.local.BulletinEntity
import com.thanhtris.seminarie307.data.local.SyncMetadataEntity
import com.thanhtris.seminarie307.data.local.TimelineEventEntity
import com.thanhtris.seminarie307.data.remote.RemoteSnapshotResult
import com.thanhtris.seminarie307.data.remote.SnapshotRemoteDataSource
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.time.Instant
import java.util.UUID

class SyncRepository(
    private val database: AppDatabase,
    private val remoteDataSource: SnapshotRemoteDataSource = SnapshotRemoteDataSource(),
) {
    private val bulletinDao = database.bulletinDao()
    private val timelineDao = database.timelineDao()
    private val metadataDao = database.metadataDao()

    suspend fun executeSync(input: SyncInput): SyncResult = withContext(Dispatchers.IO) {
        val initialVersion = readLatestCachedVersion()

        // 1. Record work_started
        recordEvent(
            input = input,
            eventType = "work_started",
            version = null,
            outcome = "started",
            reason = null,
            cachedVersion = initialVersion,
        )

        // 2. Fetch remote snapshot
        val networkCallId = UUID.randomUUID().toString()
        recordEvent(
            input = input,
            eventType = "snapshot_fetch_started",
            version = null,
            outcome = "started",
            reason = null,
            cachedVersion = initialVersion,
            networkCallId = networkCallId,
        )
        val remoteResult = remoteDataSource.fetchSnapshot(
            currentVersion = initialVersion,
            requestId = input.correlation.requestId,
        )
        when (remoteResult) {
            is RemoteSnapshotResult.Success -> recordEvent(
                input, "snapshot_fetch_completed", remoteResult.version, "success", null,
                cachedVersion = initialVersion, networkCallId = networkCallId, httpStatus = 200,
            )
            is RemoteSnapshotResult.NotModified -> recordEvent(
                input, "snapshot_fetch_completed", null, "not_modified", null,
                cachedVersion = initialVersion, networkCallId = networkCallId, httpStatus = remoteResult.statusCode,
            )
            is RemoteSnapshotResult.Failure -> recordEvent(
                input, "snapshot_fetch_completed", null, "failure", remoteResult.message,
                cachedVersion = initialVersion, networkCallId = networkCallId, httpStatus = remoteResult.statusCode,
            )
        }

        val nowUtc = Instant.now().toString()

        // 3. Process outcome with atomic version guard inside Room transaction
        when (remoteResult) {
            is RemoteSnapshotResult.Success -> {
                database.withTransaction {
                    val lockedVersion = readLatestCachedVersion()
                    if (lockedVersion == null || remoteResult.version > lockedVersion) {
                        val entities = remoteResult.items.map { BulletinEntity.fromBulletinItem(it) }
                        bulletinDao.replaceSnapshot(entities)
                        metadataDao.setValue(SyncMetadataEntity("cachedVersion", remoteResult.version.toString()))
                        metadataDao.setValue(SyncMetadataEntity("lastSyncAtUtc", nowUtc))

                        recordEvent(
                            input = input,
                            eventType = "snapshot_applied",
                            version = remoteResult.version,
                            outcome = "applied",
                            reason = null,
                            cachedVersion = remoteResult.version,
                        )

                        SyncResult(
                            outcome = SyncOutcomeType.APPLIED,
                            reason = "SNAPSHOT_APPLIED",
                            version = remoteResult.version,
                        )
                    } else if (remoteResult.version == lockedVersion) {
                        metadataDao.setValue(SyncMetadataEntity("cachedVersion", checkNotNull(lockedVersion).toString()))
                        metadataDao.setValue(SyncMetadataEntity("lastSyncAtUtc", nowUtc))
                        recordEvent(
                            input = input,
                            eventType = "snapshot_unchanged",
                            version = lockedVersion,
                            outcome = "unchanged",
                            reason = null,
                            cachedVersion = lockedVersion,
                        )
                        SyncResult(
                            outcome = SyncOutcomeType.UNCHANGED,
                            reason = "VERSION_UNCHANGED",
                            version = lockedVersion,
                        )
                    } else {
                        metadataDao.setValue(SyncMetadataEntity("cachedVersion", checkNotNull(lockedVersion).toString()))
                        metadataDao.setValue(SyncMetadataEntity("lastSyncAtUtc", nowUtc))
                        recordEvent(
                            input = input,
                            eventType = "snapshot_stale",
                            version = remoteResult.version,
                            outcome = "stale",
                            reason = "VERSION_STALE",
                            cachedVersion = lockedVersion,
                        )
                        SyncResult(
                            outcome = SyncOutcomeType.STALE,
                            reason = "VERSION_STALE",
                            version = lockedVersion,
                        )
                    }
                }
            }

            is RemoteSnapshotResult.NotModified -> {
                if (initialVersion == null) {
                    recordEvent(input, "sync_failed", null, "failure", "INVALID_RESPONSE", cachedVersion = initialVersion)
                    return@withContext SyncResult(SyncOutcomeType.FAILURE, "INVALID_RESPONSE")
                }
                metadataDao.setValue(SyncMetadataEntity("cachedVersion", initialVersion.toString()))
                metadataDao.setValue(SyncMetadataEntity("lastSyncAtUtc", nowUtc))
                recordEvent(
                    input = input,
                    eventType = "snapshot_unchanged",
                    version = null,
                    outcome = "unchanged",
                    reason = null,
                    cachedVersion = initialVersion,
                )
                SyncResult(
                    outcome = SyncOutcomeType.UNCHANGED,
                    reason = "Bản tin không đổi",
                    version = initialVersion,
                )
            }

            is RemoteSnapshotResult.Failure -> {
                val canRetry = remoteResult.isTransient && input.workAttempt < SyncWorker.MAX_RETRY_COUNT
                val outcomeType = if (canRetry) {
                    SyncOutcomeType.RETRY
                } else {
                    SyncOutcomeType.FAILURE
                }

                recordEvent(
                    input = input,
                    eventType = if (canRetry) "sync_retrying" else "sync_failed",
                    version = null,
                    outcome = if (canRetry) "retry" else "failure",
                    reason = if (remoteResult.isTransient && !canRetry) "RETRY_EXHAUSTED" else remoteResult.message,
                    cachedVersion = initialVersion,
                )

                SyncResult(
                    outcome = outcomeType,
                    reason = if (remoteResult.isTransient && !canRetry) "RETRY_EXHAUSTED" else remoteResult.message,
                    version = initialVersion,
                )
            }
        }
    }

    private suspend fun recordEvent(
        input: SyncInput,
        eventType: String,
        version: Long?,
        outcome: String?,
        reason: String?,
        cachedVersion: Long? = null,
        networkCallId: String? = null,
        httpStatus: Int? = null,
    ) {
        val now = Instant.now()
        val elapsedRealtime = SystemClock.elapsedRealtime()
        val eventEntity = TimelineEventEntity(
            eventId = UUID.randomUUID().toString(),
            source = input.source.name,
            eventType = eventType,
            occurredAtEpochMillis = now.toEpochMilli(),
            occurredAtUtc = now.toString(),
            runId = input.runId,
            version = version,
            outcome = outcome,
            reason = reason,
            requestId = input.correlation.requestId,
            workId = input.correlation.workId,
            messageId = input.correlation.messageId,
            elapsedRealtimeMillis = elapsedRealtime,
            mode = input.mode.name,
            deviceAlias = input.deviceAlias,
            cachedVersion = cachedVersion,
            versionHint = input.versionHint,
            workAttempt = input.workAttempt,
            networkCallId = networkCallId,
            signalIdsJson = org.json.JSONArray(input.signalIds).toString(),
            httpStatus = httpStatus,
        )
        timelineDao.insert(eventEntity)
    }

    private suspend fun readLatestCachedVersion(): Long? {
        val metadataVersion = metadataDao.getValue("cachedVersion")?.toLongOrNull()
        val itemVersion = bulletinDao.getLatestVersion()
        return listOfNotNull(metadataVersion, itemVersion)
            .filter { it in 0..MAX_SAFE_JSON_INTEGER }
            .maxOrNull()
    }

    companion object {
        private const val MAX_SAFE_JSON_INTEGER = 9_007_199_254_740_991L
    }
}
