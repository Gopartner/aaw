package com.moh.nusukapp.auth.ui

import android.content.Context
import android.graphics.Color
import android.graphics.Typeface
import android.view.Gravity
import android.view.View
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView

class StatusView(context: Context) : LinearLayout(context) {

    private val iconView: ImageView
    private val tvMessage: TextView
    private val tvSubMessage: TextView

    init {
        orientation = LinearLayout.VERTICAL
        gravity = Gravity.CENTER
        visibility = View.GONE

        iconView = ImageView(context).apply {
            layoutParams = LayoutParams(dpToPx(48), dpToPx(48))
        }
        addView(iconView)

        tvMessage = TextView(context).apply {
            textSize = 16f
            setTypeface(null, Typeface.BOLD)
            gravity = Gravity.CENTER
            layoutParams = LayoutParams(
                LayoutParams.WRAP_CONTENT,
                LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = dpToPx(12)
            }
        }
        addView(tvMessage)

        tvSubMessage = TextView(context).apply {
            textSize = 13f
            gravity = Gravity.CENTER
            layoutParams = LayoutParams(
                LayoutParams.WRAP_CONTENT,
                LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = dpToPx(6)
            }
        }
        addView(tvSubMessage)
    }

    fun showSuccess(message: String, subMessage: String = "") {
        iconView.setImageResource(android.R.drawable.ic_menu_compass)
        tvMessage.setTextColor(Color.parseColor("#2E7D32"))
        tvMessage.text = message
        tvSubMessage.setTextColor(Color.parseColor("#6F6F6F"))
        tvSubMessage.text = subMessage
        tvSubMessage.visibility = if (subMessage.isEmpty()) View.GONE else View.VISIBLE
        visibility = View.VISIBLE
    }

    fun showError(message: String, subMessage: String = "") {
        iconView.setImageResource(android.R.drawable.ic_menu_close_clear_cancel)
        tvMessage.setTextColor(Color.parseColor("#D32F2F"))
        tvMessage.text = message
        tvSubMessage.setTextColor(Color.parseColor("#6F6F6F"))
        tvSubMessage.text = subMessage
        tvSubMessage.visibility = if (subMessage.isEmpty()) View.GONE else View.VISIBLE
        visibility = View.VISIBLE
    }

    fun hide() {
        visibility = View.GONE
    }

    private fun dpToPx(dp: Int): Int {
        return (dp * context.resources.displayMetrics.density).toInt()
    }
}
