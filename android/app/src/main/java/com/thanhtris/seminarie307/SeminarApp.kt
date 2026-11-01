package com.thanhtris.seminarie307

import android.app.Application
import android.util.Log
import com.google.firebase.FirebaseApp
import com.google.firebase.messaging.FirebaseMessaging
import com.thanhtris.seminarie307.config.AppContainer
import com.thanhtris.seminarie307.data.local.AppDatabase
import com.thanhtris.seminarie307.data.local.SyncMetadataEntity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class SeminarApp : Application() {
    override fun onCreate() {
        super.onCreate()
        AppContainer.init(this)

        // Initialize Firebase safely
        try {
            if (FirebaseApp.getApps(this).isEmpty()) {
                FirebaseApp.initializeApp(this)
            }
            fetchAndLogFcmToken()
        } catch (e: Exception) {
            Log.w("SeminarApp", "Firebase auto-initialization waiting for configuration: ${e.message}")
        }
    }

    @Suppress("DEPRECATION")
    private fun fetchAndLogFcmToken() {
        try {
            FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
                if (task.isSuccessful) {
                    val token = task.result
                    Log.i("FCM_TOKEN", "==================================================")
                    Log.i("FCM_TOKEN", "Device Registration Token: $token")
                    Log.i("FCM_TOKEN", "==================================================")
                    CoroutineScope(Dispatchers.IO).launch {
                        AppDatabase.getInstance(this@SeminarApp).metadataDao()
                            .setValue(SyncMetadataEntity("fcmToken", token))
                    }
                } else {
                    Log.w("FCM_TOKEN", "Fetching FCM registration token failed: ${task.exception?.message}")
                }
            }
        } catch (e: Exception) {
            Log.w("FCM_TOKEN", "Could not fetch FCM token: ${e.message}")
        }
    }
}
