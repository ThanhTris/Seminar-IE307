import android.app.job.JobInfo;
import android.app.job.JobScheduler;
import android.app.job.PendingJobReasonsInfo;
import android.content.Context;
import android.os.Build;
import android.os.Looper;
import android.os.SystemClock;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.time.Duration;
import java.util.Map;
import org.json.JSONArray;
import org.json.JSONObject;

/** Framework-only query under run-as. Never initializes SeminarApp or schedules/cancels work. */
public final class Sem41JobProbe {
    private static final String PACKAGE = "com.thanhtris.seminarie307";
    private static final String NAMESPACE = "androidx.work.systemjobscheduler";

    public static void main(String[] args) {
        try {
            if (Build.VERSION.SDK_INT < 36) throw new IllegalStateException("API_36_REQUIRED");
            Looper.prepare();
            // app_process has no application Context. Bootstrap framework services only;
            // ActivityThread.systemMain does not attach or restart the target application.
            Class<?> activityThread = Class.forName("android.app.ActivityThread");
            Object thread = activityThread.getMethod("systemMain").invoke(null);
            Context context = (Context) activityThread.getMethod("getSystemContext").invoke(thread);
            JobScheduler scheduler = ((JobScheduler) context.getSystemService(Context.JOB_SCHEDULER_SERVICE))
                    .forNamespace(NAMESPACE);
            JSONObject out = new JSONObject();
            out.put("probe_version", "1.0.0");
            out.put("sdk_int", Build.VERSION.SDK_INT);
            out.put("utc_epoch_ms", System.currentTimeMillis());
            out.put("elapsed_realtime_ms", SystemClock.elapsedRealtime());
            out.put("namespace", NAMESPACE);
            out.put("package", PACKAGE);
            out.put("read_only", true);
            JSONArray jobs = new JSONArray();
            for (JobInfo job : scheduler.getAllPendingJobs()) {
                if (!job.getService().getPackageName().equals(PACKAGE)) continue;
                JSONObject row = new JSONObject();
                row.put("job_id", job.getId());
                row.put("service", job.getService().getClassName());
                String workId = job.getExtras().getString("EXTRA_WORK_SPEC_ID");
                row.put("work_id", workId == null ? JSONObject.NULL : workId);
                row.put("generation", job.getExtras().getInt("EXTRA_WORK_SPEC_GENERATION", 0));
                row.put("system_job_is_periodic", job.isPeriodic());
                row.put("minimum_latency_ms", job.getMinLatencyMillis());
                JSONArray history = new JSONArray();
                JSONArray stats = new JSONArray();
                boolean disappeared = false;
                try {
                    row.put("pending_reasons", reasons(scheduler.getPendingJobReasons(job.getId())));
                    for (PendingJobReasonsInfo entry : scheduler.getPendingJobReasonsHistory(job.getId())) {
                        history.put(new JSONObject().put("timestamp_ms", entry.getTimestampMillis())
                                .put("reasons", reasons(entry.getPendingJobReasons())));
                    }
                    if (Build.VERSION.SDK_INT >= 37) {
                        for (Map.Entry<Integer, Duration> entry : scheduler.getPendingJobReasonStats(job.getId()).entrySet()) {
                            stats.put(new JSONObject().put("reason", reason(entry.getKey()))
                                    .put("duration_ms", entry.getValue().toMillis()));
                        }
                    }
                } catch (IllegalArgumentException gone) {
                    // A job may finish/cancel between queries. Record the race, not a false reason.
                    disappeared = true;
                    row.put("pending_reasons", reasons(new int[] {JobScheduler.PENDING_JOB_REASON_INVALID_JOB_ID}));
                    history = new JSONArray();
                    stats = new JSONArray();
                }
                row.put("job_disappeared_during_query", disappeared);
                row.put("history", history);
                row.put("stats", stats);
                jobs.put(row);
            }
            out.put("jobs", jobs);
            System.out.println(out);
            System.exit(0);
        } catch (Throwable failure) {
            // No opaque exception messages or platform dumps in the public output.
            System.err.println("JOB_PROBE_FAILED_" + failure.getClass().getSimpleName());
            System.exit(1);
        }
    }

    private static JSONObject reason(int value) throws Exception {
        String name = "UNKNOWN_" + value;
        for (Field field : JobScheduler.class.getFields()) {
            if (field.getName().startsWith("PENDING_JOB_REASON_") && field.getType() == int.class
                    && Modifier.isStatic(field.getModifiers()) && field.getInt(null) == value) {
                name = field.getName();
                break;
            }
        }
        return new JSONObject().put("code", value).put("name", name);
    }

    private static JSONArray reasons(int[] values) throws Exception {
        JSONArray list = new JSONArray();
        for (int value : values) list.put(reason(value));
        return list;
    }
}
