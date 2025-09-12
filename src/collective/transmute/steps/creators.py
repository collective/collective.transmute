"""
Pipeline steps for handling creators in collective.transmute.

This module provides async generator functions for processing and normalizing
creator fields on Plone items in the transformation pipeline. These steps update
and filter creators based on configuration settings.
"""

from collective.transmute import _types as t


async def process_creators(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Process and filter the list of creators for an item.

    Configuration should be added to transmute.toml, for example:

    [principals]
    default = 'Plone'
    remove = ['admin']

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
        The updated item with filtered creators.

    Example
    -------
    >>> async for result in process_creators(item, state, settings):
    ...     print(result['creators'])
    """
    remove = settings.principals["remove"]
    default = [settings.principals["default"]]
    current = item.get("creators", [])
    creators = [creator for creator in current if creator not in remove]
    if not creators:
        creators = default
    item["creators"] = creators
    yield item
