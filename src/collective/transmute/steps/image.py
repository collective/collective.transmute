"""
Pipeline steps for handling image conversion in ``collective.transmute``.

This module provides functions and async generator steps for converting image fields
into preview image links and managing image relations in the transformation pipeline.
These steps are used by ``collective.transmute`` for content types requiring
image conversion.
"""

from collective.transmute import _types as t
from collective.transmute.utils import item as utils


IMAGE_FIELDS: tuple[str, ...] = ("image", "preview_image")


def get_conversion_types(settings: t.TransmuteSettings) -> tuple[str, ...]:
    """
    Get content types that require ``image`` to ``preview_image_link`` conversion.

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
    .. code-block:: pycon

        >>> get_conversion_types(settings)
        ('News Item', 'Document')
    """
    return settings.images["to_preview_image_link"]


def cleanup_image_fields(item: t.PloneItem) -> t.PloneItem:
    """
    Remove image fields from an item.

    Parameters
    ----------
    item : PloneItem
        The item to clean up.

    Returns
    -------
    PloneItem
        The cleaned-up item without image fields.

    Example
    -------
    .. code-block:: pycon

        >>> cleaned_item = cleanup_image_fields(item)
        >>> 'image' not in cleaned_item
        True
        >>> 'preview_image' not in cleaned_item
        True
    """
    for image_field in IMAGE_FIELDS:
        item.pop(image_field, None)
        item.pop(f"{image_field}_caption", None)
    return item


async def process_image_to_preview_image_link(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Convert an ``image`` or ``preview_image`` field to a ``preview_image_link``
    relation and manage image relations for an item.

    When both fields are present, ``preview_image`` takes precedence over ``image``.

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
    .. code-block:: pycon

        >>> async for res in process_image_to_preview_image_link(item, state, settings):
        ...     print(res)
    """
    type_ = item["@type"]
    metadata = state.metadata
    if type_ not in get_conversion_types(settings):
        yield item
    else:
        image_field = "preview_image" if "preview_image" in item else "image"
        image = item.get(image_field, None)
        if isinstance(image, dict) and metadata:
            image = utils.create_image_from_item(item, image_field)
            # Register the relation between the items
            utils.add_relation(item, image, "preview_image_link", metadata)
            # Return the new image
            yield image
        yield cleanup_image_fields(item)
