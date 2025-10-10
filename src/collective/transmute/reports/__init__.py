from collective.transmute import _types as t
from pathlib import Path


def get_reports_location(settings: t.TransmuteSettings) -> Path:
    """
    Get the reports directory from the settings.

    Parameters
    ----------
    settings : t.TransmuteSettings
        The transmute settings object.

    Returns
    -------
    Path
        The reports directory path.
    """
    path = Path(settings.config.get("reports_location", ".")).resolve()
    return path
