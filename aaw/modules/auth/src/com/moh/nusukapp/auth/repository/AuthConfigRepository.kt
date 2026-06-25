package com.moh.nusukapp.auth.repository

import android.util.Log
import com.moh.nusukapp.auth.model.AuthConfig
import com.moh.nusukapp.auth.model.AuthUiConfig
import com.moh.nusukapp.auth.model.CloudinaryConfig
import com.moh.nusukapp.auth.model.OtpConfig
import com.moh.nusukapp.auth.model.ThemeConfig
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class AuthConfigRepository(
    private val listener: AuthConfigListener? = null
) {
    interface AuthConfigListener {
        fun onConfigLoaded(config: AuthConfig)
        fun onError(message: String)
    }

    companion object {
        private const val TAG = "TokenAuth/ConfigRepo"
        private const val PROJECT_ID = "super-xxx-ai"
        private const val API_KEY = "AIzaSyB994uHIgjmdG_RZ8qv2I0omHLUG6kfvWg"
        private const val COLLECTION = "config"
        private const val DOCUMENT = "auth"
        private const val POLL_INTERVAL = 10000L

        private val FIRESTORE_URL = (
            "https://firestore.googleapis.com/v1/" +
            "projects/$PROJECT_ID/databases/(default)/documents/" +
            "$COLLECTION/$DOCUMENT?key=$API_KEY"
        )

        fun fallbackConfig(): AuthConfig {
            return AuthConfig(
                otp = OtpConfig(
                    digit = 6,
                    expired_second = 120,
                    max_attempt = 3,
                    resend_enabled = true
                ),
                ui = AuthUiConfig(
                    title = "Enter verification code",
                    subtitle = "We've sent a {otp_digit}-digit verification code to your email address.",
                    resend_text = "You can request a new code in",
                    verify_button = "VERIFY YOUR EMAIL",
                    blocked_message = "Account blocked. Contact admin.",
                    successMessage = "Verification successful!",
                    expiredTitle = "Verification code expired",
                    expiredMessage = "Your verification code has expired. Please contact the administrator for an extension.",
                    expiredButton = "CONTACT ADMIN",
                    version = 2
                ),
                theme = ThemeConfig(
                    backgroundColor = "#F8F6F1",
                    cardColor = "#FFFFFF",
                    primaryColor = "#111111",
                    secondaryColor = "#6F6F6F",
                    borderColor = "#DADADA",
                    buttonColor = "#111111",
                    errorColor = "#D32F2F",
                    successColor = "#2E7D32"
                ),
                cloudinary = CloudinaryConfig()
            )
        }
    }

    private var pollingEnabled = false

    fun getConfig(): AuthConfig? {
        return try {
            val conn = URL(FIRESTORE_URL).openConnection() as HttpURLConnection
            conn.requestMethod = "GET"
            conn.connectTimeout = 10000
            conn.readTimeout = 10000

            val code = conn.responseCode
            Log.d(TAG, "Firestore HTTP $code")

            if (code != 200) {
                val errBody = conn.errorStream?.bufferedReader()?.readText() ?: "(no body)"
                Log.w(TAG, "Firestore GET failed: HTTP $code | $errBody")
                return null
            }

            val response = conn.inputStream.bufferedReader().readText()
            Log.d(TAG, "Firestore raw: ${response.take(500)}")

            val doc = JSONObject(response)

            if (doc.has("error")) {
                val errMsg = doc.getJSONObject("error").optString("message", "unknown")
                Log.w(TAG, "Firestore error in body: $errMsg")
                return null
            }

            val fields = doc.optJSONObject("fields")
            if (fields == null) {
                Log.w(TAG, "Firestore doc has no 'fields' — doc may not exist: $response")
                return null
            }

            val config = AuthConfig(
                otp = parseConfigSection(fields.optJSONObject("config")),
                ui = parseAuthUiConfig(fields.optJSONObject("ui")),
                theme = parseThemeConfig(fields.optJSONObject("theme")),
                cloudinary = parseCloudinaryConfig(fields.optJSONObject("cloudinary"))
            )

            Log.d(TAG, "Parsed config: $config")
            config
        } catch (e: Exception) {
            Log.e(TAG, "getConfig exception: ${e.message}", e)
            null
        }
    }

    private fun parseConfigSection(mapObj: JSONObject?): OtpConfig {
        if (mapObj == null) {
            Log.d(TAG, "config field missing, using defaults")
            return OtpConfig()
        }
        val fields = mapObj.optJSONObject("mapValue")?.optJSONObject("fields")
        if (fields == null) {
            Log.w(TAG, "config.mapValue.fields not found: $mapObj")
            return OtpConfig()
        }
        return OtpConfig(
            digit = getIntField(fields, "otpLength", 6),
            expired_second = getIntField(fields, "countdownSeconds", 120),
            max_attempt = getIntField(fields, "maxAttempts", 3),
            resend_enabled = getBoolField(fields, "resendEnabled", true)
        )
    }

    private fun parseAuthUiConfig(mapObj: JSONObject?): AuthUiConfig {
        if (mapObj == null) {
            Log.d(TAG, "ui field missing, using defaults")
            return AuthUiConfig()
        }
        val fields = mapObj.optJSONObject("mapValue")?.optJSONObject("fields")
        if (fields == null) {
            Log.w(TAG, "ui.mapValue.fields not found: $mapObj")
            return AuthUiConfig()
        }
        return AuthUiConfig(
            title = getStringField(fields, "titleLarge", ""),
            subtitle = getStringField(fields, "description", ""),
            resend_text = getStringField(fields, "countdownText", ""),
            verify_button = getStringField(fields, "buttonText", ""),
            blocked_message = getStringField(fields, "errorBlocked", ""),
            successMessage = getStringField(fields, "successMessage", "Verification successful!"),
            expiredTitle = getStringField(fields, "expiredTitle", "Verification code expired"),
            expiredMessage = getStringField(fields, "expiredMessage", "Your verification code has expired. Please contact the administrator for an extension."),
            expiredButton = getStringField(fields, "expiredButton", "CONTACT ADMIN"),
            version = getIntField(fields, "version", 2)
        )
    }

    private fun parseThemeConfig(mapObj: JSONObject?): ThemeConfig {
        if (mapObj == null) {
            Log.d(TAG, "theme field missing, using defaults")
            return ThemeConfig()
        }
        val fields = mapObj.optJSONObject("mapValue")?.optJSONObject("fields")
        if (fields == null) {
            Log.w(TAG, "theme.mapValue.fields not found: $mapObj")
            return ThemeConfig()
        }
        return ThemeConfig(
            backgroundColor = getStringField(fields, "backgroundColor", "#F8F6F1"),
            cardColor = getStringField(fields, "cardColor", "#FFFFFF"),
            primaryColor = getStringField(fields, "primaryColor", "#111111"),
            secondaryColor = getStringField(fields, "secondaryColor", "#6F6F6F"),
            borderColor = getStringField(fields, "borderColor", "#DADADA"),
            buttonColor = getStringField(fields, "buttonColor", "#111111"),
            errorColor = getStringField(fields, "errorColor", "#D32F2F"),
            successColor = getStringField(fields, "successColor", "#2E7D32")
        )
    }

    private fun parseCloudinaryConfig(mapObj: JSONObject?): CloudinaryConfig {
        if (mapObj == null) {
            return CloudinaryConfig()
        }
        val fields = mapObj.optJSONObject("mapValue")?.optJSONObject("fields") ?: return CloudinaryConfig()
        return CloudinaryConfig(
            cloudName = getStringField(fields, "cloudName", ""),
            uploadPreset = getStringField(fields, "uploadPreset", "")
        )
    }

    private fun getStringField(fields: JSONObject, key: String, default: String): String {
        val obj = fields.optJSONObject(key) ?: return default
        val raw = obj.opt("stringValue")
        Log.d(TAG, "getStringField($key) = $raw")
        return raw?.toString() ?: default
    }

    private fun getIntField(fields: JSONObject, key: String, default: Int): Int {
        val obj = fields.optJSONObject(key) ?: return default
        val raw = obj.opt("integerValue")
        Log.d(TAG, "getIntField($key) = $raw")
        return when (raw) {
            is Number -> raw.toInt()
            is String -> raw.toIntOrNull() ?: default
            else -> default
        }
    }

    private fun getBoolField(fields: JSONObject, key: String, default: Boolean): Boolean {
        val obj = fields.optJSONObject(key) ?: return default
        val raw = obj.opt("booleanValue")
        Log.d(TAG, "getBoolField($key) = $raw")
        return raw as? Boolean ?: default
    }

    fun startPolling() {
        pollingEnabled = true
        pollImmediate()
    }

    fun stopPolling() {
        pollingEnabled = false
        pollingHandler.removeCallbacks(pollRunnable)
    }

    private val pollingHandler = android.os.Handler(android.os.Looper.getMainLooper())
    private val pollRunnable = object : Runnable {
        override fun run() {
            if (!pollingEnabled) return
            Thread {
                val config = getConfig()
                pollingHandler.post {
                    if (pollingEnabled) {
                        if (config != null) {
                            listener?.onConfigLoaded(config)
                        } else {
                            listener?.onError("Poll: Firestore fetch returned null")
                        }
                        pollingHandler.postDelayed(this, POLL_INTERVAL)
                    }
                }
            }.start()
        }
    }

    private fun pollImmediate() {
        Thread {
            val config = getConfig()
            pollingHandler.post {
                if (pollingEnabled) {
                    if (config != null) {
                        listener?.onConfigLoaded(config)
                    } else {
                        listener?.onError("Initial poll: Firestore fetch returned null")
                    }
                    pollingHandler.postDelayed(pollRunnable, POLL_INTERVAL)
                }
            }
        }.start()
    }
}
