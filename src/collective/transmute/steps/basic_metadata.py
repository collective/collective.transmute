"""
Pipeline steps for basic metadata normalization in collective.transmute.

This module provides async generator functions for cleaning and setting metadata fields
such as title and description. These steps are used in the transformation pipeline and
are documented for Sphinx autodoc.
"""
from collective.transmute import _types as t


async def process_title_description(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Strip whitespace from the 'title' and 'description' fields of an item.

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
        The updated item with stripped title and description.

    Example
    -------
    >>> async for result in process_title_description(item, state, settings):
    ...     print(result['title'])
    """
    for field in ("title", "description"):
        cur_value = item.get(field)
        if cur_value is not None:
            item[field] = cur_value.strip()
    yield item


async def process_title(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Ensure the 'title' field is set for an item, using filename or id if missing.

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
        The updated item with a guaranteed title field.

    Example
    -------
    >>> async for result in process_title(item, state, settings):
    ...     print(result['title'])
    """
    title = item.get("title", None)
    if not title:
        if blob := item.get("image") or item.get("file"):
            item["title"] = blob["filename"]
        else:
            item["title"] = item["id"]
    yield item
