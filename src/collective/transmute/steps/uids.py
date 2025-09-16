"""
Pipeline step to drop items based on their UID.
"""

from collective.transmute import _types as t


async def drop_item_by_uid(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Drop items based on their UID.

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
    PloneItem or None
        The item if not dropped, or ``None`` if dropped.

    Example
    -------
    .. code-block:: pycon

        >>> async for result in drop_item_by_uid(item, state, settings):
        ...     print(result) if result else print("Dropped")
    """
    annotations = state.annotations
    # Initialize drop_uids in annotations if not present
    if "drop_uids" not in annotations:
        annotations["drop_uids"] = {}
    item_uid = item["UID"]
    if annotations["drop_uids"].pop(item_uid, None):
        yield None
    else:
        yield item
