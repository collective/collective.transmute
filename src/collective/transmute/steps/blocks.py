from collective.html2blocks.converter import volto_blocks
from collective.transmute import _types as t
from collective.transmute.settings import pb_config


def _process_collection(item: dict, blocks: list[dict]) -> list[dict]:
    """Add a listing block."""
    # TODO: Process query to remove old types
    query = item.get("query")
    if query:
        block = {
            "@type": "listing",
            "headline": "",
            "headlineTag": "h2",
            "querystring": {
                "query": query,
                "sort_on": item["sort_on"],
                "sort_order": (
                    "ascending" if item["sort_reversed"] == "" else "descending"
                ),
                "sort_order_boolean": True,
            },
            "b_size": item.get("item_count", 10),
            "limit": item.get("limit", 1000),
            "styles": {},
            "variation": "summary",
        }
        blocks.append(block)
    return blocks


def _get_default_blocks(
    type_: str, has_image: bool, has_description: bool
) -> list[dict]:
    type_info = pb_config.types.get(type_, {})
    default_blocks = type_info.get("override_blocks", type_info.get("blocks", None))
    blocks = [b.to_dict() for b in default_blocks] if default_blocks else []
    if default_blocks:
        blocks = []
        for block in [b.to_dict() for b in default_blocks]:
            block_type = block["@type"]
            if (block_type == "leadimage" and not has_image) and (
                block_type == "description" and not has_description
            ):
                continue
            blocks.append(block)
    return blocks


async def process_blocks(
    item: dict, metadata: t.MetadataInfo, config: t.Settings
) -> t.PloneItemGenerator:
    type_ = item["@type"]
    has_image = bool(item.get("image"))
    has_description = bool(item.get("description", "").strip())
    blocks = _get_default_blocks(type_, has_image, has_description)
    if blocks:
        if item["_orig_type"] == "Collection":
            blocks = _process_collection(item, blocks)
        text = item.get("text", {})
        src = text.get("data", "") if text else ""
        blocks_info = volto_blocks(source=src, default_blocks=blocks)
        item.update(blocks_info)
    yield item
