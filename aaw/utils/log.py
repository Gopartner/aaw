import logging
import os
import sys
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")


def setup_logger():
    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(LOG_DIR, f"aaw_{timestamp}.log")

    logger = logging.getLogger("aaw")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    fh.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    logger.addHandler(fh)

    sys.excepthook = _handle_uncaught_exception

    logger.info("=== AAW Started ===")
    return logger


def _handle_uncaught_exception(exc_type, exc_value, exc_tb):
    logger = logging.getLogger("aaw")
    if issubclass(exc_type, KeyboardInterrupt):
        logger.info("KeyboardInterrupt — shutting down")
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_tb))


def get_logger(name=None):
    return logging.getLogger(name or "aaw")
