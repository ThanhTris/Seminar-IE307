package com.thanhtris.seminarie307.data.local

import org.json.JSONArray
import org.json.JSONObject
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
        val signalIds = JSONArray(event.signalIdsJson)
        require((0 until signalIds.length()).all { signalIds.optString(it).let(appId::matches) }) {
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
                "push_received" -> source == "PUSH" && outcome == "received" && signalIds.length() == 1
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

        JSONObject().apply {
            put("schema_version", "2.0.0")
            put("event_id", event.eventId)
            put("event_type", event.eventType)
            put("origin", "ANDROID")
            put("run_id", runId)
            put("mode", mode)
            put("source", source)
            put("device_alias", deviceAlias)
            put("timestamp_utc", event.occurredAtUtc)
            putNullable("elapsed_realtime_ms", event.elapsedRealtimeMillis)
            put("boot_session_id", JSONObject.NULL)
            putNullable("data_version", event.version)
            putNullable("cached_version", event.cachedVersion)
            putNullable("version_hint", event.versionHint)
            putNullable("request_id", event.requestId)
            putNullable("work_id", event.workId)
            putNullable("work_attempt", event.workAttempt)
            putNullable("network_call_id", event.networkCallId)
            put("update_id", JSONObject.NULL)
            put("signal_ids", signalIds)
            put("send_attempt_id", JSONObject.NULL)
            putNullable("message_id", event.messageId)
            put("ttl_ms", JSONObject.NULL)
            putNullable("http_status", event.httpStatus)
            put("provider_code", JSONObject.NULL)
            put("outcome", outcome)
            putNullable("reason", event.reason)
        }.toString()
    }

    private fun JSONObject.putNullable(key: String, value: Any?) {
        put(key, value ?: JSONObject.NULL)
    }

    private fun hasWorkerCorrelation(event: TimelineEventEntity): Boolean =
        event.requestId != null && event.workId != null && event.workAttempt != null

    private const val MAX_SAFE_JSON_INTEGER = 9_007_199_254_740_991L
}
