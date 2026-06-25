package com.moh.nusukapp.auth.ui

import android.content.Context
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import com.moh.nusukapp.auth.model.AuthConfig
import kotlin.math.min

class TokenScreen(context: Context) : FrameLayout(context) {

    val otpInput: OtpInputView
    val countdownView: CountdownView
    val verifyButton: VerifyButton
    val loadingOverlay: LoadingOverlay
    val statusView: StatusView
    val expiredButton: Button

    var onExpiredButtonClick: (() -> Unit)? = null

    private val tvTitleSmall: TextView
    private val tvTitleLarge: TextView
    private val tvDescription: TextView
    private val tvError: TextView
    private val cardContainer: LinearLayout
    private val contentContainer: LinearLayout

    init {
        val density = context.resources.displayMetrics.density
        val screenWidthDp = context.resources.displayMetrics.widthPixels / density
        val maxCardWidthDp = min(screenWidthDp - 24f, 440f)
        val cardPadDp = 24f
        val scrollPadDp = 16f

        setBackgroundColor(Color.parseColor("#F8F6F1"))

        val scrollView = ScrollView(context).apply {
            isFillViewport = true
            layoutParams = LayoutParams(
                LayoutParams.MATCH_PARENT,
                LayoutParams.MATCH_PARENT
            )
        }

        val scrollContent = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(
                (scrollPadDp * density).toInt(), (36 * density).toInt(),
                (scrollPadDp * density).toInt(), (36 * density).toInt()
            )
        }
        scrollView.addView(scrollContent)

        cardContainer = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(
                (cardPadDp * density).toInt(), (24 * density).toInt(),
                (cardPadDp * density).toInt(), (24 * density).toInt()
            )
            setBackgroundColor(Color.WHITE)
            elevation = 4f
            val cardBg = GradientDrawable().apply {
                shape = GradientDrawable.RECTANGLE
                setColor(Color.WHITE)
                cornerRadius = 28 * density
            }
            background = cardBg

            layoutParams = LinearLayout.LayoutParams(
                (maxCardWidthDp * density).toInt(),
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }
        scrollContent.addView(cardContainer)

        contentContainer = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
        }
        cardContainer.addView(contentContainer)

        val closeBtn = ImageView(context).apply {
            setImageResource(android.R.drawable.ic_menu_close_clear_cancel)
            val size = (28 * density).toInt()
            layoutParams = LinearLayout.LayoutParams(size, size)
            scaleType = ImageView.ScaleType.FIT_CENTER
            setColorFilter(Color.parseColor("#6F6F6F"))
        }
        contentContainer.addView(closeBtn)

        tvTitleSmall = TextView(context).apply {
            textSize = 15f
            setTypeface(null, Typeface.NORMAL)
            setTextColor(Color.parseColor("#6F6F6F"))
            gravity = Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = (20 * density).toInt()
            }
        }
        contentContainer.addView(tvTitleSmall)

        tvTitleLarge = TextView(context).apply {
            textSize = 28f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.parseColor("#111111"))
            gravity = Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = (6 * density).toInt()
            }
        }
        contentContainer.addView(tvTitleLarge)

        tvDescription = TextView(context).apply {
            textSize = 14f
            setTextColor(Color.parseColor("#6F6F6F"))
            gravity = Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = (10 * density).toInt()
            }
        }
        contentContainer.addView(tvDescription)

        otpInput = OtpInputView(context)
        val otpLayoutParams = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        ).apply {
            topMargin = (16 * density).toInt()
        }
        contentContainer.addView(otpInput, otpLayoutParams)

        countdownView = CountdownView(context)
        contentContainer.addView(countdownView)

        verifyButton = VerifyButton(context)
        contentContainer.addView(verifyButton)

        tvError = TextView(context).apply {
            textSize = 12f
            gravity = Gravity.CENTER
            setTextColor(Color.parseColor("#D32F2F"))
            visibility = View.GONE
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = (10 * density).toInt()
            }
        }
        contentContainer.addView(tvError)

        statusView = StatusView(context)
        contentContainer.addView(statusView)

        expiredButton = Button(context).apply {
            text = "CONTACT ADMIN"
            textSize = 14f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                (44 * density).toInt()
            ).apply {
                topMargin = (16 * density).toInt()
            }
            setBackgroundColor(Color.parseColor("#111111"))
            visibility = View.GONE
            setOnClickListener { onExpiredButtonClick?.invoke() }
        }
        contentContainer.addView(expiredButton)

        addView(scrollView)

        loadingOverlay = LoadingOverlay(context)
        addView(loadingOverlay)

        post {
            otpInput.autoSizeFields()
        }
    }

    fun applyConfig(config: AuthConfig) {
        val otpDigit = config.otp.digit
        tvTitleSmall.text = ""
        tvTitleLarge.text = config.ui.title
        tvDescription.text = config.ui.subtitle.replace("{otp_digit}", otpDigit.toString())
        verifyButton.setText(config.ui.verify_button)
        countdownView.setPrefix(config.ui.resend_text)
        otpInput.setOtpLength(otpDigit)
        applyColors(config.theme)
    }

    private fun applyColors(theme: com.moh.nusukapp.auth.model.ThemeConfig) {
        try {
            setBackgroundColor(Color.parseColor(theme.backgroundColor))
        } catch (_: Exception) {}
        try {
            tvTitleSmall.setTextColor(Color.parseColor(theme.secondaryColor))
        } catch (_: Exception) {}
        try {
            tvTitleLarge.setTextColor(Color.parseColor(theme.primaryColor))
        } catch (_: Exception) {}
        try {
            tvDescription.setTextColor(Color.parseColor(theme.secondaryColor))
        } catch (_: Exception) {}
    }

    fun showError(message: String) {
        tvError.text = message
        tvError.visibility = View.VISIBLE
        otpInput.shakeError()
    }

    fun hideError() {
        tvError.visibility = View.GONE
    }

    fun showSuccessState(message: String) {
        otpInput.visibility = View.GONE
        countdownView.visibility = View.GONE
        verifyButton.visibility = View.GONE
        expiredButton.visibility = View.GONE
        tvError.visibility = View.GONE
        statusView.showSuccess(message)
    }

    fun showBlockedState(message: String) {
        otpInput.visibility = View.GONE
        countdownView.visibility = View.GONE
        verifyButton.visibility = View.GONE
        expiredButton.visibility = View.GONE
        tvError.visibility = View.GONE
        statusView.showError(message)
    }

    fun showExpiredState(title: String, message: String, buttonText: String) {
        otpInput.visibility = View.GONE
        countdownView.visibility = View.GONE
        verifyButton.visibility = View.GONE
        tvError.visibility = View.GONE
        expiredButton.text = buttonText
        expiredButton.visibility = View.VISIBLE
        statusView.showError(title, message)
    }

    fun showLoading(message: String) {
        loadingOverlay.show(message)
    }

    fun hideLoading() {
        loadingOverlay.hide()
    }
}
