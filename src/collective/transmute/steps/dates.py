"""
Pipeline step for filtering items by date in ``collective.transmute``.

This module provides async generator functions for filtering Plone items based on
date fields in the transformation pipeline. Items older than configured dates are
dropped from the pipeline.
"""

from collective.transmute import _types as t
from collective.transmute.settings import get_settings
from functools import cache


@cache
def _date_filters_from_settings() -> tuple[tuple[str, str], ...]:
    """
    Get date filters from settings.

    Returns:
        tuple[tuple[str, str], ...]: Tuple of (field_name, date_threshold) pairs.

    Example:
        >>> filters = _date_filters_from_settings()
        >>> # Returns: (('created', '2020-01-01'), ('modified', '2019-01-01'))
    """
    settings = get_settings()
    steps = settings.steps
    filters = steps.get("date_filter", {})
    return tuple(filters.items())


async def filter_by_date(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    """
    Pipeline step to filter items by date fields.

    Drops items that have date field values older than configured thresholds.
    If any configured date field is older than its threshold, the item is dropped.

    Configuration should be added to ``transmute.toml``, for example:

    ```toml
    [steps.date_filter]
    "created" = "2000-01-01T00:00:00"
    ```

    Args:
        item (PloneItem): The Plone item to process.
        state (PipelineState): The pipeline state object.
        settings (TransmuteSettings): The transmute settings object.

    Yields:
        PloneItem | None: The item if it passes date filters, None if dropped.

    Example:
        >>> async for result in filter_by_date(item, state, settings):
        ...     if result:
        ...         print(f"Item {item['@id']} passed date filter")
        ...     else:
        ...         print("Item was dropped due to old date")
    """
    filters = _date_filters_from_settings()
    drop = False
    if filters:
        for field, since in filters:
            value: str | None = item.get(field)
            if value and value < since:
                drop = True
                break
    if drop:
        yield None
    else:
        yield item
