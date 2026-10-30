package com.thanhtris.seminarie307.ui

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.assertIsNotEnabled
import androidx.compose.ui.test.assertIsSelected
import androidx.compose.ui.test.assertCountEquals
import androidx.compose.ui.test.junit4.StateRestorationTester
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTextInput
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.unit.Density
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.thanhtris.seminarie307.integration.BulletinItem
import com.thanhtris.seminarie307.integration.BulletinUiGateway
import com.thanhtris.seminarie307.integration.BulletinUiState
import com.thanhtris.seminarie307.integration.CorrelationUi
import com.thanhtris.seminarie307.integration.ManualEnqueueResult
import com.thanhtris.seminarie307.integration.ManualSyncContext
import com.thanhtris.seminarie307.integration.SyncMode
import com.thanhtris.seminarie307.integration.SyncSource
import com.thanhtris.seminarie307.integration.TimelineEvent
import com.thanhtris.seminarie307.ui.theme.SeminarTheme
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class BulletinScreenTest {
    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun emptyScaffoldShowsBothTabsAndKeepsManualDisabled() {
        var enqueueCount = 0
        composeRule.setContent {
            SeminarTheme {
                BulletinScreen(viewState = BulletinViewState(), onManualSync = { enqueueCount++ })
            }
        }

        composeRule.onNodeWithText("Bản tin").assertIsDisplayed()
        composeRule.onNodeWithText("Timeline").assertIsDisplayed()
        composeRule.onNodeWithText("Chưa có bản tin trong cache").assertIsDisplayed()
        composeRule.onNodeWithText("Đồng bộ chưa khả dụng: chưa có gateway hoặc run đang hoạt động.").assertIsDisplayed()
        composeRule.onNodeWithText("Đồng bộ thủ công").assertIsNotEnabled()
        assertEquals(0, enqueueCount)
    }

    @Test
    fun manualUsesActiveRunContextAndAcceptedMessageDoesNotClaimApplied() {
        val expectedContext = ManualSyncContext(runId = "run-live-7", mode = SyncMode.HYBRID)
        val gateway = RecordingGateway(sampleState(activeRunId = expectedContext.runId))
        val viewModel = BulletinViewModel(gateway)
        composeRule.setContent {
            SeminarTheme {
                val viewState by viewModel.state.collectAsState()
                BulletinScreen(viewState = viewState, onManualSync = viewModel::enqueueManual)
            }
        }

        composeRule.onNodeWithText("Đồng bộ thủ công").performClick()
        composeRule.waitUntil(timeoutMillis = 5_000) { gateway.enqueueCount == 1 }
        assertEquals(expectedContext, gateway.receivedContext)
        assertEquals(1, gateway.enqueueCount)
        composeRule.onNodeWithText("Đã xếp lịch; chưa xác nhận đã đồng bộ.").assertIsDisplayed()
        composeRule.onNodeWithText("Version cache").assertIsDisplayed()
        composeRule.onNodeWithText("v41").assertIsDisplayed()
    }

    @Test
    fun runFilterRestoresAfterRecreationAndDoesNotChangeManualRun() {
        val restorationTester = StateRestorationTester(composeRule)
        val context = ManualSyncContext(runId = "run-live-7", mode = SyncMode.HYBRID)
        var received: ManualSyncContext? = null
        restorationTester.setContent {
            SeminarTheme {
                BulletinScreen(
                    viewState = BulletinViewState(data = sampleState(activeRunId = context.runId)),
                    onManualSync = { received = it },
                )
            }
        }

        composeRule.onNodeWithText("Timeline").performClick()
        composeRule.onNodeWithText("MANUAL").assertIsDisplayed()
        composeRule.onNodeWithText("snapshot_applied").assertIsDisplayed()
        composeRule.onAllNodesWithText("2026-10-31T05:00:00Z").assertCountEquals(2)
        composeRule.onNodeWithText("v41 · applied").assertIsDisplayed()
        composeRule.onNodeWithText("snapshot_applied").performClick()
        composeRule.onNodeWithText("request_id: request-test").assertIsDisplayed()
        composeRule.onNodeWithText("Lọc theo run_id").performTextInput(" run-a ")
        composeRule.onNodeWithText("run_id: run-a").assertIsDisplayed()
        composeRule.onNodeWithText("run_id: run-ab").assertDoesNotExist()

        restorationTester.emulateSavedInstanceStateRestore()
        composeRule.onNodeWithText("Timeline").assertIsSelected()
        composeRule.onNodeWithText(" run-a ").assertIsDisplayed()

        composeRule.onNodeWithText("Bản tin").performClick()
        composeRule.onNodeWithText("Đồng bộ thủ công").performClick()
        assertEquals(context, received)
    }

    @Test
    fun darkThemeAndLargeFontKeepSnapshotScrollable() {
        val state = sampleState(activeRunId = "run-live-7").copy(
            snapshot = (1..12).map { index ->
                BulletinItem("item-$index", "Tin mẫu $index", "Nội dung bản tin $index.", 41)
            },
        )
        composeRule.setContent {
            CompositionLocalProvider(LocalDensity provides Density(density = 1f, fontScale = 1.6f)) {
                SeminarTheme(darkTheme = true) {
                    BulletinScreen(viewState = BulletinViewState(data = state), onManualSync = {})
                }
            }
        }

        composeRule.onNodeWithText("Bản tin").assertIsDisplayed()
        composeRule.onNodeWithText("Tin mẫu 12").performScrollTo().assertIsDisplayed()
        composeRule.onNodeWithText("Đồng bộ thủ công").performScrollTo().assertIsDisplayed()
    }

    private fun sampleState(activeRunId: String) = BulletinUiState(
        cachedVersion = 41,
        mode = SyncMode.HYBRID,
        activeRunId = activeRunId,
        lastSyncAtUtc = "2026-10-31T05:00:00Z",
        snapshot = listOf(BulletinItem("item-1", "Tin mẫu", "Fixture cho UI test.", 41)),
        timeline = listOf(
            TimelineEvent(
                eventId = "event-a",
                source = SyncSource.MANUAL,
                eventType = "snapshot_applied",
                occurredAtEpochMillis = 20,
                occurredAtUtc = "2026-10-31T05:00:00Z",
                runId = "run-a",
                version = 41,
                outcome = "applied",
                correlation = CorrelationUi(requestId = "request-test"),
            ),
            TimelineEvent(
                eventId = "event-ab",
                source = SyncSource.PUSH,
                eventType = "push_received",
                occurredAtEpochMillis = 10,
                occurredAtUtc = "2026-10-31T04:59:00Z",
                runId = "run-ab",
            ),
        ),
        manualAvailable = true,
    )

    private class RecordingGateway(initialState: BulletinUiState) : BulletinUiGateway {
        override val state: Flow<BulletinUiState> = flowOf(initialState)
        var enqueueCount: Int = 0
            private set
        var receivedContext: ManualSyncContext? = null
            private set

        override suspend fun enqueueManual(context: ManualSyncContext): ManualEnqueueResult {
            enqueueCount += 1
            receivedContext = context
            return ManualEnqueueResult.Accepted
        }
    }
}
