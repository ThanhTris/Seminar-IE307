package com.thanhtris.seminarie307.data.remote

import com.thanhtris.seminarie307.integration.BulletinItem
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

sealed interface RemoteSnapshotResult {
    data class Success(
        val version: Long,
        val lastModifiedUtc: String,
        val items: List<BulletinItem>,
    ) : RemoteSnapshotResult

    data object NotModified : RemoteSnapshotResult

    data class Failure(
        val statusCode: Int?,
        val message: String,
        val isTransient: Boolean = false,
    ) : RemoteSnapshotResult
}

class SnapshotRemoteDataSource(
    customBaseUrl: String? = null,
) {
    val baseUrl: String = (customBaseUrl ?: defaultBaseUrl).trimEnd('/')

    suspend fun fetchSnapshot(
        currentVersion: Long? = null,
        requestId: String? = null,
    ): RemoteSnapshotResult = withContext(Dispatchers.IO) {
        var connection: HttpURLConnection? = null
        try {
            val url = URL("$baseUrl/api/bulletin")
            connection = (url.openConnection() as HttpURLConnection).apply {
                requestMethod = "GET"
                connectTimeout = 5000
                readTimeout = 5000
                setRequestProperty("Accept", "application/json")
                if (currentVersion != null) {
                    setRequestProperty("If-None-Match", "\"v$currentVersion\"")
                }
                if (!requestId.isNullOrBlank()) {
                    setRequestProperty("X-Correlation-Request-Id", requestId)
                }
            }

            val statusCode = connection.responseCode
            if (statusCode == HttpURLConnection.HTTP_NOT_MODIFIED) {
                return@withContext RemoteSnapshotResult.NotModified
            }

            if (statusCode == HttpURLConnection.HTTP_OK) {
                val responseText = connection.inputStream.bufferedReader().use { it.readText() }
                val json = JSONObject(responseText)
                val version = json.getLong("version")
                val lastModifiedUtc = json.optString("last_modified_utc", "")
                val itemsJson = json.getJSONArray("items")

                val items = mutableListOf<BulletinItem>()
                for (i in 0 until itemsJson.length()) {
                    val itemObj = itemsJson.getJSONObject(i)
                    items.add(
                        BulletinItem(
                            id = itemObj.getString("id"),
                            title = itemObj.getString("title"),
                            body = itemObj.getString("body"),
                            version = itemObj.optLong("version", version),
                        )
                    )
                }

                return@withContext RemoteSnapshotResult.Success(
                    version = version,
                    lastModifiedUtc = lastModifiedUtc,
                    items = items,
                )
            }

            val isTransient = statusCode in 500..599 || statusCode == 429 || statusCode == 408
            val errorStream = connection.errorStream?.bufferedReader()?.use { it.readText() }
            return@withContext RemoteSnapshotResult.Failure(
                statusCode = statusCode,
                message = errorStream ?: "HTTP error $statusCode",
                isTransient = isTransient,
            )
        } catch (e: Exception) {
            return@withContext RemoteSnapshotResult.Failure(
                statusCode = null,
                message = e.message ?: "Connection failure",
                isTransient = true, // Network exceptions (timeout, connect error) are transient
            )
        } finally {
            connection?.disconnect()
        }
    }

    companion object {
        @Volatile
        var defaultBaseUrl: String = "http://10.0.2.2:3000"

        fun setBaseUrl(url: String) {
            defaultBaseUrl = url.trimEnd('/')
        }
    }
}
