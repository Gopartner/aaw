import sys
import logging
import ctypes
import atexit

from aaw.app import AAW
from aaw.utils import setup_logger


def _restore_console():
    """Restore console mode on Windows in case Textual leaves it in raw mode."""
    if sys.platform != "win32":
        return
    try:
        kernel32 = ctypes.windll.kernel32
        STD_INPUT_HANDLE = -10
        ENABLE_ECHO_INPUT = 0x0004
        ENABLE_LINE_INPUT = 0x0002
        ENABLE_PROCESSED_INPUT = 0x0001
        ENABLE_INSERT_MODE = 0x0020
        ENABLE_QUICK_EDIT_MODE = 0x0040
        ENABLE_EXTENDED_FLAGS = 0x0080
        mode = ENABLE_PROCESSED_INPUT | ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT | \
               ENABLE_INSERT_MODE | ENABLE_QUICK_EDIT_MODE | ENABLE_EXTENDED_FLAGS
        kernel32.SetConsoleMode(kernel32.GetStdHandle(STD_INPUT_HANDLE), mode)
    except Exception:
        pass

atexit.register(_restore_console)


def main():
    logger = setup_logger()
    try:
        app = AAW()
        exit_code = app.run()
        return exit_code
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received")
        return 0
    except Exception:
        logger.critical("Fatal error", exc_info=True)
        return 1
    finally:
        logging.getLogger("aaw").info("=== AAW Stopped ===")
        logging.shutdown()
        _restore_console()


if __name__ == "__main__":
    sys.exit(main())
