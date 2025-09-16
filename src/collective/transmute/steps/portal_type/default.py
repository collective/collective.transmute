"""
Default type processor used by the ``portal_type`` pipeline step.

This processor yields the item unchanged as the default behavior.

Example:
    .. code-block:: python

        >>> async for result in processor(item, state):
        ...     print(result)
"""

from collective.transmute import _types as t


async def processor(item: t.PloneItem, state: t.PipelineState) -> t.PloneItemGenerator:
    """
    Default type processor used by the ``portal_type`` pipeline step.

    Args:
        item (PloneItem): The item to process.
        state (PipelineState): The pipeline state object.

    Yields:
        PloneItem: The unchanged item.

    Example:
        .. code-block:: python

            >>> async for result in processor(item, state):
            ...     print(result)
    """
    yield item
