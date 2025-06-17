from .parse import get_settings
from pathlib import Path


__all__ = ("get_settings", "logger_settings")


def logger_settings(cwd: Path) -> tuple[bool, Path]:
    """Return debug status and log file path."""
    settings = get_settings()
    config = settings.config
    is_debug = settings.is_debug
    log_file = config.get("log_file", "transmute.log")
    return is_debug, cwd / log_file
