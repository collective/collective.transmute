"""
Pipeline steps for handling and normalizing IDs in ``collective.transmute``.

This module provides async generator functions and helpers for cleaning up, fixing,
and transforming item IDs and paths in the transformation pipeline. These steps
support export prefix removal, path cleanup, and short ID normalization.
"""

from .cleanup import path_cleanup
from .prefixes import path_prefixes
from collective.transmute import _types as t

import re


PATTERNS = [
    re.compile(r"^[ _-]*(?P<path>[^ _-]*)[ _-]*$"),
]


def fix_short_id(id_: str) -> str:
    """
    Normalize a short ID by removing spaces and special characters.

    Parameters
    ----------
    id_ : str
        The ID string to normalize.

    Returns
    -------
    str
        The normalized ID string.

    Example
    -------
    .. code-block:: pycon

        >>> fix_short_id(' my id ')
        'my_id'
    """
    for pattern in PATTERNS:
        if match := re.match(pattern, id_):
            id_ = match.groupdict()["path"]
    if " " in id_:
        id_ = id_.replace(" ", "_")
    return id_


async def process_export_prefix(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Remove export prefixes from the ``@id`` field of an item.

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
    PloneItem
        The updated item with export prefix removed from ``@id``.

    Example
    -------
    .. code-block:: pycon

        >>> async for result in process_export_prefix(item, state, settings):
        ...     print(result['@id'])
    """
    path = item["@id"]
    for src in settings.paths["export_prefixes"]:
        if path.startswith(src):
            path = path.replace(src, "")
    item["@id"] = path
    # Used in reports
    item["_@id"] = path
    yield item


async def process_ids(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Normalize and clean up the ``@id`` and ``id`` fields of an item.

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
    PloneItem
        The updated item with cleaned up IDs.

    Example
    -------
    .. code-block:: pycon

        >>> async for result in process_ids(item, state, settings):
        ...     print(result['@id'], result['id'])
    """
    path = item["@id"]
    for func in (path_cleanup, path_prefixes):
        path = func(state, settings, path)
    parts = path.rsplit("/", maxsplit=-1)
    if parts:
        parts[-1] = fix_short_id(parts[-1])
        path = "/".join(parts)
        item["@id"] = path
        item["id"] = parts[-1]
    yield item
