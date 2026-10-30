package com.thanhtris.seminarie307.ui

import androidx.compose.runtime.Composable
import androidx.compose.ui.tooling.preview.Preview
import com.thanhtris.seminarie307.integration.BulletinItem
import com.thanhtris.seminarie307.integration.BulletinUiState
import com.thanhtris.seminarie307.integration.CorrelationUi
import com.thanhtris.seminarie307.integration.SyncMode
import com.thanhtris.seminarie307.integration.SyncSource
import com.thanhtris.seminarie307.integration.TimelineEvent
import com.thanhtris.seminarie307.ui.theme.SeminarTheme

private val PreviewState = BulletinUiState(
    cachedVersion = 42,
    mode = SyncMode.HYBRID,
    activeRunId = "preview-run-01",
    lastSyncAtUtc = "2026-10-31T05:00:00Z",
    snapshot = listOf(
        BulletinItem(
            id = "preview-1",
            title = "Bản tin minh họa",
            body = "Fixture này chỉ dùng trong Compose Preview, không xuất hiện khi chạy app.",
            version = 42,
        ),
    ),
    timeline = listOf(
        TimelineEvent(
            eventId = "preview-event-1",
            source = SyncSource.MANUAL,
            eventType = "snapshot_applied",
            occurredAtEpochMillis = 1_793_426_400_000,
            occurredAtUtc = "2026-10-31T05:00:00Z",
            runId = "preview-run-01",
            version = 42,
            outcome = "applied",
            correlation = CorrelationUi(requestId = "preview-request-01"),
        ),
    ),
    manualAvailable = true,
)

@Preview(showBackground = true, name = "Bản tin (fixture)")
@Composable
private fun BulletinPreview() {
    SeminarTheme {
        BulletinScreen(
            viewState = BulletinViewState(data = PreviewState),
            onManualSync = {},
        )
    }
}

@Preview(showBackground = true, name = "Trạng thái rỗng")
@Composable
private fun EmptyBulletinPreview() {
    SeminarTheme {
        BulletinScreen(
            viewState = BulletinViewState(),
            onManualSync = {},
        )
    }
}
