import logging
import os
import subprocess
import shutil
from datetime import datetime

logger = logging.getLogger("aaw.apktool")

APKTOOL_CMD = "apktool"
APKSIGNER_CMD = "apksigner"

BASE_OUTPUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output"
)


def _run(cmd, timeout=120):
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode != 0:
            logger.error("%s failed: %s", " ".join(cmd), result.stderr.strip()[:300])
        else:
            logger.info("%s succeeded", " ".join(cmd))
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except FileNotFoundError:
        logger.warning("command not found: %s", cmd[0])
        return None, "command not found", -1
    except subprocess.TimeoutExpired:
        logger.warning("command timed out: %s", " ".join(cmd))
        return None, "timed out", -1
    except OSError as e:
        logger.error("OS error running %s: %s", " ".join(cmd), e)
        return None, str(e), -1


def is_apktool_available():
    out, _, code = _run([APKTOOL_CMD, "--version"], timeout=10)
    return code == 0 and out is not None


def is_apksigner_available():
    out, _, code = _run([APKSIGNER_CMD, "--version"], timeout=10)
    return code == 0 and out is not None


def _get_app_output_dir(app_name, package):
    ts = datetime.now().strftime("%H-%M-%S_%A-%d-%m-%Y")
    pkg_dir = package.replace(".", os.sep) if "." in package else package
    d = os.path.join(BASE_OUTPUT, app_name, pkg_dir, ts, "app")
    os.makedirs(d, exist_ok=True)
    return d


def pull_apk(app_name, package, serial=None):
    logger.info("pull_apk: %s (%s)", app_name, package)
    dest_dir = _get_app_output_dir(app_name, package)

    out, _, code = _run(
        ["adb", "shell", "pm", "path", package], timeout=10
    )
    if code != 0 or not out:
        logger.error("Failed to get APK path for %s", package)
        return False, "Failed to get APK path"

    paths = []
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("package:"):
            paths.append(line[8:])

    if not paths:
        return False, "No APK paths found"

    pulled = []
    for apk_path in paths:
        fname = os.path.basename(apk_path)
        dest = os.path.join(dest_dir, fname)
        _, _, code = _run(["adb", "pull", apk_path, dest], timeout=60)
        if code == 0:
            pulled.append(fname)
        else:
            logger.error("Failed to pull %s", apk_path)

    if pulled:
        return True, f"Pulled {len(pulled)} APK(s) to {dest_dir}"
    return False, "Failed to pull any APK"


def unpack_apk(apk_path, output_dir=None):
    logger.info("unpack_apk: %s", apk_path)
    if not os.path.isfile(apk_path):
        return False, f"APK not found: {apk_path}"

    if output_dir is None:
        output_dir = os.path.splitext(apk_path)[0] + "_unpacked"

    if os.path.isdir(output_dir):
        shutil.rmtree(output_dir)

    _, err, code = _run(
        [APKTOOL_CMD, "d", apk_path, "-o", output_dir, "--force"],
        timeout=120,
    )
    if code == 0:
        return True, f"Unpacked to {output_dir}"
    return False, err or "Unknown error"


def repack_apk(input_dir, output_apk=None):
    logger.info("repack_apk: %s", input_dir)
    if not os.path.isdir(input_dir):
        return False, f"Directory not found: {input_dir}"

    if output_apk is None:
        output_apk = input_dir.rstrip(os.sep) + "_repacked.apk"

    out, err, code = _run(
        [APKTOOL_CMD, "b", input_dir, "-o", output_apk, "--use-aapt2"],
        timeout=120,
    )
    if code == 0:
        size = os.path.getsize(output_apk)
        return True, f"Repacked to {output_apk} ({_fmt_size(size)})"
    return False, err or "Unknown error"


def sign_apk(apk_path, keystore=None, key_alias=None):
    logger.info("sign_apk: %s", apk_path)
    if not os.path.isfile(apk_path):
        return False, f"APK not found: {apk_path}"

    if keystore and key_alias:
        cmd = [
            APKSIGNER_CMD, "sign",
            "--ks", keystore,
            "--ks-key-alias", key_alias,
            apk_path,
        ]
    else:
        cmd = [APKSIGNER_CMD, "sign", apk_path]

    out, err, code = _run(cmd, timeout=60)
    if code == 0:
        return True, f"Signed: {apk_path}"
    return False, err or "Signing failed"


def _fmt_size(size):
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
