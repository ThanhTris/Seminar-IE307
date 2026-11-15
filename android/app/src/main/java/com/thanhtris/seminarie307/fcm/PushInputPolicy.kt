package com.thanhtris.seminarie307.fcm

/**
 * Messaging-side input policy for push signals (SEM-38). Pure, Android-free and unit-testable.
 *
 * What it does: recognises **exact redelivery** of a signal that has already been handed to the
 * shared enqueuer, using the server `signal_id` and the FCM `message_id`, scoped by `run_id`.
 *
 * What it deliberately does NOT do:
 * - It never drops a signal because its `version_hint` is old, equal or lower than the cache.
 *   `version_hint` is only a hint (docs/EVENT_SCHEMA.md and protocol E05-B): the worker must still GET
 *   the current snapshot, and the core version guard in `SyncRepository` decides applied /
 *   unchanged / stale. A stale hint can sit next to a newer server snapshot.
 * - It never drops a signal that carries a signal_id/message_id not seen before, so a newer
 *   signal arriving while a worker runs is always enqueued (E05-C).
 * - It never rewrites the core transaction or version guard.
 *
 * The ledger is a bounded, newest-last list of keys persisted in Room `sync_metadata`, so it
 * survives process death. Keys are only recorded **after** a successful enqueue, so a signal whose
 * enqueue failed can be retried by the sender with the same `signal_id`.
 */
internal object PushInputPolicy {
    /** `sync_metadata` key holding the newline-separated ledger. */
    const val LEDGER_KEY = "pushSeenSignalKeys"

    /** Newest entries kept; older ones fall off (FCM TTL can be up to 28 days, so a time window is not used). */
    const val MAX_LEDGER_ENTRIES = 64

    /** Event `reason` for an exact redelivery that was not enqueued again. */
    const val REASON_DUPLICATE_SIGNAL = "DUPLICATE_SIGNAL"

    private const val MAX_MESSAGE_ID_LENGTH = 512

    /** A signal id is only usable for dedupe when it follows the shared application ID pattern. */
    fun usableSignalId(raw: String?): String? =
        raw?.takeIf { PushSyncEnqueueAdapter.APP_ID_PATTERN.matches(it) }

    /** FCM message ids are opaque; only require a bounded single token so the ledger stays parseable. */
    fun usableMessageId(raw: String?): String? =
        raw?.takeIf { it.length in 1..MAX_MESSAGE_ID_LENGTH && it.none(Char::isWhitespace) }

    /** Dedupe keys for one callback; empty when neither id is usable (then nothing can be deduplicated). */
    fun keysFor(runId: String, signalId: String?, messageId: String?): List<String> = buildList {
        usableSignalId(signalId)?.let { add("$runId|sig|$it") }
        usableMessageId(messageId)?.let { add("$runId|msg|$it") }
    }

    fun parseLedger(raw: String?): List<String> =
        raw?.split('\n')?.filter { it.isNotEmpty() } ?: emptyList()

    fun isDuplicate(ledger: List<String>, keys: List<String>): Boolean {
        if (keys.isEmpty()) return false
        val seen = ledger.toHashSet()
        return keys.any { it in seen }
    }

    /** Returns the serialized ledger with [keys] appended (de-duplicated) and capped to the newest entries. */
    fun record(ledger: List<String>, keys: List<String>): String {
        val merged = ledger.filterNot { it in keys } + keys
        return merged.takeLast(MAX_LEDGER_ENTRIES).joinToString("\n")
    }
}
