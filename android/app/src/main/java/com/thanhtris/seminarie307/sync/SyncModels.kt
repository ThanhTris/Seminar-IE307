package com.thanhtris.seminarie307.sync

import com.thanhtris.seminarie307.integration.CorrelationUi
import com.thanhtris.seminarie307.integration.SyncMode
import com.thanhtris.seminarie307.integration.SyncSource

data class SyncInput(
    val source: SyncSource,
    val mode: SyncMode,
    val runId: String,
    val versionHint: Long? = null,
    val correlation: CorrelationUi = CorrelationUi(),
)

enum class SyncOutcomeType {
    APPLIED,
    UNCHANGED,
    STALE,
    RETRY,
    FAILURE,
}

data class SyncResult(
    val outcome: SyncOutcomeType,
    val reason: String,
    val version: Long? = null,
)
