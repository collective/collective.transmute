from collective.transmute import _types as t
from collective.transmute.utils.querystring import post_process_querystring


async def process_querystring(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    """Post-Process the querystring of a collection-like object or listing block."""
    if query := item.get("query", []):
        item["query"] = post_process_querystring(query, state)
    elif blocks := item.get("blocks", {}):
        for block in blocks.values():
            if (qs := block.get("querystring", {})) and (query := qs.get("query", [])):
                block["querystring"]["query"] = post_process_querystring(query, state)
    yield item
