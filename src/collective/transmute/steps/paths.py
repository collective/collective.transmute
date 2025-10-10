"""
Pipeline steps for handling path filtering in ``collective.transmute``.

This module provides functions and async generator steps for filtering and validating
item paths in the transformation pipeline. These steps use settings to determine which
paths are allowed or dropped during processing.
"""

from collections import defaultdict
from collective.transmute import _types as t


def _is_valid_path(
    path: str, allowed: set[str], drop: set[str], dropped_by_path_prefix: dict
) -> bool:
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
    dropped_by_path_prefix : dict[str, int]
        Dictionary mapping dropped path prefixes to their count.

    Returns
    -------
    bool
        True if the path is allowed, False otherwise.

    Example
    -------
    .. code-block:: pycon

        >>> _is_valid_path('/foo/bar', {'/foo'}, {'/foo/bar'})
        False
    """
    status = True
    for prefix in drop:
        if path.startswith(prefix):
            dropped_by_path_prefix[prefix] += 1
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
    .. code-block:: pycon

        >>> async for result in process_paths(item, state, settings):
        ...     print(result)
    """
    id_ = item["@id"]
    path_filter = settings.paths["filter"]
    allowed = path_filter["allowed"]
    drop = path_filter["drop"]
    annotations = state.annotations
    if "dropped_by_path_prefix" not in annotations:
        annotations["dropped_by_path_prefix"] = defaultdict(int)
    if not _is_valid_path(id_, allowed, drop, annotations["dropped_by_path_prefix"]):
        yield None
    else:
        yield item
