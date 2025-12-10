from pathlib import Path

import logging


__version__ = "1.0.0a6"

PACKAGE_NAME = "collective.transmute"


_LOGGER: logging.Logger | None = None


def get_logger() -> logging.Logger:
    from collective.transmute.settings import logger_settings

    global _LOGGER
    is_debug, path = logger_settings(Path.cwd())

    # Initialize logger if not already done
    if _LOGGER is None:
        level = logging.DEBUG if is_debug else logging.INFO
        logger = logging.getLogger(PACKAGE_NAME)
        logger.setLevel(level)

        file_handler = logging.FileHandler(path, "a")
        file_handler.setLevel(level)
        file_formatter = logging.Formatter("%(levelname)s: %(message)s")
        file_handler.setFormatter(file_formatter)
        if file_handler not in logger.handlers:
            logger.addHandler(file_handler)
        _LOGGER = logger

    return _LOGGER


def main():
    from collective.transmute.utils import settings

    settings.register_encoders()


main()
