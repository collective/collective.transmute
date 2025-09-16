"""
Pipeline steps for handling blob fields in ``collective.transmute``.

This module provides async generator functions for extracting and processing blob
fields (such as files and images) from items in the transformation pipeline. These
steps are used by ``collective.transmute``.
"""

from collective.transmute import _types as t


BLOBS_KEYS = [
    "file",
    "image",
]


async def process_blobs(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Extract and process blob fields (file, image) from an item.

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
        The updated item with extracted blob files in '_blob_files_'.

    Example
    -------
    .. code-block:: pycon

        >>> async for result in process_blobs(item, state, settings):
        ...     print(result['_blob_files_'])
    """
    item["_blob_files_"] = {}
    for key in BLOBS_KEYS:
        data = item.pop(key, None)
        if not isinstance(data, dict):
            continue
        item["_blob_files_"][key] = data
    yield item
