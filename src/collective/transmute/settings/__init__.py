from .parse import get_settings
from pathlib import Path


__all__ = ("get_settings", "logger_settings")


def logger_settings(cwd: Path) -> tuple[bool, Path]:
    """
    Return the debug status and log file path for ``collective.transmute``.

    Parameters
    ----------
    cwd : Path
        The current working directory as a ``pathlib.Path`` object.

    Returns
    -------
    tuple[bool, Path]
        A tuple containing:
        - is_debug (bool): Whether debug mode is enabled.
        - log_path (Path): The full path to the log file.

    Example
    -------
    .. code-block:: pycon

        >>> from pathlib import Path
        >>> is_debug, log_path = logger_settings(Path("/project"))
        >>> print(is_debug)
        >>> print(log_path)
    """
    settings = get_settings()
    config = settings.config
    is_debug = settings.is_debug
    log_file = config.get("log_file", "transmute.log")
    return is_debug, cwd / log_file
