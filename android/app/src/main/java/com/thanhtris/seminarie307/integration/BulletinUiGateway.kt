package com.thanhtris.seminarie307.integration

import kotlinx.coroutines.flow.Flow

enum class SyncMode {
    PERIODIC,
    PUSH,
    HYBRID,
}

enum class SyncSource {
    MANUAL,
    PERIODIC,
    PUSH,
}

data class BulletinItem(
    val id: String,
    val title: String,
    val body: String,
    val version: Long,
)

data class CorrelationUi(
    val requestId: String? = null,
    val workId: String? = null,
    val messageId: String? = null,
)

data class TimelineEvent(
    val eventId: String,
    val source: SyncSource?,
    val eventType: String,
    val occurredAtEpochMillis: Long,
    val occurredAtUtc: String,
    val runId: String?,
    val version: Long? = null,
    val outcome: String? = null,
    val reason: String? = null,
    val correlation: CorrelationUi? = null,
    val elapsedRealtimeMillis: Long? = null,
)

data class BulletinUiState(
    val cachedVersion: Long? = null,
    val mode: SyncMode? = null,
    val activeRunId: String? = null,
    val lastSyncAtUtc: String? = null,
    val snapshot: List<BulletinItem> = emptyList(),
    val timeline: List<TimelineEvent> = emptyList(),
    val manualAvailable: Boolean = false,
) {
    fun manualContextOrNull(): ManualSyncContext? {
        val runId = activeRunId?.takeIf(String::isNotBlank) ?: return null
        val mode = mode ?: return null
        return ManualSyncContext(runId = runId, mode = mode)
    }

    val canEnqueueManual: Boolean
        get() = manualAvailable && manualContextOrNull() != null
}

data class ManualSyncContext(
    val runId: String,
    val mode: SyncMode,
)

sealed interface ManualEnqueueResult {
    data object Accepted : ManualEnqueueResult
    data class Rejected(val reason: String) : ManualEnqueueResult
}

/** UI-facing port. The implementation observes cache/local events and only enqueues manual sync. */
interface BulletinUiGateway {
    val state: Flow<BulletinUiState>

    suspend fun enqueueManual(context: ManualSyncContext): ManualEnqueueResult
}
