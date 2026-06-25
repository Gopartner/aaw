package com.moh.nusukapp.auth.model

data class OtpConfig(
    val digit: Int = 6,
    val expired_second: Int = 120,
    val max_attempt: Int = 3,
    val resend_enabled: Boolean = true
)
