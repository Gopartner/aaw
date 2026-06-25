package com.moh.nusukapp.auth.repository

import android.util.Log
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class DeviceRepository {

    companion object {
        private const val TAG = "TokenAuth/DeviceRepo"
        private const val PROJECT_ID = "super-xxx-ai"
        private const val API_KEY = "AIzaSyB994uHIgjmdG_RZ8qv2I0omHLUG6kfvWg"
        private const val COLLECTION = "devices"

        private fun deviceUrl(deviceId: String): String {
            return (
                "https://firestore.googleapis.com/v1/" +
                "projects/$PROJECT_ID/databases/(default)/documents/" +
                "$COLLECTION/$deviceId?key=$API_KEY"
            )
        }
    }

    data class DeviceData(
        val deviceId: String = "",
        val token: String = "",
        val status: String = "pending",
        val createdAt: Long = 0,
        val expiredAt: Long = 0,
        val attemptCount: Int = 0,
        val verified: Boolean = false,
        val lastSeen: Long = 0
    )

    fun getDevice(deviceId: String): DeviceData? {
        return try {
            val conn = URL(deviceUrl(deviceId)).openConnection() as HttpURLConnection
            conn.requestMethod = "GET"
            conn.connectTimeout = 10000
            conn.readTimeout = 10000

            val code = conn.responseCode
            if (code == 404) return null
            if (code != 200) {
                Log.w(TAG, "getDevice HTTP $code")
                return null
            }

            val response = conn.inputStream.bufferedReader().readText()
            val doc = JSONObject(response)
            if (doc.has("error")) return null

            val fields = doc.optJSONObject("fields") ?: return null
            parseDeviceData(fields)
        } catch (e: Exception) {
            Log.e(TAG, "getDevice exception: ${e.message}", e)
            null
        }
    }

    fun createDevice(
        deviceId: String,
        token: String,
        expiredAt: Long,
        countdownSeconds: Int
    ): Boolean {
        return try {
            val now = System.currentTimeMillis()
            val fieldsJson = JSONObject().apply {
                put("deviceId", JSONObject().apply { put("stringValue", deviceId) })
                put("token", JSONObject().apply { put("stringValue", token) })
                put("status", JSONObject().apply { put("stringValue", "pending") })
                put("createdAt", JSONObject().apply { put("integerValue", now) })
                put("expiredAt", JSONObject().apply { put("integerValue", expiredAt) })
                put("attemptCount", JSONObject().apply { put("integerValue", 0) })
                put("verified", JSONObject().apply { put("booleanValue", false) })
                put("lastSeen", JSONObject().apply { put("integerValue", now) })
                put("countdownSeconds", JSONObject().apply { put("integerValue", countdownSeconds) })
            }
            val body = JSONObject().apply { put("fields", fieldsJson) }
            writeDevice(deviceId, body.toString(), "PATCH")
        } catch (e: Exception) {
            Log.e(TAG, "createDevice exception: ${e.message}", e)
            false
        }
    }

    fun updateLastSeen(deviceId: String): Boolean {
        return try {
            val now = System.currentTimeMillis()
            val fieldsJson = JSONObject().apply {
                put("lastSeen", JSONObject().apply { put("integerValue", now) })
            }
            val body = JSONObject().apply { put("fields", fieldsJson) }
            writeDevice(deviceId, body.toString(), "PATCH")
        } catch (e: Exception) {
            Log.e(TAG, "updateLastSeen exception: ${e.message}", e)
            false
        }
    }

    fun verifyDevice(deviceId: String): Boolean {
        return try {
            val fieldsJson = JSONObject().apply {
                put("status", JSONObject().apply { put("stringValue", "verified") })
                put("verified", JSONObject().apply { put("booleanValue", true) })
            }
            val body = JSONObject().apply { put("fields", fieldsJson) }
            writeDevice(deviceId, body.toString(), "PATCH")
        } catch (e: Exception) {
            Log.e(TAG, "verifyDevice exception: ${e.message}", e)
            false
        }
    }

    fun expireDevice(deviceId: String): Boolean {
        return try {
            val fieldsJson = JSONObject().apply {
                put("status", JSONObject().apply { put("stringValue", "expired") })
            }
            val body = JSONObject().apply { put("fields", fieldsJson) }
            writeDevice(deviceId, body.toString(), "PATCH")
        } catch (e: Exception) {
            Log.e(TAG, "expireDevice exception: ${e.message}", e)
            false
        }
    }

    fun blockDevice(deviceId: String): Boolean {
        return try {
            val fieldsJson = JSONObject().apply {
                put("status", JSONObject().apply { put("stringValue", "blocked") })
            }
            val body = JSONObject().apply { put("fields", fieldsJson) }
            writeDevice(deviceId, body.toString(), "PATCH")
        } catch (e: Exception) {
            Log.e(TAG, "blockDevice exception: ${e.message}", e)
            false
        }
    }

    fun incrementAttempt(deviceId: String): Boolean {
        return try {
            val existing = getDevice(deviceId)
            val count = (existing?.attemptCount ?: 0) + 1
            val fieldsJson = JSONObject().apply {
                put("attemptCount", JSONObject().apply { put("integerValue", count) })
            }
            val body = JSONObject().apply { put("fields", fieldsJson) }
            writeDevice(deviceId, body.toString(), "PATCH")
        } catch (e: Exception) {
            Log.e(TAG, "incrementAttempt exception: ${e.message}", e)
            false
        }
    }

    fun checkToken(deviceId: String): String? {
        val device = getDevice(deviceId) ?: return null
        return device.token
    }

    private fun writeDevice(deviceId: String, body: String, method: String): Boolean {
        return try {
            val url = URL(deviceUrl(deviceId))
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = method
            conn.doOutput = true
            conn.connectTimeout = 10000
            conn.readTimeout = 10000
            conn.setRequestProperty("Content-Type", "application/json")
            conn.outputStream.write(body.toByteArray())
            val code = conn.responseCode
            Log.d(TAG, "write $deviceId → HTTP $code")
            code in 200..299
        } catch (e: Exception) {
            Log.e(TAG, "write $deviceId failed: ${e.message}")
            false
        }
    }

    private fun parseDeviceData(fields: JSONObject): DeviceData {
        return DeviceData(
            deviceId = getStringField(fields, "deviceId"),
            token = getStringField(fields, "token"),
            status = getStringField(fields, "status", "pending"),
            createdAt = getLongField(fields, "createdAt"),
            expiredAt = getLongField(fields, "expiredAt"),
            attemptCount = getIntField(fields, "attemptCount"),
            verified = getBoolField(fields, "verified"),
            lastSeen = getLongField(fields, "lastSeen")
        )
    }

    private fun getStringField(fields: JSONObject, key: String, default: String = ""): String {
        val obj = fields.optJSONObject(key) ?: return default
        return obj.optString("stringValue", default)
    }

    private fun getIntField(fields: JSONObject, key: String, default: Int = 0): Int {
        val obj = fields.optJSONObject(key) ?: return default
        val raw = obj.opt("integerValue")
        return when (raw) {
            is Number -> raw.toInt()
            is String -> raw.toIntOrNull() ?: default
            else -> default
        }
    }

    private fun getLongField(fields: JSONObject, key: String, default: Long = 0L): Long {
        val obj = fields.optJSONObject(key) ?: return default
        val raw = obj.opt("integerValue")
        return when (raw) {
            is Number -> raw.toLong()
            is String -> raw.toLongOrNull() ?: default
            else -> default
        }
    }

    private fun getBoolField(fields: JSONObject, key: String, default: Boolean = false): Boolean {
        val obj = fields.optJSONObject(key) ?: return default
        return obj.optBoolean("booleanValue", default)
    }
}
