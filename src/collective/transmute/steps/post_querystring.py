"""
Pipeline steps for post-processing querystrings in ``collective.transmute``.

This module provides async generator functions for updating and normalizing
querystring definitions in collection-like objects and listing blocks during the
transformation pipeline. These steps use state information to resolve and update
querystring paths and values.
"""

from collective.transmute import _types as t
from collective.transmute.utils.querystring import post_process_querystring


async def process_querystring(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Post-process the querystring of a collection-like object or listing block.

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
        The updated item with post-processed querystring(s).

    Example
    -------
    .. code-block:: python

        >>> async for result in process_querystring(item, state, settings):
        ...     print(result['query'])
    """
    if query := item.get("query", []):
        item["query"] = post_process_querystring(query, state)
    elif blocks := item.get("blocks", {}):
        for block in blocks.values():
            if (qs := block.get("querystring", {})) and (query := qs.get("query", [])):
                block["querystring"]["query"] = post_process_querystring(query, state)
    yield item
