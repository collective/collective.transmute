"""
Pipeline steps for handling blob fields in ``collective.transmute``.

This module provides async generator functions for extracting and processing blob
fields (such as files and images) from items in the transformation pipeline. These
steps are used by ``collective.transmute``.

The field names can be configured in the Transmute settings under the
`steps.blobs.field_names` key. The default value is:


.. code-block:: toml

    [steps.blobs]
    field_names = [
        "file",
        "image",
        "preview_image",
    ]


"""

from collective.transmute import _types as t
from collective.transmute.settings import get_settings
from functools import cache


@cache
def _blobs_field_names() -> list[str]:
    """
    Obtain the list of blob field names from transmute settings.

    Returns
    -------
    list[str]
        A list of possible blob field names.
    """
    settings = get_settings()
    blob_step_settings: dict = settings.steps.get("blobs", {})
    field_names: list[str] = blob_step_settings.get("field_names", [])
    return field_names


async def process_blobs(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Extract and process blob fields (file, image, preview_image) from an item.

    The extracted blob fields are stored in a new key '_blob_files_' within the item.

    If the blob field value is not a dictionary, it will be ignored.

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
    for key in _blobs_field_names():
        data = item.pop(key, None)
        # Only process if data is a dict (blob field data)
        if not isinstance(data, dict):
            continue
        item["_blob_files_"][key] = data
    yield item
