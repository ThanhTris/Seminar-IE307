package com.thanhtris.seminarie307.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase

@Database(
    entities = [
        BulletinEntity::class,
        TimelineEventEntity::class,
        SyncMetadataEntity::class,
    ],
    version = 2,
    exportSchema = false,
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun bulletinDao(): BulletinDao
    abstract fun timelineDao(): TimelineDao
    abstract fun metadataDao(): SyncMetadataDao

    companion object {
        private val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("ALTER TABLE timeline_events ADD COLUMN mode TEXT")
                db.execSQL("ALTER TABLE timeline_events ADD COLUMN deviceAlias TEXT")
                db.execSQL("ALTER TABLE timeline_events ADD COLUMN cachedVersion INTEGER")
                db.execSQL("ALTER TABLE timeline_events ADD COLUMN versionHint INTEGER")
                db.execSQL("ALTER TABLE timeline_events ADD COLUMN workAttempt INTEGER")
                db.execSQL("ALTER TABLE timeline_events ADD COLUMN networkCallId TEXT")
                db.execSQL("ALTER TABLE timeline_events ADD COLUMN signalIdsJson TEXT NOT NULL DEFAULT '[]'")
                db.execSQL("ALTER TABLE timeline_events ADD COLUMN httpStatus INTEGER")
            }
        }

        @Volatile
        private var instance: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return instance ?: synchronized(this) {
                instance ?: Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "seminar_bulletin.db",
                )
                    .addMigrations(MIGRATION_1_2)
                    .fallbackToDestructiveMigration(dropAllTables = true)
                    .build()
                    .also { instance = it }
            }
        }
    }
}
