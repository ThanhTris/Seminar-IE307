package com.thanhtris.seminarie307.experiments

import android.app.NotificationManager
import android.os.SystemClock
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.work.WorkManager
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.data.local.SyncMetadataEntity
import com.thanhtris.seminarie307.fcm.FcmTokenKeys
import com.thanhtris.seminarie307.fcm.FcmTokenStatus
import com.thanhtris.seminarie307.sync.PeriodicSyncScheduler
import com.thanhtris.seminarie307.sync.SyncWorker
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.time.Instant

/** SEM-34 setup and read-only capture. Invoke outside the E02 observation window. */
@RunWith(AndroidJUnit4::class)
class PushPilotControl {
    @Test
    fun control() = runBlocking {
        val arguments = InstrumentationRegistry.getArguments()
        val action = arguments.getString("sem34_action")
        assumeTrue("SEM-34 requires an explicit action", action != null)
        require(action in setOf("preflight", "prepare", "snapshot", "cleanup"))
        val runId = requireNotNull(arguments.getString("sem34_run_id"))
        require(Regex("^[A-Za-z0-9][A-Za-z0-9._-]{0,100}$").matches(runId))
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val database = AppDatabase.getInstance(context)
        val metadata = database.metadataDao()
        val manager = WorkManager.getInstance(context)
        val directory = File(context.filesDir, "sem34/$runId").apply { mkdirs() }
        val setup = File(directory, "setup.json")
        val periodicName = PeriodicSyncScheduler.PERIODIC_WORK_NAME

        when (action) {
            "prepare" -> {
                check(!setup.exists()) { "This run was already prepared; preserve its setup" }
                check(metadata.getValue(FcmTokenKeys.STATUS) == FcmTokenStatus.READY.name) {
                    "A current Firebase token is required before preparing E02"
                }
                check(File(context.filesDir, "fcm/device-token.txt").length() > 0)
                val periodicIds = manager.getWorkInfosForUniqueWork(periodicName).get().map { it.id }.toSet()
                val active = manager.getWorkInfosByTag(SyncWorker::class.java.name).get().filter { !it.state.isFinished }
                check(active.all { it.id in periodicIds }) { "Drain existing one-time sync work first" }
                PeriodicSyncScheduler(context, database).cancelPeriodicSync(runId)
                assertTrue(manager.getWorkInfosByTag(SyncWorker::class.java.name).get().none { !it.state.isFinished })
                setup.writeText(JSONObject().put("previous_mode", metadata.getValue("mode") ?: JSONObject.NULL).toString())
                metadata.setValue(SyncMetadataEntity("mode", "PUSH"))
            }
            "cleanup" -> {
                check(setup.exists()) { "This run has no saved setup to restore" }
                check(manager.getWorkInfosByTag(SyncWorker::class.java.name).get().none { !it.state.isFinished }) {
                    "Keep the device reserved until sync work has drained"
                }
                val previous = JSONObject(setup.readText())
                if (previous.isNull("previous_mode")) metadata.deleteValue("mode")
                else metadata.setValue(SyncMetadataEntity("mode", previous.getString("previous_mode")))
            }
        }

        val rows = JSONArray()
        database.timelineDao().observeAll().first()
            .filter { it.runId == runId }
            .sortedWith(compareBy({ it.occurredAtEpochMillis }, { it.eventId }))
            .forEach { event ->
                rows.put(JSONObject().apply {
                    put("eventId", event.eventId)
                    put("source", event.source ?: JSONObject.NULL)
                    put("eventType", event.eventType)
                    put("occurredAtEpochMillis", event.occurredAtEpochMillis)
                    put("occurredAtUtc", event.occurredAtUtc)
                    put("runId", event.runId ?: JSONObject.NULL)
                    put("version", event.version ?: JSONObject.NULL)
                    put("outcome", event.outcome ?: JSONObject.NULL)
                    put("reason", event.reason ?: JSONObject.NULL)
                    put("requestId", event.requestId ?: JSONObject.NULL)
                    put("workId", event.workId ?: JSONObject.NULL)
                    put("messageId", event.messageId ?: JSONObject.NULL)
                    put("elapsedRealtimeMillis", event.elapsedRealtimeMillis ?: JSONObject.NULL)
                })
            }
        File(directory, "$action-events-legacy.jsonl").writeText(
            (0 until rows.length()).joinToString("") { rows.getJSONObject(it).toString() + "\n" }
        )
        val periodic = manager.getWorkInfosForUniqueWork(periodicName).get()
        val activeSync = manager.getWorkInfosByTag(SyncWorker::class.java.name).get().count { !it.state.isFinished }
        val notifications = context.getSystemService(NotificationManager::class.java).activeNotifications.size
        File(directory, "$action-state.json").writeText(JSONObject().apply {
            put("captured_at_utc", Instant.now().toString())
            put("elapsed_realtime_ms", SystemClock.elapsedRealtime())
            put("action", action)
            put("run_id", runId)
            put("android_event_format", "legacy-room-v1")
            put("mode", metadata.getValue("mode") ?: JSONObject.NULL)
            put("cached_version", metadata.getValue("cachedVersion") ?: JSONObject.NULL)
            put("fcm_token_status", metadata.getValue(FcmTokenKeys.STATUS) ?: JSONObject.NULL)
            put("debug_token_file_present", File(context.filesDir, "fcm/device-token.txt").length() > 0)
            put("active_periodic_work_count", periodic.count { !it.state.isFinished })
            put("active_sync_work_count", activeSync)
            put("active_app_notification_count", notifications)
        }.toString(2) + "\n")
    }
}
