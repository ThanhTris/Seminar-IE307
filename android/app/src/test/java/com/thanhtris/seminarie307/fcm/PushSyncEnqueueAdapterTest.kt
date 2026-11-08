package com.thanhtris.seminarie307.fcm

import com.thanhtris.seminarie307.data.local.SyncMetadataDao
import com.thanhtris.seminarie307.data.local.SyncMetadataEntity
import com.thanhtris.seminarie307.data.local.TimelineDao
import com.thanhtris.seminarie307.data.local.TimelineEventEntity
import com.thanhtris.seminarie307.integration.SyncMode
import com.thanhtris.seminarie307.integration.SyncSource
import com.thanhtris.seminarie307.sync.SyncInput
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import java.util.UUID

class PushSyncEnqueueAdapterTest {

    private lateinit var fakeTimelineDao: FakeTimelineDao
    private lateinit var fakeMetadataDao: FakeSyncMetadataDao
    private var enqueuedInputs = mutableListOf<SyncInput>()
    private var enqueueWorkMock: suspend (SyncInput) -> UUID? = { input ->
        enqueuedInputs.add(input)
        UUID.randomUUID()
    }

    private lateinit var adapter: PushSyncEnqueueAdapter

    @Before
    fun setUp() {
        fakeTimelineDao = FakeTimelineDao()
        fakeMetadataDao = FakeSyncMetadataDao()
        enqueuedInputs.clear()
        adapter = PushSyncEnqueueAdapter(
            timelineDao = fakeTimelineDao,
            metadataDao = fakeMetadataDao,
            enqueueWork = enqueueWorkMock,
        )
    }

    @Test
    fun rejectsPushMessageWithNotificationPayload() = runBlocking {
        val result = adapter.processPushPayload(
            data = mapOf("run_id" to "run-001"),
            messageId = "msg-001",
            hasNotificationPayload = true,
        )

        assertTrue(result is PushProcessingResult.Ignored)
        assertEquals("NOTIFICATION_PAYLOAD_NOT_ALLOWED", (result as PushProcessingResult.Ignored).reason)
        assertEquals(0, fakeTimelineDao.events.size)
        assertEquals(0, enqueuedInputs.size)
    }

    @Test
    fun rejectsEmptyDataPayload() = runBlocking {
        val result = adapter.processPushPayload(
            data = emptyMap(),
            messageId = "msg-001",
            hasNotificationPayload = false,
        )

        assertTrue(result is PushProcessingResult.Ignored)
        assertEquals("EMPTY_DATA_PAYLOAD", (result as PushProcessingResult.Ignored).reason)
        assertEquals(0, fakeTimelineDao.events.size)
        assertEquals(0, enqueuedInputs.size)
    }

    @Test
    fun rejectsMissingOrInvalidRunIdWithoutBogusEvents() = runBlocking {
        val missingResult = adapter.processPushPayload(
            data = mapOf("version_hint" to "1"),
            messageId = "msg-001",
        )
        assertTrue(missingResult is PushProcessingResult.Rejected)
        assertEquals("INVALID_PAYLOAD", (missingResult as PushProcessingResult.Rejected).reason)
        assertEquals(0, fakeTimelineDao.events.size)
        assertEquals(0, enqueuedInputs.size)

        val invalidResult = adapter.processPushPayload(
            data = mapOf("run_id" to "bad run id with spaces"),
            messageId = "msg-002",
        )
        assertTrue(invalidResult is PushProcessingResult.Rejected)
        assertEquals("INVALID_PAYLOAD", (invalidResult as PushProcessingResult.Rejected).reason)
        assertEquals(0, fakeTimelineDao.events.size)
        assertEquals(0, enqueuedInputs.size)
    }

    @Test
    fun recordsPushReceivedAndRejectsTriggerWhenModeDisabled() = runBlocking {
        // App is configured to PERIODIC mode only
        fakeMetadataDao.setValue(SyncMetadataEntity("mode", SyncMode.PERIODIC.name))

        val result = adapter.processPushPayload(
            data = mapOf(
                "run_id" to "run-push-001",
                "request_id" to "req-001",
                "version_hint" to "2",
            ),
            messageId = "msg-001",
        )

        assertTrue(result is PushProcessingResult.Rejected)
        assertEquals("MODE_DISABLED", (result as PushProcessingResult.Rejected).reason)
        assertEquals("run-push-001", result.runId)

        // Verifies observed push receipt is recorded, followed by trigger_rejected
        assertEquals(2, fakeTimelineDao.events.size)
        val pushReceived = fakeTimelineDao.events[0]
        assertEquals("push_received", pushReceived.eventType)
        assertEquals("received", pushReceived.outcome)
        assertEquals("run-push-001", pushReceived.runId)
        assertEquals(2L, pushReceived.version)
        assertEquals("req-001", pushReceived.requestId)
        assertEquals("msg-001", pushReceived.messageId)

        val triggerRejected = fakeTimelineDao.events[1]
        assertEquals("trigger_rejected", triggerRejected.eventType)
        assertEquals("rejected", triggerRejected.outcome)
        assertEquals("MODE_DISABLED", triggerRejected.reason)
        assertEquals("run-push-001", triggerRejected.runId)

        // Work is not enqueued
        assertEquals(0, enqueuedInputs.size)
    }

    @Test
    fun acceptsValidPayloadAndEnqueuesWorker() = runBlocking {
        fakeMetadataDao.setValue(SyncMetadataEntity("mode", SyncMode.HYBRID.name))

        val result = adapter.processPushPayload(
            data = mapOf(
                "run_id" to "run-push-100",
                "request_id" to "req-custom-100",
                "version_hint" to "5",
                "mode" to "PUSH",
            ),
            messageId = "projects/my-project/messages/12345",
        )

        assertTrue(result is PushProcessingResult.Enqueued)
        val enqueued = result as PushProcessingResult.Enqueued
        assertEquals("run-push-100", enqueued.runId)
        assertEquals("req-custom-100", enqueued.requestId)
        assertNotNull(enqueued.workId)

        // Check timeline event
        assertEquals(1, fakeTimelineDao.events.size)
        val event = fakeTimelineDao.events[0]
        assertEquals("push_received", event.eventType)
        assertEquals("received", event.outcome)
        assertEquals(SyncSource.PUSH.name, event.source)
        assertEquals("run-push-100", event.runId)
        assertEquals(5L, event.version)
        assertEquals("req-custom-100", event.requestId)
        assertEquals("projects/my-project/messages/12345", event.messageId)

        // Check enqueued input
        assertEquals(1, enqueuedInputs.size)
        val input = enqueuedInputs[0]
        assertEquals(SyncSource.PUSH, input.source)
        assertEquals(SyncMode.PUSH, input.mode)
        assertEquals("run-push-100", input.runId)
        assertEquals(5L, input.versionHint)
        assertEquals("req-custom-100", input.correlation.requestId)
        assertEquals("projects/my-project/messages/12345", input.correlation.messageId)
    }

    @Test
    fun autoGeneratesRequestIdWhenMissingInPayload() = runBlocking {
        fakeMetadataDao.setValue(SyncMetadataEntity("mode", SyncMode.PUSH.name))

        val result = adapter.processPushPayload(
            data = mapOf(
                "run_id" to "run-push-200",
            ),
            messageId = "msg-200",
        )

        assertTrue(result is PushProcessingResult.Enqueued)
        val enqueued = result as PushProcessingResult.Enqueued
        assertTrue(enqueued.requestId.startsWith("req-"))

        val event = fakeTimelineDao.events[0]
        assertEquals(enqueued.requestId, event.requestId)

        val input = enqueuedInputs[0]
        assertEquals(enqueued.requestId, input.correlation.requestId)
    }

    private class FakeTimelineDao : TimelineDao {
        val events = mutableListOf<TimelineEventEntity>()

        override fun observeAll(): Flow<List<TimelineEventEntity>> = flowOf(events)

        override suspend fun insert(event: TimelineEventEntity) {
            events.add(event)
        }

        override suspend fun clearAll() {
            events.clear()
        }
    }

    private class FakeSyncMetadataDao : SyncMetadataDao {
        val map = mutableMapOf<String, String>()

        override fun observeValue(key: String): Flow<String?> = flowOf(map[key])

        override suspend fun getValue(key: String): String? = map[key]

        override suspend fun setValue(entry: SyncMetadataEntity) {
            map[entry.key] = entry.value
        }

        override suspend fun deleteValue(key: String) {
            map.remove(key)
        }
    }
}
