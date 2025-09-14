"""
Pipeline steps for handling image conversion in ``collective.transmute``.

This module provides functions and async generator steps for converting image fields
into preview image links and managing image relations in the transformation pipeline.
These steps are used by ``collective.transmute`` for content types requiring
image conversion.
"""

from collective.transmute import _types as t
from collective.transmute.utils import item as utils


def get_conversion_types(settings: t.TransmuteSettings) -> tuple[str, ...]:
    """
    Get content types that require image to preview_image_link conversion.

    Parameters
    ----------
    settings : TransmuteSettings
        The transmute settings object.

    Returns
    -------
    tuple[str, ...]
        Tuple of content type strings.

    Example
    -------
    >>> get_conversion_types(settings)
    ('News Item', 'Document')
    """
    return settings.images["to_preview_image_link"]


async def process_image_to_preview_image_link(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Convert image field to preview_image_link and manage image relations for an item.

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
        The new image item (if created) and the updated original item.

    Example
    -------
    >>> async for result in process_image_to_preview_image_link(item, state, settings):
    ...     print(result)
    """
    type_ = item["@type"]
    metadata = state.metadata
    if type_ not in get_conversion_types(settings):
        yield item
    else:
        image = item.get("image", None)
        if isinstance(image, dict) and metadata:
            image = utils.create_image_from_item(item)
            # Register the relation between the items
            utils.add_relation(item, image, "preview_image_link", metadata)
            # Return the new image
            yield image
            yield item
        else:
            item.pop("image", None)
            item.pop("image_caption", None)
            yield item
