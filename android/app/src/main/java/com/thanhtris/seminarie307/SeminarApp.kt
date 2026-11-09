package com.thanhtris.seminarie307

import android.app.Application
import com.thanhtris.seminarie307.config.AppContainer
import com.thanhtris.seminarie307.fcm.FcmTokenManager

class SeminarApp : Application() {
    override fun onCreate() {
        super.onCreate()
        AppContainer.init(this)

        // SEM-33: obtain/store the registration token; records FIREBASE_NOT_CONFIGURED when no
        // google-services.json is present. The raw token is never written to Logcat.
        FcmTokenManager.refreshFromFirebase(this)
    }
}
