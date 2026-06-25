package com.moh.nusukapp.auth.model

data class AuthConfig(
    val otp: OtpConfig = OtpConfig(),
    val ui: AuthUiConfig = AuthUiConfig(),
    val theme: ThemeConfig = ThemeConfig(),
    val cloudinary: CloudinaryConfig = CloudinaryConfig()
)
