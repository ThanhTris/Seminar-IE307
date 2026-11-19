package com.thanhtris.seminarie307.config

/** Selects the host-loopback route used by the shared APK. */
object ServerEndpoint {
    const val EMULATOR_BASE_URL = "http://10.0.2.2:3000"
    const val DEVICE_BASE_URL = "http://127.0.0.1:3000"

    fun forRuntime(
        fingerprint: String,
        model: String,
        hardware: String,
        product: String,
    ): String {
        val emulator = fingerprint.startsWith("generic", ignoreCase = true) ||
            fingerprint.startsWith("unknown", ignoreCase = true) ||
            model.contains("emulator", ignoreCase = true) ||
            model.contains("google_sdk", ignoreCase = true) ||
            hardware.contains("goldfish", ignoreCase = true) ||
            hardware.contains("ranchu", ignoreCase = true) ||
            product.contains("sdk", ignoreCase = true) ||
            product.contains("emulator", ignoreCase = true)

        return if (emulator) EMULATOR_BASE_URL else DEVICE_BASE_URL
    }
}
