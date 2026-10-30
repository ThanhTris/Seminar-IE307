package com.thanhtris.seminarie307.ui

import com.thanhtris.seminarie307.integration.TimelineEvent

/** Blank means all runs; non-blank input is trimmed and compared exactly, case-sensitively. */
fun filterTimeline(events: List<TimelineEvent>, input: String): List<TimelineEvent> {
    val runId = input.trim()
    if (runId.isEmpty()) return events.sortedByDescending(TimelineEvent::occurredAtEpochMillis)
    return events
        .asSequence()
        .filter { it.runId == runId }
        .sortedByDescending(TimelineEvent::occurredAtEpochMillis)
        .toList()
}
