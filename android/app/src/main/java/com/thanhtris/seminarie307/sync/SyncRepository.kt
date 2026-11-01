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
        val initialVersion = bulletinDao.getLatestVersion()

        // 1. Record work_started
        recordEvent(
            input = input,
            eventType = "work_started",
            version = initialVersion,
            outcome = "started",
            reason = "Bắt đầu fetch snapshot từ server",
        )

        // 2. Fetch remote snapshot
        val remoteResult = remoteDataSource.fetchSnapshot(
            currentVersion = initialVersion,
            requestId = input.correlation.requestId,
        )

        val nowUtc = Instant.now().toString()

        // 3. Process outcome with atomic version guard inside Room transaction
        when (remoteResult) {
            is RemoteSnapshotResult.Success -> {
                database.withTransaction {
                    val lockedVersion = bulletinDao.getLatestVersion()
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
                            reason = "Đã lưu snapshot v${remoteResult.version} (${entities.size} bản tin)",
                        )

                        SyncResult(
                            outcome = SyncOutcomeType.APPLIED,
                            reason = "Đã cập nhật snapshot v${remoteResult.version}",
                            version = remoteResult.version,
                        )
                    } else {
                        recordEvent(
                            input = input,
                            eventType = "snapshot_stale",
                            version = lockedVersion,
                            outcome = "stale",
                            reason = "Bỏ qua: version server (${remoteResult.version}) không mới hơn cache ($lockedVersion)",
                        )
                        SyncResult(
                            outcome = SyncOutcomeType.STALE,
                            reason = "Version không mới hơn cache",
                            version = lockedVersion,
                        )
                    }
                }
            }

            RemoteSnapshotResult.NotModified -> {
                metadataDao.setValue(SyncMetadataEntity("lastSyncAtUtc", nowUtc))
                recordEvent(
                    input = input,
                    eventType = "snapshot_unchanged",
                    version = initialVersion,
                    outcome = "unchanged",
                    reason = "Bản tin không đổi (HTTP 304 Not Modified)",
                )
                SyncResult(
                    outcome = SyncOutcomeType.UNCHANGED,
                    reason = "Bản tin không đổi",
                    version = initialVersion,
                )
            }

            is RemoteSnapshotResult.Failure -> {
                val outcomeType = if (remoteResult.isTransient) {
                    SyncOutcomeType.RETRY
                } else {
                    SyncOutcomeType.FAILURE
                }

                recordEvent(
                    input = input,
                    eventType = if (remoteResult.isTransient) "sync_retrying" else "sync_failed",
                    version = initialVersion,
                    outcome = if (remoteResult.isTransient) "retry" else "failure",
                    reason = remoteResult.message,
                )

                SyncResult(
                    outcome = outcomeType,
                    reason = remoteResult.message,
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
        )
        timelineDao.insert(eventEntity)
    }
}
