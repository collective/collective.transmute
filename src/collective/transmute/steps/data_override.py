"""
Pipeline steps for handling data overrides in ``collective.transmute``.

This module provides async generator functions for overwriting item data fields
based on configuration settings in the transformation pipeline. These steps allow
customization of item fields using the data_override section in transmute.toml.
"""

from collective.transmute import _types as t


async def process_data_override(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Overwrite item data (by @id) with information from settings.

    Configuration should be added to transmute.toml, for example:

    [data_override]
    "/campus/areia/noticias" = { "title" = "Notícias" }
    "/campus/areia/home" = { "exclude_from_nav" = true, "review_state" = "private" }

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
        The updated item with overridden data fields.

    Example
    -------
    >>> async for result in process_data_override(item, state, settings):
    ...     print(result['title'])
    """
    id_ = item["@id"]
    override = settings.data_override.get(id_, {})
    for key, value in override.items():
        item[key] = value
    yield item
