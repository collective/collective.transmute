from collective.transmute import _types as t
from collective.transmute.utils import querystring as qs_utils


POST_PROCESSING_STEP = "collective.transmute.steps.post_querystring.process_querystring"


async def processor(item: t.PloneItem, state: t.PipelineState) -> t.PloneItemGenerator:
    """Fix a collection."""
    query = item.get("query", [])
    if query:
        item["query"], post_processing = qs_utils.cleanup_querystring(query)
        if post_processing:
            uid = item["UID"]
            if uid not in state.post_processing:
                state.post_processing[uid] = []
            state.post_processing[uid].append(POST_PROCESSING_STEP)
    yield item
