package com.moh.nusukapp.auth.ui

import android.animation.ObjectAnimator
import android.content.Context
import android.graphics.Color
import android.graphics.Typeface
import android.view.Gravity
import android.view.MotionEvent
import android.view.animation.DecelerateInterpolator
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ProgressBar

class VerifyButton(context: Context) : LinearLayout(context) {

    val button: Button
    private val spinner: ProgressBar
    private var label = "Verify"
    var onClick: (() -> Unit)? = null
    private var isEnabled = false

    init {
        orientation = VERTICAL
        gravity = Gravity.CENTER

        val density = context.resources.displayMetrics.density

        button = Button(context).apply {
            text = label
            textSize = 16f
            setTypeface(null, Typeface.BOLD)
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            layoutParams = LayoutParams(LayoutParams.MATCH_PARENT, (50 * density).toInt())
            setPadding(0, 0, 0, 0)
            setBackgroundColor(Color.parseColor("#A9A9A9"))
            isEnabled = false
            setOnClickListener { onClick?.invoke() }

            setOnTouchListener { _, event ->
                when (event.action) {
                    MotionEvent.ACTION_DOWN -> {
                        if (isEnabled) {
                            animate().scaleX(0.97f).scaleY(0.97f)
                                .setDuration(80)
                                .start()
                        }
                        false
                    }
                    MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                        if (isEnabled) {
                            animate().scaleX(1.0f).scaleY(1.0f)
                                .setDuration(80)
                                .start()
                        }
                        false
                    }
                    else -> false
                }
            }
        }
        addView(button)

        spinner = ProgressBar(context).apply {
            layoutParams = LayoutParams((22 * density).toInt(), (22 * density).toInt())
            visibility = GONE
        }
        addView(spinner)
    }

    fun setButtonEnabled(enabled: Boolean) {
        isEnabled = enabled
        button.isEnabled = enabled
        if (enabled) {
            button.setBackgroundColor(Color.parseColor("#111111"))
        } else {
            button.setBackgroundColor(Color.parseColor("#A9A9A9"))
        }
    }

    fun setLoading(loading: Boolean) {
        if (loading) {
            button.text = ""
            button.isEnabled = false
            spinner.visibility = VISIBLE
        } else {
            spinner.visibility = GONE
            button.text = label
            setButtonEnabled(true)
        }
    }

    fun setText(text: String) {
        label = text
        button.text = text
    }
}
