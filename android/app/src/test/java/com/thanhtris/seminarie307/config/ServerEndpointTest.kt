package com.thanhtris.seminarie307.config

import org.junit.Assert.assertEquals
import org.junit.Test

class ServerEndpointTest {
    @Test
    fun emulatorUsesHostGatewayAddress() {
        assertEquals(
            ServerEndpoint.EMULATOR_BASE_URL,
            ServerEndpoint.forRuntime(
                fingerprint = "google/sdk_gphone64_x86_64/generic",
                model = "sdk_gphone64_x86_64",
                hardware = "ranchu",
                product = "sdk_gphone64_x86_64",
            ),
        )
    }

    @Test
    fun physicalDeviceUsesLoopbackForAdbReverse() {
        assertEquals(
            ServerEndpoint.DEVICE_BASE_URL,
            ServerEndpoint.forRuntime(
                fingerprint = "OPPO/CPHxxxx/CPHxxxx:16/BUILD/123:user/release-keys",
                model = "OPPO Find X9",
                hardware = "qcom",
                product = "CPHxxxx",
            ),
        )
    }
}
