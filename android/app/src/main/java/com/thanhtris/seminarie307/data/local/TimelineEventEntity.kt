package com.thanhtris.seminarie307.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.thanhtris.seminarie307.integration.CorrelationUi
import com.thanhtris.seminarie307.integration.SyncSource
import com.thanhtris.seminarie307.integration.TimelineEvent

@Entity(tableName = "timeline_events")
data class TimelineEventEntity(
    @PrimaryKey val eventId: String,
    val source: String?,
    val eventType: String,
    val occurredAtEpochMillis: Long,
    val occurredAtUtc: String,
    val runId: String?,
    val version: Long? = null,
    val outcome: String? = null,
    val reason: String? = null,
    val requestId: String? = null,
    val workId: String? = null,
    val messageId: String? = null,
) {
    fun toTimelineEvent(): TimelineEvent = TimelineEvent(
        eventId = eventId,
        source = source?.let { runCatching { SyncSource.valueOf(it) }.getOrNull() },
        eventType = eventType,
        occurredAtEpochMillis = occurredAtEpochMillis,
        occurredAtUtc = occurredAtUtc,
        runId = runId,
        version = version,
        outcome = outcome,
        reason = reason,
        correlation = CorrelationUi(
            requestId = requestId,
            workId = workId,
            messageId = messageId,
        ),
    )

    companion object {
        fun fromTimelineEvent(event: TimelineEvent): TimelineEventEntity = TimelineEventEntity(
            eventId = event.eventId,
            source = event.source?.name,
            eventType = event.eventType,
            occurredAtEpochMillis = event.occurredAtEpochMillis,
            occurredAtUtc = event.occurredAtUtc,
            runId = event.runId,
            version = event.version,
            outcome = event.outcome,
            reason = event.reason,
            requestId = event.correlation?.requestId,
            workId = event.correlation?.workId,
            messageId = event.correlation?.messageId,
        )
    }
}
