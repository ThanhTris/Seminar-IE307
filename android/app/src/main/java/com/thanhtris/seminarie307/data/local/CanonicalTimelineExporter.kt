package com.thanhtris.seminarie307.data.local

import com.thanhtris.seminarie307.integration.JsonStringArrayCodec
import java.time.Instant

/** Serializes only rows that carry enough captured provenance to satisfy EVENT_SCHEMA 2.0.0. */
object CanonicalTimelineExporter {
    private val appId = Regex("^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
    private val uuid = Regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")
    private val eventTypes = setOf(
        "push_received", "trigger_rejected", "periodic_registered", "work_enqueued", "work_started",
        "snapshot_fetch_started", "snapshot_fetch_completed", "snapshot_applied", "snapshot_unchanged",
        "snapshot_stale", "sync_retrying", "sync_failed",
    )
    private val reasonCode = Regex("^[A-Z][A-Z0-9_]{0,63}$")

    /** Returns JSONL or fails closed; legacy/incomplete rows are never relabeled as schema 2.0.0. */
    fun export(events: List<TimelineEventEntity>): String = events.joinToString("\n") { event ->
        require(uuid.matches(event.eventId)) { "Invalid event_id; cannot export canonical schema 2.0.0" }
        require(event.eventType in eventTypes) { "Unsupported event_type '${event.eventType}'; cannot export canonical schema 2.0.0" }
        val runId = event.runId?.takeIf(appId::matches)
            ?: error("Missing valid run_id for event ${event.eventId}")
        val mode = event.mode?.takeIf { it in setOf("PERIODIC", "PUSH", "HYBRID") }
            ?: error("Missing captured mode for event ${event.eventId}")
        val deviceAlias = event.deviceAlias?.takeIf(appId::matches)
            ?: error("Missing captured device_alias for event ${event.eventId}")
        val source = event.source?.takeIf { it in setOf("MANUAL", "PERIODIC", "PUSH") }
            ?: error("Missing valid source for event ${event.eventId}")
        val outcome = event.outcome?.takeIf(String::isNotBlank)
            ?: error("Missing outcome for event ${event.eventId}")
        require(event.reason == null || reasonCode.matches(event.reason)) {
            "Unsafe/noncanonical reason for event ${event.eventId}"
        }
        val signalIds = JsonStringArrayCodec.decode(event.signalIdsJson)
        require(signalIds.all(appId::matches)) {
            "Invalid signal_ids for event ${event.eventId}"
        }
        require(event.occurredAtUtc.endsWith("Z")) { "Non-UTC timestamp for event ${event.eventId}" }
        Instant.parse(event.occurredAtUtc)
        require(event.elapsedRealtimeMillis == null || event.elapsedRealtimeMillis >= 0) {
            "Invalid elapsed_realtime_ms for event ${event.eventId}"
        }
        require(event.version == null || event.version in 0..MAX_SAFE_JSON_INTEGER)
        require(event.cachedVersion == null || event.cachedVersion in 0..MAX_SAFE_JSON_INTEGER)
        require(event.versionHint == null || event.versionHint in 0..MAX_SAFE_JSON_INTEGER)
        require(event.requestId == null || appId.matches(event.requestId))
        require(event.workId == null || uuid.matches(event.workId))
        require(event.workAttempt == null || event.workAttempt >= 0)
        require(event.networkCallId == null || uuid.matches(event.networkCallId))
        require(event.messageId == null || event.messageId.length in 1..512)
        require(event.httpStatus == null || event.httpStatus in 100..599)
        require(
            when (event.eventType) {
                "push_received" -> source == "PUSH" && outcome == "received" && signalIds.size == 1
                "trigger_rejected" -> outcome == "rejected" && event.reason != null
                "periodic_registered" -> source == "PERIODIC" && outcome == "registered" && event.requestId == null && event.workId != null
                "work_enqueued" -> source in setOf("MANUAL", "PUSH") && outcome == "enqueued" && event.requestId != null && event.workId != null
                "work_started" -> outcome == "started" && hasWorkerCorrelation(event) && event.version == null
                "snapshot_fetch_started" -> outcome == "started" && hasWorkerCorrelation(event) && event.networkCallId != null && event.version == null
                "snapshot_fetch_completed" -> hasWorkerCorrelation(event) && event.networkCallId != null && when (outcome) {
                    "success" -> event.httpStatus == 200 && event.version != null
                    "not_modified" -> event.httpStatus == 304 && event.version == null
                    "failure" -> event.reason != null
                    else -> false
                }
                "snapshot_applied" -> outcome == "applied" && hasWorkerCorrelation(event) && event.version != null && event.cachedVersion == event.version
                "snapshot_unchanged" -> outcome == "unchanged" && hasWorkerCorrelation(event) && event.cachedVersion != null
                "snapshot_stale" -> outcome == "stale" && hasWorkerCorrelation(event) && event.version != null &&
                    event.cachedVersion != null && event.cachedVersion > event.version && event.reason == "VERSION_STALE"
                "sync_retrying" -> outcome == "retry" && hasWorkerCorrelation(event) && event.reason != null && event.version == null
                "sync_failed" -> outcome == "failure" && hasWorkerCorrelation(event) && event.reason != null && event.version == null
                else -> false
            },
        ) { "Event type/outcome fields do not satisfy EVENT_SCHEMA 2.0.0 for ${event.eventId}" }
        if (event.source == "PERIODIC") require(mode in setOf("PERIODIC", "HYBRID"))
        if (event.source == "PUSH" && event.eventType !in setOf("push_received", "trigger_rejected")) {
            require(mode in setOf("PUSH", "HYBRID"))
        }
        if (event.eventType in setOf("trigger_rejected", "snapshot_stale", "sync_retrying", "sync_failed")) {
            require(event.reason != null)
        }

        fun json(value: String): String = JsonStringArrayCodec.quoteString(value)
        fun nullable(value: Any?): String = value?.let { jsonScalar(it) } ?: "null"
        JsonStringArrayCodec.objectOf(
            listOf(
                "schema_version" to json("2.0.0"),
                "event_id" to json(event.eventId),
                "event_type" to json(event.eventType),
                "origin" to json("ANDROID"),
                "run_id" to json(runId),
                "mode" to json(mode),
                "source" to json(source),
                "device_alias" to json(deviceAlias),
                "timestamp_utc" to json(event.occurredAtUtc),
                "elapsed_realtime_ms" to nullable(event.elapsedRealtimeMillis),
                "boot_session_id" to "null",
                "data_version" to nullable(event.version),
                "cached_version" to nullable(event.cachedVersion),
                "version_hint" to nullable(event.versionHint),
                "request_id" to nullable(event.requestId),
                "work_id" to nullable(event.workId),
                "work_attempt" to nullable(event.workAttempt),
                "network_call_id" to nullable(event.networkCallId),
                "update_id" to "null",
                "signal_ids" to JsonStringArrayCodec.encode(signalIds),
                "send_attempt_id" to "null",
                "message_id" to nullable(event.messageId),
                "ttl_ms" to "null",
                "http_status" to nullable(event.httpStatus),
                "provider_code" to "null",
                "outcome" to json(outcome),
                "reason" to nullable(event.reason),
            ),
        )
    }

    private fun jsonScalar(value: Any): String = when (value) {
        is String -> JsonStringArrayCodec.quoteString(value)
        is Number -> value.toString()
        is Boolean -> value.toString()
        else -> error("Unsupported JSON scalar ${value::class.simpleName}")
    }

    private fun hasWorkerCorrelation(event: TimelineEventEntity): Boolean =
        event.requestId != null && event.workId != null && event.workAttempt != null

    private const val MAX_SAFE_JSON_INTEGER = 9_007_199_254_740_991L
}
