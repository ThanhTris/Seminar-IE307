package com.thanhtris.seminarie307.data.remote

import com.thanhtris.seminarie307.integration.BulletinItem
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.IOException
import java.net.HttpURLConnection
import java.net.MalformedURLException
import java.net.URL
import java.time.Instant

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

/** GET client for the pinned v2 snapshot contract. Error details are never copied into logs. */
class SnapshotRemoteDataSource(
    customBaseUrl: String? = null,
) {
    val baseUrl: String = (customBaseUrl ?: defaultBaseUrl).trimEnd('/')

    suspend fun fetchSnapshot(
        currentVersion: Long? = null,
        requestId: String? = null,
    ): RemoteSnapshotResult = withContext(Dispatchers.IO) {
        if (currentVersion != null && currentVersion !in 0..MAX_SAFE_JSON_INTEGER) {
            return@withContext permanentFailure("INVALID_RESPONSE")
        }
        if (requestId != null && !APP_ID.matches(requestId)) {
            return@withContext permanentFailure("INVALID_RESPONSE")
        }

        var connection: HttpURLConnection? = null
        try {
            val url = URL("$baseUrl/api/bulletin")
            connection = (url.openConnection() as HttpURLConnection).apply {
                requestMethod = "GET"
                connectTimeout = CONNECT_TIMEOUT_MS
                readTimeout = READ_TIMEOUT_MS
                instanceFollowRedirects = false
                setRequestProperty("Accept", "application/json")
                if (currentVersion != null) {
                    setRequestProperty("If-None-Match", "\"v$currentVersion\"")
                }
                if (requestId != null) {
                    setRequestProperty("X-Correlation-Request-Id", requestId)
                }
            }

            val statusCode = connection.responseCode
            val responseApiVersion = connection.getHeaderField("X-API-Version")
            if (!supportedApiVersion(responseApiVersion)) {
                return@withContext RemoteSnapshotResult.Failure(
                    statusCode = statusCode,
                    message = "INVALID_RESPONSE",
                    isTransient = false,
                )
            }

            if (statusCode == HttpURLConnection.HTTP_NOT_MODIFIED) {
                val expectedEtag = currentVersion?.let { "\"v$it\"" }
                if (expectedEtag == null || connection.getHeaderField("ETag") != expectedEtag) {
                    return@withContext permanentFailure("INVALID_RESPONSE", statusCode)
                }
                return@withContext RemoteSnapshotResult.NotModified
            }

            if (statusCode == HttpURLConnection.HTTP_OK) {
                val contentType = connection.getHeaderField("Content-Type")
                    ?.substringBefore(';')
                    ?.trim()
                    ?.lowercase()
                if (contentType != "application/json") {
                    return@withContext permanentFailure("INVALID_RESPONSE", statusCode)
                }
                val responseText = connection.inputStream.bufferedReader(Charsets.UTF_8).use { it.readText() }
                val snapshot = parseSnapshot(responseText, responseApiVersion)
                    ?: return@withContext permanentFailure("INVALID_RESPONSE", statusCode)
                val expectedEtag = "\"v${snapshot.version}\""
                if (connection.getHeaderField("ETag") != expectedEtag) {
                    return@withContext permanentFailure("INVALID_RESPONSE", statusCode)
                }
                return@withContext RemoteSnapshotResult.Success(
                    version = snapshot.version,
                    lastModifiedUtc = snapshot.lastModifiedUtc,
                    items = snapshot.items,
                )
            }

            val transient = statusCode in 500..599 || statusCode == 429 || statusCode == 408
            return@withContext RemoteSnapshotResult.Failure(
                statusCode = statusCode,
                message = "HTTP_ERROR",
                isTransient = transient,
            )
        } catch (_: MalformedURLException) {
            return@withContext permanentFailure("UNEXPECTED_ERROR")
        } catch (_: IOException) {
            return@withContext RemoteSnapshotResult.Failure(
                statusCode = null,
                message = "NETWORK_ERROR",
                isTransient = true,
            )
        } catch (_: Exception) {
            return@withContext permanentFailure("INVALID_RESPONSE")
        } finally {
            connection?.disconnect()
        }
    }

    private fun parseSnapshot(body: String, apiVersionHeader: String): Snapshot? = try {
        val json = JSONObject(body)
        if (json.keys().asSequence().toSet() != setOf("api_version", "version", "last_modified_utc", "items")) return null
        if (json.getString("api_version") != apiVersionHeader) return null

        val rawVersion = json.get("version")
        val version = rawVersion.asJsonInteger() ?: return null
        if (version !in 0..MAX_SAFE_JSON_INTEGER) return null

        val lastModifiedUtc = json.getString("last_modified_utc")
        if (!lastModifiedUtc.endsWith("Z")) return null
        Instant.parse(lastModifiedUtc)

        val rawItems = json.getJSONArray("items")
        if (rawItems.length() > MAX_ITEMS) return null
        if (version == 0L && rawItems.length() != 0) return null

        val ids = mutableSetOf<String>()
        val versions = mutableSetOf<Long>()
        val items = ArrayList<BulletinItem>(rawItems.length())
        var previousVersion = Long.MAX_VALUE
        for (index in 0 until rawItems.length()) {
            val item = rawItems.getJSONObject(index)
            if (item.keys().asSequence().toSet() != setOf("id", "title", "body", "version")) return null
            val id = item.getString("id")
            val title = item.getString("title")
            val text = item.getString("body")
            val itemVersion = item.get("version").asJsonInteger() ?: return null
            if (!APP_ID.matches(id) || !ids.add(id)) return null
            if (title.isBlank() || title.codePointCount(0, title.length) > MAX_TITLE_CODE_POINTS) return null
            if (text.codePointCount(0, text.length) > MAX_BODY_CODE_POINTS) return null
            if (itemVersion !in 1..version || !versions.add(itemVersion) || itemVersion >= previousVersion) return null
            previousVersion = itemVersion
            items += BulletinItem(id = id, title = title, body = text, version = itemVersion)
        }
        if (version > 0 && items.firstOrNull()?.version != version) return null
        Snapshot(version = version, lastModifiedUtc = lastModifiedUtc, items = items)
    } catch (_: Exception) {
        null
    }

    private fun Any?.asJsonInteger(): Long? = when (this) {
        is Int -> toLong()
        is Long -> this
        else -> null // Reject floating point numbers and numeric strings.
    }

    private fun supportedApiVersion(value: String?): Boolean {
        if (value == null || !SEMVER.matches(value)) return false
        return value.substringBefore('.').toIntOrNull() == SUPPORTED_API_MAJOR
    }

    private fun permanentFailure(code: String, statusCode: Int? = null) =
        RemoteSnapshotResult.Failure(statusCode = statusCode, message = code, isTransient = false)

    private data class Snapshot(
        val version: Long,
        val lastModifiedUtc: String,
        val items: List<BulletinItem>,
    )

    companion object {
        private const val SUPPORTED_API_MAJOR = 2
        private const val CONNECT_TIMEOUT_MS = 5_000
        private const val READ_TIMEOUT_MS = 5_000
        private const val MAX_ITEMS = 100
        private const val MAX_TITLE_CODE_POINTS = 256
        private const val MAX_BODY_CODE_POINTS = 4_096
        private const val MAX_SAFE_JSON_INTEGER = 9_007_199_254_740_991L
        private val APP_ID = Regex("^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
        private val SEMVER = Regex("^\\d+\\.\\d+\\.\\d+$")

        @Volatile
        var defaultBaseUrl: String = "http://10.0.2.2:3000"

        fun setBaseUrl(url: String) {
            defaultBaseUrl = url.trimEnd('/')
        }
    }
}
