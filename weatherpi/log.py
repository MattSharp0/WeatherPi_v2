import logging
import os
import sys
from datetime import date, timedelta
from typing import Optional

LOG_FORMAT = "%(asctime)s: %(levelname)s: %(name)s: %(message)s"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

LOG_LEVELS = ["DEBUG", "INFO", "WARN", "ERROR"]

LOG_DEFAULT = "INFO"

LOG_DIR = "logs"

iso_date = date.today().isoformat()

log_path = os.path.join(LOG_DIR, "{}.log".format(iso_date))


def get_logger(name: Optional[str] = None, level: str = LOG_DEFAULT) -> logging.Logger:
    try:
        assert level in LOG_LEVELS
    except AssertionError:
        level = LOG_DEFAULT

    logger = logging.getLogger(name=name)
    handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(filename=log_path)
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATETIME_FORMAT)
    handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.addHandler(file_handler)

    logger.setLevel(level=level)
    return logger


def clear_logs(days_to_keep: int = 5) -> None:

    try:
        logs = os.listdir(LOG_DIR)
    except FileNotFoundError:
        return

    if len(logs) == 0:
        return

    cuttoff_date = date.today() - timedelta(days=days_to_keep)

    logs_to_remove = [log for log in logs if date.fromisoformat(log.removesuffix(".log")) < cuttoff_date]

    for file in logs_to_remove:
        try:
            os.remove("{}/{}".format(LOG_DIR, file))
        except FileNotFoundError:
            pass
        except OSError:
            pass
