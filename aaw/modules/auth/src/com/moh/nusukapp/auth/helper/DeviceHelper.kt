package com.moh.nusukapp.auth.helper

import android.content.res.Resources

object DeviceHelper {
    fun dpToPx(dp: Int): Int {
        return (dp * Resources.getSystem().displayMetrics.density).toInt()
    }

    fun dpToPx(dp: Float): Float {
        return dp * Resources.getSystem().displayMetrics.density
    }

    fun spToPx(sp: Int): Float {
        return sp * Resources.getSystem().displayMetrics.scaledDensity
    }

    fun screenWidthPx(): Int {
        return Resources.getSystem().displayMetrics.widthPixels
    }

    fun screenHeightPx(): Int {
        return Resources.getSystem().displayMetrics.heightPixels
    }
}
