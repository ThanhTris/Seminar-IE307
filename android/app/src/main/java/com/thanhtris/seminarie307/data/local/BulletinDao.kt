package com.thanhtris.seminarie307.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Transaction
import kotlinx.coroutines.flow.Flow

@Dao
interface BulletinDao {
    @Query("SELECT * FROM bulletin_items ORDER BY version DESC, id ASC")
    fun observeAll(): Flow<List<BulletinEntity>>

    @Query("SELECT MAX(version) FROM bulletin_items")
    suspend fun getLatestVersion(): Long?

    @Query("DELETE FROM bulletin_items")
    suspend fun clearAll()

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(items: List<BulletinEntity>)

    @Transaction
    suspend fun replaceSnapshot(items: List<BulletinEntity>) {
        clearAll()
        insertAll(items)
    }
}
