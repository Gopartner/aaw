package com.moh.nusukapp.auth.ui

import android.animation.ObjectAnimator
import android.animation.ValueAnimator
import android.content.Context
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.text.Editable
import android.text.InputFilter
import android.text.InputType
import android.text.TextWatcher
import android.view.Gravity
import android.view.KeyEvent
import android.view.View
import android.view.animation.DecelerateInterpolator
import android.widget.EditText
import android.widget.LinearLayout

class OtpInputView(context: Context) : LinearLayout(context) {

    private var otpLength = 6
    private val fields = mutableListOf<EditText>()
    private var isBlocked = false
    private var onOtpComplete: ((String) -> Unit)? = null
    private var gapDp = 8f
    private var boxWidthPx = 0
    private var boxHeightPx = 0

    init {
        orientation = HORIZONTAL
        gravity = Gravity.CENTER
        val density = context.resources.displayMetrics.density
        boxWidthPx = (48 * density).toInt()
        boxHeightPx = (56 * density).toInt()
        buildFields()
        autoSizeFields()
    }

    fun autoSizeFields() {
        post {
            val totalWidth = measuredWidth
            if (totalWidth <= 0) return@post
            val gapPx = (gapDp * context.resources.displayMetrics.density).toInt()
            val totalGapPx = (otpLength - 1) * gapPx
            val calcWidth = (totalWidth - totalGapPx) / otpLength
            if (calcWidth > 0) {
                boxWidthPx = calcWidth
                boxHeightPx = (calcWidth * 1.15f).toInt()
                rebuildFields()
            }
        }
    }

    private fun rebuildFields() {
        val otp = getOtp()
        for (f in fields) f.clearFocus()
        fields.clear()
        removeAllViews()
        for (i in 0 until otpLength) {
            val field = createField(i)
            fields.add(field)
            addView(field)
            if (i < otpLength - 1) {
                addView(createSpacer())
            }
        }
        if (otp.isNotEmpty()) {
            for (i in otp.indices) {
                if (i < fields.size) {
                    fields[i].setText(otp[i].toString())
                }
            }
        }
        fields.getOrNull(0)?.requestFocus()
        updateAllFieldBackgrounds()
    }

    private fun buildFields() {
        fields.clear()
        removeAllViews()
        for (i in 0 until otpLength) {
            val field = createField(i)
            fields.add(field)
            addView(field)
            if (i < otpLength - 1) {
                addView(createSpacer())
            }
        }
        fields.getOrNull(0)?.requestFocus()
    }

    fun setOtpLength(length: Int) {
        otpLength = length
        rebuildFields()
    }

    fun getOtp(): String {
        val sb = StringBuilder()
        for (f in fields) sb.append(f.text?.toString() ?: "")
        return sb.toString()
    }

    fun clearAll() {
        for (f in fields) f.text?.clear()
        fields.getOrNull(0)?.requestFocus()
    }

    fun setBlocked(blocked: Boolean) {
        isBlocked = blocked
        for (f in fields) f.isEnabled = !blocked
    }

    fun setOnOtpCompleteListener(l: (String) -> Unit) {
        onOtpComplete = l
    }

    fun shakeError() {
        val animator = ValueAnimator.ofFloat(-8f, 8f, -6f, 6f, 0f)
        animator.duration = 400
        animator.interpolator = DecelerateInterpolator()
        animator.addUpdateListener { anim ->
            translationX = anim.animatedValue as Float
        }
        animator.start()
    }

    private fun createField(index: Int): EditText {
        val density = context.resources.displayMetrics.density
        val box = EditText(context)

        box.layoutParams = LayoutParams(boxWidthPx, boxHeightPx)
        box.gravity = Gravity.CENTER
        box.textSize = 20f
        box.setTypeface(null, Typeface.BOLD)
        box.inputType = InputType.TYPE_CLASS_NUMBER
        box.setFilters(arrayOf(InputFilter.LengthFilter(1)))
        box.setTextColor(Color.parseColor("#111111"))
        box.setPadding(0, 0, 0, 0)
        box.isCursorVisible = false
        box.setIncludeFontPadding(false)

        updateFieldBackground(box, false, false)

        box.onFocusChangeListener = { _, focused ->
            val hasText = !box.text.isNullOrEmpty()
            updateFieldBackground(box, focused, hasText)
            if (focused && hasText) {
                box.setSelection(box.text!!.length)
            }
        }

        box.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
            override fun afterTextChanged(s: Editable?) {
                if (isBlocked) return
                if (s?.length == 1 && index < fields.size - 1) {
                    fields[index + 1].requestFocus()
                    animateField(box)
                }
                updateAllFieldBackgrounds()
                if (getOtp().length == otpLength) {
                    onOtpComplete?.invoke(getOtp())
                }
            }
        })

        box.setOnKeyListener { _, keyCode, event ->
            if (isBlocked) return@setOnKeyListener true
            if (event.action == KeyEvent.ACTION_DOWN && keyCode == KeyEvent.KEYCODE_DEL) {
                if (box.text.isNullOrEmpty() && index > 0) {
                    fields[index - 1].requestFocus()
                    fields[index - 1].text?.clear()
                    return@setOnKeyListener true
                }
            }
            false
        }

        return box
    }

    private fun createSpacer(): View {
        val density = context.resources.displayMetrics.density
        val spacer = View(context)
        spacer.layoutParams = LayoutParams((gapDp * density).toInt(), 0)
        return spacer
    }

    private fun updateFieldBackground(box: EditText, focused: Boolean, hasText: Boolean) {
        val density = context.resources.displayMetrics.density
        val bg = GradientDrawable().apply {
            shape = GradientDrawable.RECTANGLE
            cornerRadius = 12 * density
            when {
                focused && !hasText -> {
                    setColor(Color.WHITE)
                    setStroke(2, Color.parseColor("#111111"))
                }
                hasText -> {
                    setColor(Color.parseColor("#F5F5F5"))
                    setStroke(1, Color.parseColor("#111111"))
                }
                else -> {
                    setColor(Color.WHITE)
                    setStroke(1, Color.parseColor("#DADADA"))
                }
            }
        }
        box.background = bg
    }

    private fun updateAllFieldBackgrounds() {
        for ((i, f) in fields.withIndex()) {
            val focused = f.isFocused
            val hasText = !f.text.isNullOrEmpty()
            updateFieldBackground(f, focused, hasText)
        }
    }

    private fun animateField(box: EditText) {
        val anim = ObjectAnimator.ofFloat(box, "scaleX", 0.9f, 1.05f, 1.0f)
        anim.duration = 120
        box.scaleY = box.scaleX
        anim.start()
    }
}
