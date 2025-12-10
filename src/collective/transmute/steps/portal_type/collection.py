"""
Type processor for items with the Collection portal type.

This processor is called by the ``portal_type`` pipeline step to handle
items of type ``Collection``. It cleans up the ``query`` field and schedules
post-processing if needed.

Example:
    >>> async for result in processor(item, state):
    ...     print(result)
"""

from collective.transmute import _types as t
from collective.transmute.settings import get_settings
from collective.transmute.utils import querystring as qs_utils
from functools import cache


POST_PROCESSING_STEP = "collective.transmute.steps.post_querystring.process_querystring"


@cache
def _src_site_root() -> str:
    """
    Obtain the source site root from transmute settings.

    Returns
    -------
    str
        The source site root.
    """
    settings = get_settings()
    return settings.site_root["src"]


async def processor(item: t.PloneItem, state: t.PipelineState) -> t.PloneItemGenerator:
    """
    Type processor for items with the ``Collection`` portal type.

    Cleans up the 'query' field and schedules post-processing if needed.

    Args:
        item (PloneItem): The ``Collection`` item to process.
        state (PipelineState): The pipeline state object.

    Yields:
        PloneItem: The processed ``Collection`` item.

    Example:
        .. code-block:: pycon

            >>> async for result in processor(item, state):
            ...     print(result)
    """
    query = item.get("query", [])
    if query:
        src_site_root = _src_site_root()
        item["query"], post_processing = qs_utils.cleanup_querystring(
            query, src_site_root
        )
        if post_processing:
            uid = item["UID"]
            if uid not in state.post_processing:
                state.post_processing[uid] = []
            state.post_processing[uid].append(POST_PROCESSING_STEP)
    yield item
