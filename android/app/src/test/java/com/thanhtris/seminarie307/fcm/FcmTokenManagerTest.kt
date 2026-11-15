package com.thanhtris.seminarie307.fcm

import com.thanhtris.seminarie307.data.local.SyncMetadataDao
import com.thanhtris.seminarie307.data.local.SyncMetadataEntity
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import java.time.Instant

class FcmTokenManagerTest {

    private lateinit var dao: FakeSyncMetadataDao
    private val exported = mutableListOf<String>()
    private var now = Instant.parse("2026-11-09T01:00:00Z")
    private lateinit var manager: FcmTokenManager

    @Before
    fun setUp() {
        dao = FakeSyncMetadataDao()
        exported.clear()
        manager = FcmTokenManager(
            metadataDao = dao,
            nowUtc = { now },
            exportToken = { exported.add(it) },
        )
    }

    @Test
    fun storesFirstTokenWithFingerprintAndStatus() = runBlocking {
        val result = manager.onTokenAvailable("token-A", FcmTokenSource.STARTUP)

        val stored = result as TokenUpdateResult.Stored
        assertTrue(stored.changed)
        assertEquals(FcmTokenManager.fingerprint("token-A"), stored.fingerprint)
        assertEquals("token-A", dao.map[FcmTokenKeys.TOKEN])
        assertEquals(stored.fingerprint, dao.map[FcmTokenKeys.FINGERPRINT])
        assertEquals("STARTUP", dao.map[FcmTokenKeys.SOURCE])
        assertEquals("READY", dao.map[FcmTokenKeys.STATUS])
        assertEquals("2026-11-09T01:00:00Z", dao.map[FcmTokenKeys.UPDATED_AT_UTC])
        assertNull(dao.map[FcmTokenKeys.REFRESH_COUNT])
        assertEquals(listOf("token-A"), exported)
    }

    @Test
    fun sameTokenIsNotCountedAsRefresh() = runBlocking {
        manager.onTokenAvailable("token-A", FcmTokenSource.STARTUP)
        now = Instant.parse("2026-11-09T02:00:00Z")

        val result = manager.onTokenAvailable("token-A", FcmTokenSource.ON_NEW_TOKEN) as TokenUpdateResult.Stored

        assertFalse(result.changed)
        assertEquals("2026-11-09T01:00:00Z", dao.map[FcmTokenKeys.UPDATED_AT_UTC])
        assertNull(dao.map[FcmTokenKeys.REFRESH_COUNT])
        assertEquals("ON_NEW_TOKEN", dao.map[FcmTokenKeys.SOURCE])
    }

    @Test
    fun changedTokenReplacesStoredTokenAndTracksRotation() = runBlocking {
        manager.onTokenAvailable("token-A", FcmTokenSource.STARTUP)
        now = Instant.parse("2026-11-09T03:00:00Z")

        val result = manager.onTokenAvailable("token-B", FcmTokenSource.ON_NEW_TOKEN) as TokenUpdateResult.Stored

        assertTrue(result.changed)
        assertEquals("token-B", dao.map[FcmTokenKeys.TOKEN])
        assertEquals(FcmTokenManager.fingerprint("token-B"), dao.map[FcmTokenKeys.FINGERPRINT])
        assertEquals(FcmTokenManager.fingerprint("token-A"), dao.map[FcmTokenKeys.PREVIOUS_FINGERPRINT])
        assertEquals("1", dao.map[FcmTokenKeys.REFRESH_COUNT])
        assertEquals("2026-11-09T03:00:00Z", dao.map[FcmTokenKeys.UPDATED_AT_UTC])
        assertEquals(listOf("token-A", "token-B"), exported)
    }

    @Test
    fun invalidTokensAreRejectedAndNeverStored() = runBlocking {
        for (bad in listOf(null, "", "has space", "tab\tinside", "x".repeat(8193))) {
            val result = manager.onTokenAvailable(bad, FcmTokenSource.ON_NEW_TOKEN)
            assertEquals(TokenUpdateResult.Rejected(FcmTokenStatus.INVALID_TOKEN), result)
        }
        assertNull(dao.map[FcmTokenKeys.TOKEN])
        assertEquals("INVALID_TOKEN", dao.map[FcmTokenKeys.STATUS])
        assertTrue(exported.isEmpty())
    }

    @Test
    fun missingFirebaseConfigRecordsStatusWithoutToken() = runBlocking {
        manager.onTokenUnavailable(FcmTokenStatus.FIREBASE_NOT_CONFIGURED)

        assertEquals("FIREBASE_NOT_CONFIGURED", dao.map[FcmTokenKeys.STATUS])
        assertNull(dao.map[FcmTokenKeys.TOKEN])
    }

    @Test
    fun fetchFailureKeepsOldTokenButMarksItNotReady() = runBlocking {
        manager.onTokenAvailable("token-A", FcmTokenSource.STARTUP)

        manager.onTokenUnavailable(FcmTokenStatus.FETCH_FAILED)

        assertEquals("token-A", dao.map[FcmTokenKeys.TOKEN])
        assertEquals("FETCH_FAILED", dao.map[FcmTokenKeys.STATUS])
    }

    @Test
    fun exportFailureDoesNotLoseStoredToken() = runBlocking {
        val failing = FcmTokenManager(dao, { now }, { error("disk full") })

        val result = failing.onTokenAvailable("token-A", FcmTokenSource.STARTUP)

        assertTrue(result is TokenUpdateResult.Stored)
        assertEquals("token-A", dao.map[FcmTokenKeys.TOKEN])
    }

    @Test
    fun fingerprintIsStableShortAndDoesNotContainToken() {
        val token = "dGVzdC10b2tlbi1zZWNyZXQ"
        val fp = FcmTokenManager.fingerprint(token)

        assertEquals(16, fp.length)
        assertTrue(fp.all { it in '0'..'9' || it in 'a'..'f' })
        assertEquals(fp, FcmTokenManager.fingerprint(token))
        assertNotEquals(fp, FcmTokenManager.fingerprint(token + "x"))
        assertFalse(fp.contains(token))
    }

    private class FakeSyncMetadataDao : SyncMetadataDao {
        val map = mutableMapOf<String, String?>()

        override fun observeValue(key: String): Flow<String?> = flowOf(map[key])

        override suspend fun getValue(key: String): String? = map[key]

        override suspend fun setValue(entry: SyncMetadataEntity) {
            map[entry.key] = entry.value
        }

        override suspend fun deleteValue(key: String) {
            map.remove(key)
        }
    }
}
