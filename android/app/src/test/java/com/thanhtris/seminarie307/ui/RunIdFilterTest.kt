package com.thanhtris.seminarie307.ui

import com.thanhtris.seminarie307.integration.SyncSource
import com.thanhtris.seminarie307.integration.TimelineEvent
import org.junit.Assert.assertEquals
import org.junit.Test

class RunIdFilterTest {
    private val events = listOf(
        event("a-older", "run-a", 10),
        event("ab-newer", "run-ab", 30),
        event("a-newer", "run-a", 20),
    )

    @Test
    fun blankFilterShowsAllNewestFirst() {
        assertEquals(listOf("ab-newer", "a-newer", "a-older"), filterTimeline(events, "  ").map { it.eventId })
    }

    @Test
    fun filterTrimsEndsButMatchesRunIdExactlyAndCaseSensitively() {
        assertEquals(listOf("a-newer", "a-older"), filterTimeline(events, " run-a ").map { it.eventId })
        assertEquals(emptyList<TimelineEvent>(), filterTimeline(events, "RUN-A"))
        assertEquals(listOf("ab-newer"), filterTimeline(events, "run-ab").map { it.eventId })
    }

    private fun event(id: String, runId: String, time: Long) = TimelineEvent(
        eventId = id,
        source = SyncSource.MANUAL,
        eventType = "test_event",
        occurredAtEpochMillis = time,
        occurredAtUtc = "1970-01-01T00:00:00Z",
        runId = runId,
    )
}
