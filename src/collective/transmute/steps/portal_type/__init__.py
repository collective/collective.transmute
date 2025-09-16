"""
Pipeline step for processing and mapping Plone item portal types.

This module provides functions to pre-process items and map their portal types
according to pipeline settings. Used in the ``collective.transmute`` pipeline.

Example:
    .. code-block:: pycon

        >>> async for result in process_type(item, state, settings):
        ...     print(result)
"""

from collective.transmute import _types as t
from collective.transmute.utils import load_processor


_PROCESSORS: dict[str, t.ItemProcessor] = {}


async def _pre_process(
    item: t.PloneItem, settings: t.TransmuteSettings, state: t.PipelineState
) -> t.PloneItemGenerator:
    """
    Pre-process a Plone item using a type-specific processor.

    Args:
        item (PloneItem): The item to process.
        settings (TransmuteSettings): The transmute settings object.
        state (PipelineState): The pipeline state object.

    Yields:
        PloneItem: The processed item.

    Example:
        .. code-block:: pycon

            >>> async for processed in _pre_process(item, settings, state):
            ...     print(processed)
    """
    type_ = item["@type"]
    processor = _PROCESSORS.get(type_)
    if not processor:
        # Load the processor for the type
        processor = load_processor(type_, settings)
        _PROCESSORS[type_] = processor
    async for processed in processor(item, state):
        yield processed


async def process_type(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    """
    Pipeline step to map and update the portal type of a Plone item.

    Uses type and path mappings from settings to update the item's portal type.
    Yields None if the item should be dropped.

    Args:
        item (PloneItem): The item to process.
        state (PipelineState): The pipeline state object.
        settings (TransmuteSettings): The transmute settings object.

    Yields:
        PloneItem | None: The processed item or None if dropped.

    Example:
        .. code-block:: pycon

            >>> async for result in process_type(item, state, settings):
            ...     print(result)
    """
    types = settings.types
    types_path = settings.paths.get("portal_type", {})
    async for processed in _pre_process(item, settings, state):
        if processed:
            id_ = processed["@id"]
            type_ = processed["@type"]
            # Get the new type mapping
            new_type = types.get(type_, {}).get("portal_type")
            # Check if we have a specific mapping via type
            new_type = types_path.get(id_, new_type)
            if not new_type:
                # Dropping content
                yield None
            else:
                processed["@type"] = new_type
                processed["_orig_type"] = type_
                yield processed
        else:
            # If the item is None, we yield None
            yield None
