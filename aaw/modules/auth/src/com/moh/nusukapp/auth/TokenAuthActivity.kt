package com.moh.nusukapp.auth

import android.app.Activity
import android.os.Bundle

import com.moh.nusukapp.auth.controller.TokenController
import com.moh.nusukapp.auth.model.AuthConfig
import com.moh.nusukapp.auth.model.OtpConfig
import com.moh.nusukapp.auth.model.UiConfig
import com.moh.nusukapp.auth.model.ThemeConfig
import com.moh.nusukapp.auth.ui.TokenScreen

class TokenAuthActivity : Activity() {

    private lateinit var tokenScreen: TokenScreen
    private var tokenController: TokenController? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        tokenScreen = TokenScreen(this)
        setContentView(tokenScreen)

        val sampleConfig = AuthConfig(
            otp = OtpConfig(digit = 6),
            ui = UiConfig(
                title = "Verification Code",
                subtitle = "Enter the {otp_digit}-digit code sent to your device",
                verify_button = "VERIFY",
                resend_text = "Resend in"
            ),
            theme = ThemeConfig(
                primaryColor = "#111111",
                secondaryColor = "#6F6F6F",
                backgroundColor = "#F8F6F1"
            )
        )

        tokenScreen.applyConfig(sampleConfig)

        tokenController = TokenController(
            onCountdownUpdate = { time -> tokenScreen.countdownView.setTime(time) },
            onSuccess = {
                tokenScreen.otpInput.visibility = android.view.View.GONE
                tokenScreen.showSuccessState("Verified!")
            },
            onError = { msg -> tokenScreen.showError(msg) },
            onBlocked = { tokenScreen.showBlockedState("Too many attempts") },
            onExpired = { title, msg, btn ->
                tokenScreen.showExpiredState(title, msg, btn)
            }
        )

        tokenController?.setToken("123456")
        tokenController?.startCountdown(120)

        tokenScreen.expiredButton.setOnClickListener {
            finish()
        }

        tokenScreen.verifyButton.setOnClickListener {
            val code = tokenScreen.otpInput.getOtp()
            if (code.length < 4) {
                tokenScreen.showError("Enter complete code")
                return@setOnClickListener
            }
            tokenScreen.showLoading("Verifying...")
            tokenController?.verifyToken(code)
            tokenScreen.hideLoading()
        }
    }

    override fun onDestroy() {
        tokenController?.destroy()
        super.onDestroy()
    }
}
