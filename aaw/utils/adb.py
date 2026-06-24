import subprocess
import logging

logger = logging.getLogger("aaw.adb")


def _run_adb(args, timeout=5):
    try:
        result = subprocess.run(
            ["adb"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode != 0:
            logger.debug("adb %s exited %d: %s", " ".join(args), result.returncode, result.stderr.strip()[:120])
        return result.stdout.strip(), result.returncode
    except FileNotFoundError:
        logger.warning("adb not found on PATH")
        return None, -1
    except subprocess.TimeoutExpired:
        logger.warning("adb %s timed out after %ds", " ".join(args), timeout)
        return None, -1
    except OSError as e:
        logger.error("adb %s OS error: %s", " ".join(args), e)
        return None, -1


def get_device_info():
    info = {
        "connected": False,
        "model": None,
        "android_version": None,
        "root": False,
        "serial": None,
    }

    out, code = _run_adb(["devices"])
    if code != 0 or out is None:
        logger.info("No ADB device detected")
        return info

    lines = [l for l in out.splitlines() if l.strip() and not l.startswith("List")]
    if not lines:
        return info

    first = lines[0]
    if "\tdevice" not in first and "\tunauthorized" not in first:
        return info

    info["connected"] = True
    info["serial"] = first.split("\t")[0]

    if "\tunauthorized" in first:
        return info

    prop_cmds = {
        "model": ["shell", "getprop", "ro.product.model"],
        "android_version": ["shell", "getprop", "ro.build.version.release"],
        "sdk": ["shell", "getprop", "ro.build.version.sdk"],
        "debuggable": ["shell", "getprop", "ro.debuggable"],
        "secure": ["shell", "getprop", "ro.secure"],
    }

    for key, args in prop_cmds.items():
        val, _ = _run_adb(args)
        info[key] = val if val else None

    if info.get("debuggable") == "1" or info.get("secure") == "0":
        info["root"] = True

    su_out, _ = _run_adb(["shell", "su", "-c", "id"])
    if su_out and "uid=0" in su_out:
        info["root"] = True

    return info


def get_installed_apps():
    out, code = _run_adb(["shell", "pm", "list", "packages", "-f"])
    if code != 0 or not out:
        return []

    apps = []
    for line in out.splitlines():
        if ":" not in line:
            continue
        parts = line.split(":")
        if len(parts) >= 2:
            pkg = parts[-1].strip()
            if pkg:
                apps.append({"package": pkg})
    return apps


def is_adb_available():
    out, code = _run_adb(["version"])
    return code == 0 and out is not None
