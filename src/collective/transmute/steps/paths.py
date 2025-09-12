"""
Pipeline steps for handling path filtering in collective.transmute.

This module provides functions and async generator steps for filtering and validating
item paths in the transformation pipeline. These steps use settings to determine which
paths are allowed or dropped during processing.
"""

from collective.transmute import _types as t


def _is_valid_path(path: str, allowed: set[str], drop: set[str]) -> bool:
    """
    Check if a path is allowed to be processed based on allowed and drop prefixes.

    Parameters
    ----------
    path : str
        The path to check.
    allowed : set[str]
        Set of allowed path prefixes.
    drop : set[str]
        Set of drop path prefixes.

    Returns
    -------
    bool
        True if the path is allowed, False otherwise.

    Example
    -------
    >>> _is_valid_path('/foo/bar', {'/foo'}, {'/foo/bar'})
    False
    """
    status = True
    for prefix in drop:
        if path.startswith(prefix):
            return False
    if allowed:
        status = False
        for prefix in allowed:
            if path.startswith(prefix):
                return True
    return status


async def process_paths(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Filter items based on path settings, yielding only allowed items.

    Parameters
    ----------
    item : PloneItem
        The item to process.
    state : PipelineState
        The pipeline state object.
    settings : TransmuteSettings
        The transmute settings object.

    Yields
    ------
    PloneItem or None
        The item if allowed, or None if dropped.

    Example
    -------
    >>> async for result in process_paths(item, state, settings):
    ...     print(result)
    """
    id_ = item["@id"]
    path_filter = settings.paths["filter"]
    allowed = path_filter["allowed"]
    drop = path_filter["drop"]
    if not _is_valid_path(id_, allowed, drop):
        yield None
    else:
        yield item
