package com.thanhtris.seminarie307.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface TimelineDao {
    @Query("SELECT * FROM timeline_events ORDER BY occurredAtEpochMillis DESC")
    fun observeAll(): Flow<List<TimelineEventEntity>>

    @Query("SELECT * FROM timeline_events WHERE runId = :runId ORDER BY occurredAtEpochMillis, eventId")
    suspend fun getAllForRun(runId: String): List<TimelineEventEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(event: TimelineEventEntity)

    @Query("DELETE FROM timeline_events")
    suspend fun clearAll()
}
