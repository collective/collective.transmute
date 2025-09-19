from collective.transmute import _types as t
from urllib import parse


_CLEANUP: tuple[tuple[str, str], ...] | None = None


def _get_paths_cleanup(settings: t.TransmuteSettings) -> tuple[tuple[str, str], ...]:
    """
    Return cleanup paths from settings.

    Parameters
    ----------
    settings : TransmuteSettings
        The transmute settings object.

    Returns
    -------
    tuple[tuple[str, str], ...]
        Tuple of (source, replacement) path pairs for cleanup.

    Example
    -------
    .. code-block:: pycon

        >>> cleanup = get_paths_cleanup(settings)
    """
    global _CLEANUP
    if _CLEANUP is None:
        _CLEANUP = tuple(settings.paths["cleanup"].items())
    return _CLEANUP


def path_cleanup(
    state: t.PipelineState, settings: t.TransmuteSettings, path: str
) -> str:
    """Clean up a path using cleanup settings."""
    path = parse.unquote(path).replace(" ", "_")
    cleanup_paths = _get_paths_cleanup(settings)
    for src, rpl in cleanup_paths:
        if src in path:
            path = path.replace(src, rpl)
    return path
