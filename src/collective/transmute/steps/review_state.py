from collective.transmute import _types as t
from collective.transmute.utils import workflow


def _is_valid_state(state_filter: tuple[str, ...], review_state: str) -> bool:
    """Check if review_state is allowed to be processed."""
    status = True
    if review_state and state_filter:
        status = review_state in state_filter
    return status


async def process_review_state(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    review_state: str = item.get("review_state", "")
    state_filter: tuple[str, ...] = settings.review_state["filter"]["allowed"]
    if not _is_valid_state(state_filter, review_state):
        yield None
    else:
        item = workflow.rewrite_workflow_history(item)
        yield item
