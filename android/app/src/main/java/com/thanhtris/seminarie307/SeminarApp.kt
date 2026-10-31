package com.thanhtris.seminarie307

import android.app.Application
import com.thanhtris.seminarie307.config.AppContainer

class SeminarApp : Application() {
    override fun onCreate() {
        super.onCreate()
        AppContainer.init(this)
    }
}
