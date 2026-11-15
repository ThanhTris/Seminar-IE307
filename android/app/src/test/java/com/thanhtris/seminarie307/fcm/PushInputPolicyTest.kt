package com.thanhtris.seminarie307.fcm

import com.thanhtris.seminarie307.data.local.SyncMetadataDao
import com.thanhtris.seminarie307.data.local.SyncMetadataEntity
import com.thanhtris.seminarie307.data.local.TimelineDao
import com.thanhtris.seminarie307.data.local.TimelineEventEntity
import com.thanhtris.seminarie307.integration.SyncMode
import com.thanhtris.seminarie307.sync.SyncInput
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import java.util.Collections
import java.util.UUID

/** SEM-38 cases: duplicate, stale hint, new signal while a worker is running. */
class PushInputPolicyTest {

    private lateinit var timeline: FakeTimelineDao
    private lateinit var metadata: FakeSyncMetadataDao
    private val enqueued = mutableListOf<SyncInput>()
    private var enqueueResult: suspend (SyncInput) -> UUID? = { input ->
        enqueued.add(input)
        UUID.randomUUID()
    }
    private lateinit var adapter: PushSyncEnqueueAdapter

    @Before
    fun setUp() {
        timeline = FakeTimelineDao()
        metadata = FakeSyncMetadataDao()
        metadata.map["mode"] = SyncMode.HYBRID.name
        metadata.map["deviceAlias"] = "emulator-test-1"
        enqueued.clear()
        adapter = newAdapter()
    }

    private fun newAdapter() = PushSyncEnqueueAdapter(timeline, metadata) { enqueueResult(it) }

    private fun payload(
        run: String = "run-e05",
        signal: String? = null,
        hint: String? = null,
        mode: String = "HYBRID",
    ): Map<String, String> = buildMap {
        put("run_id", run)
        put("mode", mode)
        put("source", "PUSH")
        signal?.let { put("signal_id", it) }
        hint?.let { put("version_hint", it) }
    }

    private fun eventTypes() = timeline.events.map { it.eventType }

    // ---- Case A: duplicate -------------------------------------------------------------

    @Test
    fun sameSignalIdWithDifferentFcmMessageIdIsNotEnqueuedTwice() = runBlocking {
        val first = adapter.processPushPayload(payload(signal = "sig-1", hint = "6"), messageId = "m-1")
        val second = adapter.processPushPayload(payload(signal = "sig-1", hint = "6"), messageId = "m-2")

        assertTrue(first is PushProcessingResult.Enqueued)
        assertEquals(PushProcessingResult.Rejected("DUPLICATE_SIGNAL", "run-e05"), second)
        assertEquals(1, enqueued.size)
        // Both callbacks are observed receipts; only the duplicate gets a rejection, no work for it.
        assertEquals(listOf("push_received", "push_received", "trigger_rejected"), eventTypes())
        val rejected = timeline.events.last()
        assertEquals("rejected", rejected.outcome)
        assertEquals("DUPLICATE_SIGNAL", rejected.reason)
        assertEquals("m-2", rejected.messageId)
        assertEquals(null, rejected.version)
        assertEquals(6L, rejected.versionHint)
    }

    @Test
    fun sameFcmMessageIdWithoutSignalIdIsRecognisedAsRedelivery() = runBlocking {
        adapter.processPushPayload(payload(), messageId = "projects/p/messages/abc")
        val second = adapter.processPushPayload(payload(), messageId = "projects/p/messages/abc")

        assertEquals(PushProcessingResult.Rejected("DUPLICATE_SIGNAL", "run-e05"), second)
        assertEquals(1, enqueued.size)
    }

    @Test
    fun duplicateIsRecognisedByNewAdapterInstanceBecauseLedgerIsPersisted() = runBlocking {
        adapter.processPushPayload(payload(signal = "sig-1"), messageId = "m-1")

        val afterProcessRestart = newAdapter().processPushPayload(payload(signal = "sig-1"), messageId = "m-3")

        assertTrue(afterProcessRestart is PushProcessingResult.Rejected)
        assertEquals(1, enqueued.size)
    }

    @Test
    fun sameSignalIdInAnotherRunIsNotADuplicate() = runBlocking {
        adapter.processPushPayload(payload(run = "run-a", signal = "sig-1"), messageId = "m-1")
        val other = adapter.processPushPayload(payload(run = "run-b", signal = "sig-1"), messageId = "m-2")

        assertTrue(other is PushProcessingResult.Enqueued)
        assertEquals(2, enqueued.size)
    }

    @Test
    fun concurrentRedeliveryEnqueuesOnlyOnce() = runBlocking {
        enqueueResult = { input ->
            delay(50) // widen the window between "check" and "record"
            enqueued.add(input)
            UUID.randomUUID()
        }

        val results = (1..4).map { n ->
            async { adapter.processPushPayload(payload(signal = "sig-1"), messageId = "m-$n") }
        }.awaitAll()

        assertEquals(1, results.count { it is PushProcessingResult.Enqueued })
        assertEquals(3, results.count { it is PushProcessingResult.Rejected && it.reason == "DUPLICATE_SIGNAL" })
        assertEquals(1, enqueued.size)
    }

    @Test
    fun failedEnqueueIsNotRememberedSoSenderRetryWithSameSignalIdIsProcessed() = runBlocking {
        enqueueResult = { null }
        val failed = adapter.processPushPayload(payload(signal = "sig-1"), messageId = "m-1")
        assertEquals(PushProcessingResult.Rejected("WORK_ENQUEUE_FAILED", "run-e05"), failed)

        enqueueResult = { input ->
            enqueued.add(input)
            UUID.randomUUID()
        }
        val retry = adapter.processPushPayload(payload(signal = "sig-1"), messageId = "m-2")

        assertTrue(retry is PushProcessingResult.Enqueued)
        assertEquals(1, enqueued.size)
    }

    @Test
    fun enqueueExceptionIsNotRemembered() = runBlocking {
        enqueueResult = { error("boom") }
        adapter.processPushPayload(payload(signal = "sig-1"), messageId = "m-1")

        enqueueResult = { input ->
            enqueued.add(input)
            UUID.randomUUID()
        }
        val retry = adapter.processPushPayload(payload(signal = "sig-1"), messageId = "m-2")

        assertTrue(retry is PushProcessingResult.Enqueued)
    }

    @Test
    fun modeDisabledRejectionDoesNotConsumeTheSignal() = runBlocking {
        metadata.map["mode"] = SyncMode.PERIODIC.name
        val blocked = adapter.processPushPayload(payload(signal = "sig-1"), messageId = "m-1")
        assertEquals(PushProcessingResult.Rejected("MODE_DISABLED", "run-e05"), blocked)

        metadata.map["mode"] = SyncMode.PUSH.name
        val later = adapter.processPushPayload(payload(signal = "sig-1", mode = "PUSH"), messageId = "m-2")

        assertTrue(later is PushProcessingResult.Enqueued)
    }

    @Test
    fun signalsWithoutUsableIdsCannotBeDeduplicatedAndAreNotDropped() = runBlocking {
        adapter.processPushPayload(payload(), messageId = null)
        adapter.processPushPayload(payload(signal = "bad id with spaces"), messageId = null)
        adapter.processPushPayload(payload(signal = "bad id with spaces"), messageId = null)

        assertEquals(3, enqueued.size)
        assertEquals(null, metadata.map[PushInputPolicy.LEDGER_KEY])
    }

    @Test
    fun duplicateNeverCreatesNotificationOrSecondEnginePath() = runBlocking {
        adapter.processPushPayload(payload(signal = "sig-1"), messageId = "m-1")
        adapter.processPushPayload(payload(signal = "sig-1"), messageId = "m-2")

        // Only timeline rows and the shared enqueue lambda are touched: no event types other than these.
        assertTrue(eventTypes().all { it in setOf("push_received", "trigger_rejected") })
        assertEquals(1, enqueued.size)
    }

    // ---- Case B: old / equal hint -----------------------------------------------------

    @Test
    fun hintOlderOrEqualToCacheIsStillEnqueuedBecauseWorkerFetchesCurrentSnapshot() = runBlocking {
        metadata.map["cachedVersion"] = "5"

        val older = adapter.processPushPayload(payload(signal = "sig-old", hint = "3"), messageId = "m-1")
        val equal = adapter.processPushPayload(payload(signal = "sig-eq", hint = "5"), messageId = "m-2")

        assertTrue(older is PushProcessingResult.Enqueued)
        assertTrue(equal is PushProcessingResult.Enqueued)
        assertEquals(listOf(3L, 5L), enqueued.map { it.versionHint })
        assertFalse("trigger_rejected" in eventTypes())
    }

    @Test
    fun repeatedHintWithNewSignalIdIsEnqueued() = runBlocking {
        adapter.processPushPayload(payload(signal = "sig-1", hint = "6"), messageId = "m-1")
        val second = adapter.processPushPayload(payload(signal = "sig-2", hint = "6"), messageId = "m-2")

        assertTrue(second is PushProcessingResult.Enqueued)
        assertEquals(2, enqueued.size)
    }

    // ---- Case C: new signal while a worker is running -----------------------------------

    @Test
    fun newerSignalWhileEarlierWorkIsPendingIsEnqueuedNotSkipped() = runBlocking {
        // The earlier work (hint 6) is still queued/running: the adapter has no completion callback.
        val running = adapter.processPushPayload(payload(signal = "sig-v6", hint = "6"), messageId = "m-6")
        val newer = adapter.processPushPayload(payload(signal = "sig-v7", hint = "7"), messageId = "m-7")

        assertTrue(running is PushProcessingResult.Enqueued)
        assertTrue(newer is PushProcessingResult.Enqueued)
        assertTrue((running as PushProcessingResult.Enqueued).workId != (newer as PushProcessingResult.Enqueued).workId)
        assertEquals(listOf(6L, 7L), enqueued.map { it.versionHint })
    }

    // ---- Pure policy ---------------------------------------------------------------------

    @Test
    fun ledgerIsCappedToNewestEntriesAndKeepsKeysUnique() {
        var raw = ""
        for (i in 1..(PushInputPolicy.MAX_LEDGER_ENTRIES + 10)) {
            raw = PushInputPolicy.record(PushInputPolicy.parseLedger(raw), listOf("r|sig|s$i"))
        }
        val ledger = PushInputPolicy.parseLedger(raw)

        assertEquals(PushInputPolicy.MAX_LEDGER_ENTRIES, ledger.size)
        assertFalse(PushInputPolicy.isDuplicate(ledger, listOf("r|sig|s1")))
        assertTrue(PushInputPolicy.isDuplicate(ledger, listOf("r|sig|s${PushInputPolicy.MAX_LEDGER_ENTRIES + 10}")))

        val again = PushInputPolicy.parseLedger(PushInputPolicy.record(ledger, listOf(ledger.last())))
        assertEquals(ledger.size, again.size)
    }

    @Test
    fun keysUseRunScopeAndOnlyUsableIds() {
        assertEquals(
            listOf("r|sig|s1", "r|msg|projects/p/messages/1"),
            PushInputPolicy.keysFor("r", "s1", "projects/p/messages/1"),
        )
        assertTrue(PushInputPolicy.keysFor("r", "not valid", "has space").isEmpty())
        assertTrue(PushInputPolicy.keysFor("r", null, "x".repeat(513)).isEmpty())
        assertFalse(PushInputPolicy.isDuplicate(emptyList(), emptyList()))
    }

    // ---- Fakes -----------------------------------------------------------------------------

    private class FakeTimelineDao : TimelineDao {
        val events: MutableList<TimelineEventEntity> = Collections.synchronizedList(mutableListOf())
        override fun observeAll(): Flow<List<TimelineEventEntity>> = flowOf(events)
        override suspend fun getAllForRun(runId: String): List<TimelineEventEntity> = events.filter { it.runId == runId }
        override suspend fun insert(event: TimelineEventEntity) {
            events.add(event)
        }
        override suspend fun clearAll() {
            events.clear()
        }
    }

    private class FakeSyncMetadataDao : SyncMetadataDao {
        val map: MutableMap<String, String?> = Collections.synchronizedMap(mutableMapOf())
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
