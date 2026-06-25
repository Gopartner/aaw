package com.moh.nusukapp.auth.ui

import android.content.Context
import android.graphics.Color
import android.view.Gravity
import android.widget.LinearLayout
import android.widget.TextView

class CountdownView(context: Context) : LinearLayout(context) {

    private val tvPrefix: TextView
    private val tvCountdown: TextView

    init {
        orientation = VERTICAL
        gravity = Gravity.CENTER

        tvPrefix = TextView(context).apply {
            textSize = 13f
            setTextColor(Color.parseColor("#6F6F6F"))
            gravity = Gravity.CENTER
            layoutParams = LayoutParams(
                LayoutParams.WRAP_CONTENT,
                LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = dpToPx(12)
            }
        }
        addView(tvPrefix)

        tvCountdown = TextView(context).apply {
            textSize = 20f
            setTextColor(Color.parseColor("#111111"))
            gravity = Gravity.CENTER
            layoutParams = LayoutParams(
                LayoutParams.WRAP_CONTENT,
                LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = dpToPx(4)
            }
        }
        addView(tvCountdown)
    }

    fun setPrefix(text: String) {
        tvPrefix.text = text
    }

    fun setTime(text: String) {
        tvCountdown.text = text
    }

    private fun dpToPx(dp: Int): Int {
        return (dp * context.resources.displayMetrics.density).toInt()
    }
}
