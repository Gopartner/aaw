package com.moh.nusukapp.auth.helper

import android.util.Log
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.util.Base64

object CloudinaryUploader {

    private const val TAG = "TokenAuth/Cloudinary"
    private const val UPLOAD_API_URL = "https://admin-nusukapp.vercel.app/api/upload"

    fun uploadImage(
        imageBytes: ByteArray,
        deviceId: String
    ): String? {
        return try {
            val base64 = Base64.getEncoder().encodeToString(imageBytes)
            val requestBody = JSONObject().apply {
                put("image", "data:image/jpeg;base64,$base64")
                put("deviceId", deviceId)
            }

            val url = URL(UPLOAD_API_URL)
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.doOutput = true
            conn.connectTimeout = 30000
            conn.readTimeout = 30000
            conn.setRequestProperty("Content-Type", "application/json")

            val writer = OutputStreamWriter(conn.outputStream, "UTF-8")
            writer.write(requestBody.toString())
            writer.flush()
            writer.close()

            val responseCode = conn.responseCode
            Log.d(TAG, "Upload response code: $responseCode")

            return if (responseCode in 200..299) {
                val response = conn.inputStream.bufferedReader().readText()
                val json = JSONObject(response)
                val result = json.optString("url")
                Log.d(TAG, "Upload success: $result")
                result
            } else {
                val error = conn.errorStream?.bufferedReader()?.readText() ?: "unknown"
                Log.e(TAG, "Upload failed ($responseCode): $error")
                null
            }
        } catch (e: Exception) {
            Log.e(TAG, "Upload exception: ${e.message}", e)
            null
        }
    }
}
