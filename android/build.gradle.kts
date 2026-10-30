buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        // AGP 9 supplies built-in Kotlin support; this pins its KGP runtime to the SEM-11 baseline.
        classpath(libs.kotlin.gradlePlugin)
    }
}

plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.compose.compiler) apply false
}
