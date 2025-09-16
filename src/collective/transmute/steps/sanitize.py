"""
Pipeline step for sanitizing Plone items by dropping unwanted keys.

This module provides functions to remove specified keys from Plone items,
including block-related keys if present. Used in the ``collective.transmute`` pipeline.

Example:
    .. code-block:: pycon

        >>> async for result in process_cleanup(item, state, settings):
        ...     print(result)
"""

from collective.transmute import _types as t


_DROP_KEYS: dict[bool, set[str]] = {}


def get_drop_keys(has_blocks: bool, settings: t.TransmuteSettings) -> set[str]:
    """
    Get the set of keys to drop from a Plone item during sanitization.

    Args:
        has_blocks (bool): Whether the item contains blocks.
        settings (TransmuteSettings): The transmute settings object.

    Returns:
        set[str]: The set of keys to drop.

    Example:
        .. code-block:: pycon

            >>> get_drop_keys(True, settings)
            {'title', 'description', 'blocks'}
    """
    if has_blocks not in _DROP_KEYS:
        drop_keys: set[str] = set(settings.sanitize["drop_keys"])
        if has_blocks:
            block_keys: set[str] = set(settings.sanitize["block_keys"])
            drop_keys = drop_keys | block_keys
        _DROP_KEYS[has_blocks] = drop_keys
    return _DROP_KEYS[has_blocks]


async def process_cleanup(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    """
    Pipeline step to sanitize a Plone item by dropping unwanted keys.

    Removes keys specified in ``settings.sanitize['drop_keys']`` and, if blocks are
    present,also removes ``settings.sanitize['block_keys']``.

    Args:
        item (PloneItem): The Plone item to sanitize.
        state (PipelineState): The pipeline state object.
        settings (TransmuteSettings): The transmute settings object.

    Yields:
        PloneItem: The sanitized item.

    Example:
        .. code-block:: pycon

            >>> async for result in process_cleanup(item, state, settings):
            ...     print(result)
    """
    has_blocks: bool = "blocks" in item
    drop_keys: set[str] = get_drop_keys(has_blocks, settings)
    item = {k: v for k, v in item.items() if k not in drop_keys}
    yield item
