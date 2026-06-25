package com.moh.nusukapp.auth.ui

import android.content.Context
import android.graphics.Color
import android.view.Gravity
import android.view.View
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.TextView

class LoadingOverlay(context: Context) : FrameLayout(context) {

    private val tvMessage: TextView

    init {
        setBackgroundColor(Color.parseColor("#4D000000"))
        visibility = View.GONE

        val container = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            layoutParams = LayoutParams(
                LayoutParams.WRAP_CONTENT,
                LayoutParams.WRAP_CONTENT
            ).apply {
                gravity = Gravity.CENTER
            }
        }

        val spinner = ProgressBar(context).apply {
            layoutParams = LayoutParams(
                dpToPx(48), dpToPx(48)
            )
        }
        container.addView(spinner)

        tvMessage = TextView(context).apply {
            textSize = 16f
            setTextColor(Color.WHITE)
            gravity = Gravity.CENTER
            layoutParams = LayoutParams(
                LayoutParams.WRAP_CONTENT,
                LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = dpToPx(16)
            }
        }
        container.addView(tvMessage)

        addView(container)
    }

    fun show(message: String) {
        tvMessage.text = message
        visibility = View.VISIBLE
        bringToFront()
    }

    fun hide() {
        visibility = View.GONE
    }

    private fun dpToPx(dp: Int): Int {
        return (dp * context.resources.displayMetrics.density).toInt()
    }
}
