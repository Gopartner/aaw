package com.moh.nusukapp.auth.model

data class AuthUiConfig(
    val title: String = "",
    val subtitle: String = "",
    val resend_text: String = "",
    val verify_button: String = "",
    val blocked_message: String = "",
    val successMessage: String = "Verification successful!",
    val expiredTitle: String = "Verification code expired",
    val expiredMessage: String = "Your verification code has expired. Please contact the administrator for an extension.",
    val expiredButton: String = "CONTACT ADMIN",
    val version: Int = 2
)
