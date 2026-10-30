package com.thanhtris.seminarie307.config

import com.thanhtris.seminarie307.integration.BulletinUiGateway
import com.thanhtris.seminarie307.integration.EmptyBulletinUiGateway

object AppContainer {
    // SEM-25/28 replace this binding with the adapter over the shared sync core.
    val bulletinUiGateway: BulletinUiGateway = EmptyBulletinUiGateway()
}
