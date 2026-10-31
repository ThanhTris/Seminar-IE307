package com.thanhtris.seminarie307.data.local

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.thanhtris.seminarie307.integration.BulletinItem

@Entity(tableName = "bulletin_items")
data class BulletinEntity(
    @PrimaryKey val id: String,
    val title: String,
    val body: String,
    val version: Long,
) {
    fun toBulletinItem(): BulletinItem = BulletinItem(
        id = id,
        title = title,
        body = body,
        version = version,
    )

    companion object {
        fun fromBulletinItem(item: BulletinItem): BulletinEntity = BulletinEntity(
            id = item.id,
            title = item.title,
            body = item.body,
            version = item.version,
        )
    }
}
