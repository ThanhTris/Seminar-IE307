package com.thanhtris.seminarie307.config

import android.content.Context
import com.thanhtris.seminarie307.integration.BulletinUiGateway
import com.thanhtris.seminarie307.integration.EmptyBulletinUiGateway
import com.thanhtris.seminarie307.integration.RealBulletinUiGateway

object AppContainer {
    @Volatile
    private var gatewayInstance: BulletinUiGateway? = null

    fun init(context: Context) {
        if (gatewayInstance == null) {
            synchronized(this) {
                if (gatewayInstance == null) {
                    gatewayInstance = RealBulletinUiGateway(context.applicationContext)
                }
            }
        }
    }

    val bulletinUiGateway: BulletinUiGateway
        get() = gatewayInstance ?: EmptyBulletinUiGateway()
}
