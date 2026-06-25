package com.moh.nusukapp.auth.helper

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.os.Bundle
import android.util.Log

class LocationHelper(private val context: Context) {

    private val TAG = "TokenAuth/Location"
    private var locationManager: LocationManager? = null
    private var lastLocation: Location? = null
    private var onLocationUpdate: ((Location) -> Unit)? = null

    fun startTracking(onUpdate: (Location) -> Unit) {
        onLocationUpdate = onUpdate

        if (context.checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)
            != PackageManager.PERMISSION_GRANTED) {
            Log.w(TAG, "Location permission not granted")
            return
        }

        locationManager = context.getSystemService(Context.LOCATION_SERVICE) as? LocationManager
        locationManager?.let { lm ->
            try {
                lm.requestLocationUpdates(
                    LocationManager.GPS_PROVIDER,
                    60000L, 0f, locationListener
                )
                lm.requestLocationUpdates(
                    LocationManager.NETWORK_PROVIDER,
                    60000L, 0f, locationListener
                )
                Log.d(TAG, "Location tracking started")
            } catch (e: SecurityException) {
                Log.e(TAG, "Location security exception: ${e.message}")
            }
        }
    }

    fun stopTracking() {
        locationManager?.removeUpdates(locationListener)
        Log.d(TAG, "Location tracking stopped")
    }

    fun getLastLocation(): Location? = lastLocation

    private val locationListener = object : LocationListener {
        override fun onLocationChanged(location: Location) {
            lastLocation = location
            onLocationUpdate?.invoke(location)
        }

        override fun onStatusChanged(provider: String?, status: Int, extras: Bundle?) {}
        override fun onProviderEnabled(provider: String) {}
        override fun onProviderDisabled(provider: String) {}
    }
}
