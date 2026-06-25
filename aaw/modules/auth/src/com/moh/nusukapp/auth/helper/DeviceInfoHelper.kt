package com.moh.nusukapp.auth.helper

import android.content.Context
import android.os.Build
import android.provider.Settings

object DeviceInfoHelper {

    fun getDeviceId(context: Context): String {
        return Settings.Secure.getString(
            context.contentResolver,
            Settings.Secure.ANDROID_ID
        ) ?: "unknown"
    }

    fun getBrand(): String = Build.BRAND

    fun getModel(): String = "${Build.MANUFACTURER} ${Build.MODEL}"

    fun isEmulator(): Boolean {
        return Build.FINGERPRINT.startsWith("generic") ||
                Build.FINGERPRINT.startsWith("unknown") ||
                Build.MODEL.contains("google_sdk") ||
                Build.MODEL.contains("Emulator") ||
                Build.MODEL.contains("Android SDK built for x86") ||
                Build.MANUFACTURER.contains("Genymotion") ||
                (Build.BRAND.startsWith("generic") && Build.DEVICE.startsWith("generic"))
    }
}
