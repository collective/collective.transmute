"""
Pipeline steps for handling constraints in ``collective.transmute``.

This module provides async generator functions for processing and normalizing
constraints on Plone items in the transformation pipeline. These steps fix and
update ``exportimport`` constraints using portal type mappings.
"""

from collective.transmute import _types as t
from collective.transmute.utils.portal_types import fix_portal_type


async def process_constraints(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Fix and normalize ``exportimport`` constraints for a Plone item.

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
        The updated item with normalized constraints.

    Example
    -------
    .. code-block:: python

        >>> async for result in process_constraints(item, state, settings):
        ...     print(result['exportimport.constrains'])
    """
    key = "exportimport.constrains"
    if old_constrains := item.pop(key, None):
        constrains = {}
        for c_type, value in old_constrains.items():
            value = {fix_portal_type(v) for v in value}
            # Remove empty value
            if "" in value:
                value.remove("")
            constrains[c_type] = list(value)
        item[key] = constrains
    yield item
