"""
Pipeline step for processing Plone item review states.

This module provides functions to filter items based on their workflow review
state and to rewrite workflow history as needed. Used in the ``collective.transmute``
pipeline.

Example:
    .. code-block:: python

        >>> async for result in process_review_state(item, state, settings):
        ...     print(result)
"""

from collective.transmute import _types as t
from collective.transmute.utils import workflow


def _is_valid_state(state_filter: tuple[str, ...], review_state: str) -> bool:
    """
    Check if a review state is allowed to be processed.

    Args:
        state_filter (tuple[str, ...]): Allowed review states.
        review_state (str): The item's review state.

    Returns:
        bool: True if review_state is allowed, False otherwise.

    Example:
        .. code-block:: python

            >>> _is_valid_state(("published", "private"), "published")
            True
            >>> _is_valid_state(("published",), "private")
            False
    """
    status = True
    if review_state and state_filter:
        status = review_state in state_filter
    return status


async def process_review_state(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    """
    Pipeline step to process the review state of a Plone item.

    If the item's review state is not in the allowed filter, yields ``None``.
    Otherwise, rewrites workflow history and yields the updated item.

    Args:
        item (PloneItem): The Plone item to process.
        state (PipelineState): The pipeline state object.
        settings (TransmuteSettings): The transmute settings object.

    Yields:
        PloneItem | None: The processed item or None if filtered out.

    Example:
        .. code-block:: python

            >>> async for result in process_review_state(item, state, settings):
            ...     print(result)
    """
    review_state: str = item.get("review_state", "")
    state_filter: tuple[str, ...] = settings.review_state["filter"]["allowed"]
    if not _is_valid_state(state_filter, review_state):
        yield None
    else:
        item = workflow.rewrite_workflow_history(item)
        yield item
