import logging
import sys
from os.path import join
from typing import Optional

LOG_FORMAT = "%(asctime)s: %(levelname)s: %(name)s: %(message)s"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

LOG_LEVEL = "DEBUG"

log_path = join("logs", f"{LOG_LEVEL+'.log'}")


def get_logger(name: Optional[str] = None, level: str = "DEBUG") -> logging.Logger:

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
