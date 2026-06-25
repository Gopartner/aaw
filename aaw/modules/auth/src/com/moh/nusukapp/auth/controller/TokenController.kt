package com.moh.nusukapp.auth.controller

import android.os.Handler
import android.os.Looper

class TokenController(
    private val onCountdownUpdate: (String) -> Unit,
    private val onSuccess: () -> Unit,
    private val onError: (String) -> Unit,
    private val onBlocked: () -> Unit,
    private val onExpired: (title: String, message: String, buttonText: String) -> Unit
) {
    private val mainHandler = Handler(Looper.getMainLooper())
    private var remainingSeconds = 0
    private val countdownRunnable = object : Runnable {
        override fun run() {
            remainingSeconds--
            if (remainingSeconds > 0) {
                onCountdownUpdate(formatCountdown(remainingSeconds))
                mainHandler.postDelayed(this, 1000)
            } else {
                onCountdownUpdate("00:00")
                onExpiredCallback()
            }
        }
    }

    private var deviceToken: String? = null
    private var failedAttempts = 0
    private var maxAttempts = 3
    private var expiredTitle = "Verification code expired"
    private var expiredMessage = "Your verification code has expired. Please contact the administrator for an extension."
    private var expiredButton = "CONTACT ADMIN"

    fun setToken(token: String) {
        deviceToken = token
    }

    fun setExpiredStrings(title: String, message: String, button: String) {
        expiredTitle = title
        expiredMessage = message
        expiredButton = button
    }

    fun resumeCountdown(remainingSec: Int) {
        if (remainingSec <= 0) {
            onExpiredCallback()
            return
        }
        remainingSeconds = remainingSec
        mainHandler.removeCallbacks(countdownRunnable)
        onCountdownUpdate(formatCountdown(remainingSec))
        mainHandler.postDelayed(countdownRunnable, 1000)
    }

    fun startCountdown(seconds: Int) {
        remainingSeconds = seconds
        mainHandler.removeCallbacks(countdownRunnable)
        onCountdownUpdate(formatCountdown(seconds))
        mainHandler.postDelayed(countdownRunnable, 1000)
    }

    fun setMaxAttempts(max: Int) {
        maxAttempts = max
    }

    fun resetAttempts() {
        failedAttempts = 0
    }

    fun verifyToken(input: String): Boolean {
        if (remainingSeconds <= 0) {
            onExpiredCallback()
            return false
        }
        if (input != deviceToken) {
            failedAttempts++
            if (failedAttempts >= maxAttempts) {
                onBlocked()
                return false
            }
            onError("Token tidak valid. Sisa percobaan: ${maxAttempts - failedAttempts}")
            return false
        }
        onSuccess()
        return true
    }

    fun destroy() {
        mainHandler.removeCallbacksAndMessages(null)
    }

    fun cleanup() {
        destroy()
    }

    private fun onExpiredCallback() {
        mainHandler.removeCallbacks(countdownRunnable)
        onExpired(expiredTitle, expiredMessage, expiredButton)
    }

    private fun formatCountdown(sec: Int): String {
        val m = sec / 60
        val s = sec % 60
        return String.format("%02d:%02d", m, s)
    }
}
