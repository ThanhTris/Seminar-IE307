package com.thanhtris.seminarie307.experiments

import android.os.SystemClock
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.work.WorkManager
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.data.local.CanonicalTimelineExporter
import com.thanhtris.seminarie307.data.local.SyncMetadataEntity
import com.thanhtris.seminarie307.data.remote.RemoteSnapshotResult
import com.thanhtris.seminarie307.data.remote.SnapshotRemoteDataSource
import com.thanhtris.seminarie307.integration.SyncMode
import com.thanhtris.seminarie307.sync.PeriodicSyncScheduler
import kotlinx.coroutines.runBlocking
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.time.Instant
import java.util.UUID

/** SEM-29 setup/export adapter. Invoke outside the natural observation window. */
@RunWith(AndroidJUnit4::class)
class PeriodicPilotControl {
    @Test
    fun control() = runBlocking {
        val arguments = InstrumentationRegistry.getArguments()
        val action = arguments.getString("sem29_action")
        assumeTrue("SEM-29 requires an explicit action", action != null)
        val runId = requireNotNull(arguments.getString("sem29_run_id"))
        require(Regex("^[A-Za-z0-9][A-Za-z0-9._-]{0,100}$").matches(runId))
        require(action in setOf("probe", "diagnose", "register", "snapshot", "cancel", "export-v2"))

        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val database = AppDatabase.getInstance(context)
        val scheduler = PeriodicSyncScheduler(context, database)
        val manager = WorkManager.getInstance(context)

        when (action) {
            "probe" -> {
                val result = SnapshotRemoteDataSource().fetchSnapshot(requestId = "req-${UUID.randomUUID()}")
                assertTrue("The actual app network client must reach the v2 server", result is RemoteSnapshotResult.Success)
            }
            "diagnose" -> {
                assertTrue("Existing periodic work needs a separate handoff", activeIds(manager).isEmpty())
                val first = scheduler.schedulePeriodicSync(SyncMode.PERIODIC, runId, "emulator-main")
                assertNotNull(first)
                val second = scheduler.schedulePeriodicSync(SyncMode.PERIODIC, runId, "emulator-main")
                assertEquals(first, second)
                assertEquals(listOf(first.toString()), activeIds(manager))
                scheduler.cancelPeriodicSync(runId)
                assertTrue("Cancellation must leave no active unique work", activeIds(manager).isEmpty())
            }
            "register" -> {
                assertTrue("An existing schedule would contaminate this run", activeIds(manager).isEmpty())
                database.metadataDao().setValue(SyncMetadataEntity("mode", "PERIODIC"))
                assertNotNull(scheduler.schedulePeriodicSync(SyncMode.PERIODIC, runId, "emulator-main"))
                database.metadataDao().setValue(SyncMetadataEntity("deviceAlias", "emulator-main"))
                assertEquals(1, activeIds(manager).size)
            }
            "cancel" -> {
                scheduler.cancelPeriodicSync(runId)
                assertTrue("Cancellation must leave no active unique work", activeIds(manager).isEmpty())
            }
        }

        // Export the actual legacy Room columns, preserving their names and values.
        // Missing v2 measurements require producer changes and cannot be reconstructed here.
        val directory = File(context.filesDir, "sem29/$runId").apply { mkdirs() }
        val rows = mutableListOf<JSONObject>()
        database.openHelper.readableDatabase.query(
            "SELECT * FROM timeline_events WHERE runId = ? ORDER BY occurredAtEpochMillis, eventId",
            arrayOf(runId),
        ).use { cursor ->
            while (cursor.moveToNext()) {
                val row = JSONObject()
                for (index in 0 until cursor.columnCount) {
                    val value = when (cursor.getType(index)) {
                        android.database.Cursor.FIELD_TYPE_NULL -> JSONObject.NULL
                        android.database.Cursor.FIELD_TYPE_INTEGER -> cursor.getLong(index)
                        else -> cursor.getString(index)
                    }
                    row.put(cursor.getColumnName(index), value)
                }
                rows.add(row)
            }
        }
        File(directory, "$action-events-legacy.jsonl").writeText(
            rows.joinToString(separator = "\n", postfix = if (rows.isEmpty()) "" else "\n") { it.toString() }
        )
        if (action == "export-v2") {
            val events = database.timelineDao().getAllForRun(runId)
            val canonical = mutableListOf<String>()
            val omitted = mutableListOf<JSONObject>()
            events.forEach { event ->
                runCatching { CanonicalTimelineExporter.export(listOf(event)) }
                    .onSuccess { canonical.add(it) }
                    .onFailure { failure ->
                        omitted += JSONObject().apply {
                            put("event_id", event.eventId)
                            put("event_type", event.eventType)
                            put("reason", failure.message ?: "CANONICAL_VALIDATION_FAILED")
                        }
                    }
            }
            File(directory, "events-v2.jsonl").writeText(
                canonical.joinToString(separator = "\n", postfix = if (canonical.isEmpty()) "" else "\n")
            )
            File(directory, "events-v2-export-report.json").writeText(JSONObject().apply {
                put("schema_version", "2.0.0")
                put("status", when {
                    events.isEmpty() -> "EMPTY"
                    omitted.isNotEmpty() -> "PARTIAL"
                    else -> "COMPLETE"
                })
                put("exported_event_count", canonical.size)
                put("omitted_event_count", omitted.size)
                put("omitted_events", JSONArray(omitted))
                put("source_format", "legacy-room-v1 plus captured schema-2 fields")
            }.toString(2) + "\n")
        }
        val works = JSONArray()
        manager.getWorkInfosForUniqueWork(PeriodicSyncScheduler.PERIODIC_WORK_NAME).get().forEach { work ->
            works.put(JSONObject().apply {
                put("work_id", work.id.toString())
                put("state", work.state.name)
                put("run_attempt_count", work.runAttemptCount)
            })
        }
        File(directory, "$action-state.json").writeText(JSONObject().apply {
            put("captured_at_utc", Instant.now().toString())
            put("elapsed_realtime_ms", SystemClock.elapsedRealtime())
            put("run_id", runId)
            put("action", action)
            put("event_format", if (action == "export-v2") "canonical-2.0.0-export-attempt" else "legacy-room-v1")
            put("cached_version", database.metadataDao().getValue("cachedVersion") ?: JSONObject.NULL)
            put("mode", database.metadataDao().getValue("mode") ?: JSONObject.NULL)
            put("periodic_work", works)
        }.toString(2) + "\n")
    }

    private fun activeIds(manager: WorkManager): List<String> = manager
        .getWorkInfosForUniqueWork(PeriodicSyncScheduler.PERIODIC_WORK_NAME).get()
        .filter { !it.state.isFinished }
        .map { it.id.toString() }
}
