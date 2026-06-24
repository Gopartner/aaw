__all__ = [
    "MOCK_APPS",
    "MOCK_TIMELINE",
    "MOCK_APK_FILES",
    "MOCK_DATA_COLLECT",
    "MOCK_WORKSPACE_ITEMS",
    "MOCK_TREE",
]

MOCK_APPS = [
    {"id": 1, "name": "WhatsApp", "package": "com.whatsapp", "version": "2.26.10", "type": "User App", "type_key": "user", "uid": "10123", "target_sdk": 35, "root_access": "YES", "size": 185.2},
    {"id": 2, "name": "Chrome", "package": "com.android.chrome", "version": "126.0.6478", "type": "System App", "type_key": "system", "uid": "10145", "target_sdk": 34, "root_access": "NO", "size": 342.1},
    {"id": 3, "name": "Settings", "package": "com.android.settings", "version": "15.0", "type": "System App", "type_key": "system", "uid": "1000", "target_sdk": 35, "root_access": "NO", "size": 58.4},
    {"id": 4, "name": "Camera", "package": "com.vendor.camera", "version": "3.2.1", "type": "Vendor", "type_key": "vendor", "uid": "10167", "target_sdk": 34, "root_access": "NO", "size": 92.7},
    {"id": 5, "name": "Gmail", "package": "com.google.android.gm", "version": "2025.08", "type": "User App", "type_key": "user", "uid": "10189", "target_sdk": 35, "root_access": "NO", "size": 210.5},
    {"id": 6, "name": "Maps", "package": "com.google.android.apps.maps", "version": "11.145", "type": "User App", "type_key": "user", "uid": "10201", "target_sdk": 35, "root_access": "NO", "size": 295.8},
    {"id": 7, "name": "YouTube", "package": "com.google.android.youtube", "version": "19.45", "type": "User App", "type_key": "user", "uid": "10223", "target_sdk": 34, "root_access": "NO", "size": 178.3},
    {"id": 8, "name": "Play Store", "package": "com.android.vending", "version": "42.8", "type": "System App", "type_key": "system", "uid": "10245", "target_sdk": 35, "root_access": "NO", "size": 45.6},
    {"id": 9, "name": "Telegram", "package": "org.telegram.messenger", "version": "10.14", "type": "User App", "type_key": "user", "uid": "10267", "target_sdk": 35, "root_access": "YES", "size": 162.9},
    {"id": 10, "name": "Netflix", "package": "com.netflix.mediaclient", "version": "8.122", "type": "User App", "type_key": "user", "uid": "10289", "target_sdk": 34, "root_access": "NO", "size": 88.4},
]

MOCK_TIMELINE = [
    {"time": "10:05:42", "activity": "SplashActivity"},
    {"time": "10:05:45", "activity": "LoginActivity"},
    {"time": "10:06:10", "activity": "OTPActivity"},
    {"time": "10:06:25", "activity": "HomeActivity"},
    {"time": "10:09:31", "activity": "ProfileActivity"},
    {"time": "10:10:02", "activity": "HomeActivity"},
    {"time": "10:12:15", "activity": "ChatActivity"},
    {"time": "10:14:30", "activity": "MediaViewerActivity"},
    {"time": "10:15:45", "activity": "ChatActivity"},
    {"time": "10:17:00", "activity": "HomeActivity"},
    {"time": "10:18:22", "activity": "CallActivity"},
    {"time": "10:19:10", "activity": "HomeActivity"},
]

MOCK_APK_FILES = [
    "base.apk",
    "split_config.arm64.apk",
    "split_config.xxhdpi.apk",
    "split_config.id.apk",
]

MOCK_DATA_COLLECT = [
    "databases/",
    "shared_prefs/",
    "files/",
    "cache/",
    "external/",
]

MOCK_WORKSPACE_ITEMS = [
    "README.md",
    "SUMMARY.md",
    "AI_CONTEXT.md",
    "navigation.json",
    "timeline.json",
    "prompts/",
    "reports/",
    "graphs/",
]

MOCK_TREE = {
    "output/": {
        "WhatsApp/": {
            "com.whatsapp/": {
                "09-15-30_kamis-25-06-2026/": {},
                "10-15-22_kamis-25-06-2026/": {
                    "README.md": None,
                    "SUMMARY.md": None,
                    "AI_CONTEXT.md": None,
                    "runtime/": {},
                    "app/": {},
                    "data/": {},
                    "reports/": {},
                    "graphs/": {},
                    "prompts/": {},
                },
                "latest/": {},
            }
        }
    }
}
