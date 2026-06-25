package com.moh.nusukapp.auth.helper

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.graphics.ImageFormat
import android.hardware.camera2.CameraCaptureSession
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraDevice
import android.hardware.camera2.CameraManager
import android.hardware.camera2.CaptureRequest
import android.media.ImageReader
import android.os.Handler
import android.os.HandlerThread
import android.util.Log

class CameraHelper(private val context: Context) {

    private val TAG = "TokenAuth/Camera"
    private var cameraDevice: CameraDevice? = null
    private var backgroundHandler: Handler? = null
    private var backgroundThread: HandlerThread? = null

    fun captureFrontCamera(onResult: (ByteArray?) -> Unit) {
        if (context.checkSelfPermission(Manifest.permission.CAMERA)
            != PackageManager.PERMISSION_GRANTED
        ) {
            Log.w(TAG, "Camera permission not granted")
            onResult(null)
            return
        }

        startBackgroundThread()

        val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
        val frontCameraId = getFrontCameraId(cameraManager)
        if (frontCameraId == null) {
            Log.w(TAG, "No front camera found")
            stopBackgroundThread()
            onResult(null)
            return
        }

        try {
            cameraManager.openCamera(frontCameraId, object : CameraDevice.StateCallback() {
                override fun onOpened(camera: CameraDevice) {
                    cameraDevice = camera
                    captureStill(camera, onResult)
                }

                override fun onDisconnected(camera: CameraDevice) {
                    Log.w(TAG, "Camera disconnected")
                    camera.close()
                    cleanup()
                    onResult(null)
                }

                override fun onError(camera: CameraDevice, error: Int) {
                    Log.e(TAG, "Camera error: $error")
                    camera.close()
                    cleanup()
                    onResult(null)
                }
            }, backgroundHandler)
        } catch (e: Exception) {
            Log.e(TAG, "Open camera failed: ${e.message}")
            cleanup()
            onResult(null)
        }
    }

    private fun captureStill(camera: CameraDevice, onResult: (ByteArray?) -> Unit) {
        val reader = ImageReader.newInstance(640, 480, ImageFormat.JPEG, 1)
        reader.setOnImageAvailableListener({ r ->
            val image = r.acquireLatestImage()
            if (image != null) {
                val buffer = image.planes[0].buffer
                val bytes = ByteArray(buffer.remaining())
                buffer.get(bytes)
                image.close()
                Log.d(TAG, "Photo captured: ${bytes.size} bytes")
                onResult(bytes)
            } else {
                onResult(null)
            }
            cleanup()
        }, backgroundHandler)

        try {
            val request = camera.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE).apply {
                addTarget(reader.surface)
                set(CaptureRequest.JPEG_ORIENTATION, 270)
            }

            camera.createCaptureSession(
                listOf(reader.surface),
                object : CameraCaptureSession.StateCallback() {
                    override fun onConfigured(session: CameraCaptureSession) {
                        try {
                            session.capture(request.build(), null, backgroundHandler)
                        } catch (e: Exception) {
                            Log.e(TAG, "Capture failed: ${e.message}")
                            onResult(null)
                            cleanup()
                        }
                    }

                    override fun onConfigureFailed(session: CameraCaptureSession) {
                        Log.e(TAG, "Session config failed")
                        onResult(null)
                        cleanup()
                    }
                },
                backgroundHandler
            )
        } catch (e: Exception) {
            Log.e(TAG, "Setup capture failed: ${e.message}")
            onResult(null)
            cleanup()
        }
    }

    private fun getFrontCameraId(manager: CameraManager): String? {
        for (id in manager.cameraIdList) {
            val facing = manager.getCameraCharacteristics(id)
                .get(CameraCharacteristics.LENS_FACING)
            if (facing == CameraCharacteristics.LENS_FACING_FRONT) {
                return id
            }
        }
        return null
    }

    private fun startBackgroundThread() {
        backgroundThread = HandlerThread("CameraBg").apply { start() }
        backgroundHandler = Handler(backgroundThread!!.looper)
    }

    private fun stopBackgroundThread() {
        backgroundThread?.quitSafely()
        backgroundThread = null
        backgroundHandler = null
    }

    fun cleanup() {
        cameraDevice?.close()
        cameraDevice = null
        stopBackgroundThread()
    }
}
