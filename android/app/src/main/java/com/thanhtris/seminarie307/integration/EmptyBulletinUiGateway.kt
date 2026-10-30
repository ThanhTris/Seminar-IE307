package com.thanhtris.seminarie307.integration

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flowOf

/** Safe scaffold binding until SEM-25/28 supplies the cache and enqueue adapter. */
class EmptyBulletinUiGateway : BulletinUiGateway {
    override val state: Flow<BulletinUiState> = flowOf(BulletinUiState())

    override suspend fun enqueueManual(context: ManualSyncContext): ManualEnqueueResult =
        ManualEnqueueResult.Rejected("Chưa có sync core được kết nối.")
}
