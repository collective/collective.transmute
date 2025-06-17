from .about import __version__  # noQA: F401
from pathlib import Path

import logging


PACKAGE_NAME = "collective.transmute"


def get_logger():
    from collective.transmute.settings import logger_settings

    is_debug, path = logger_settings(Path.cwd())
    level = logging.DEBUG if is_debug else logging.INFO

    logger = logging.getLogger(PACKAGE_NAME)
    logger.setLevel(level)

    file_handler = logging.FileHandler(path, "a")
    file_handler.setLevel(level)
    file_formatter = logging.Formatter("%(levelname)s: %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger
