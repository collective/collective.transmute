from collective.html2blocks.converter import volto_blocks
from collective.transmute import _types as t


def _blocks_collection(item: t.PloneItem, blocks: list[dict]) -> list[dict]:
    """Add a listing block."""
    # TODO: Process query to remove old types
    query = item.get("query")
    if query:
        querystring = {
            "query": query,
        }

        if "sort_on" in item:
            querystring["sort_on"] = item["sort_on"]

        if "sort_order" in item:
            querystring["sort_order"] = item["sort_order"]
            querystring["sort_order_boolean"] = True
        elif "sort_reversed" in item:
            querystring["sort_order"] = (
                "ascending" if item["sort_reversed"] == "" else "descending"
            )
            querystring["sort_order_boolean"] = True

        block = {
            "@type": "listing",
            "headline": "",
            "headlineTag": "h2",
            "querystring": querystring,
            "b_size": item.get("item_count", 10),
            "limit": item.get("limit", 1000),
            "styles": {},
            "variation": "summary",
        }
        blocks.append(block)
    return blocks


def _blocks_folder(item: t.PloneItem, blocks: list[dict]) -> list[dict]:
    """Adds a listing block."""
    possible_variations = {
        "listing_view": "listing",
        "summary_view": "summary",
        "tabular_view": "listing",
        "full_view": "summary",
        "album_view": "imageGallery",
        "galeria_de_fotos": "imageGallery",
        "galeria_de_albuns": "imageGallery",
    }
    if variation := item.get("layout"):
        variation = possible_variations.get(variation)

    if not variation:
        variation = "listing"
    block = {
        "@type": "listing",
        "headline": "",
        "headlineTag": "h2",
        "styles": {},
        "variation": variation,
    }
    blocks.append(block)
    return blocks


BLOCKS_ORIG_TYPE = {
    "Collection": _blocks_collection,
    "Topic": _blocks_collection,
    "Folder": _blocks_folder,
}


def _get_default_blocks(
    type_info: dict, has_image: bool, has_description: bool
) -> list[dict]:
    default_blocks = type_info.get("override_blocks", type_info.get("blocks"))
    blocks = list(default_blocks) if default_blocks else []
    if default_blocks:
        blocks = []
        for block in default_blocks:
            block_type = block["@type"]
            if (block_type == "leadimage" and not has_image) or (
                block_type == "description" and not has_description
            ):
                continue
            blocks.append(block)
    return blocks


async def process_blocks(
    item: t.PloneItem, metadata: t.MetadataInfo, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    type_ = item["@type"]
    has_image = bool(item.get("image"))
    has_description = has_description = bool(
        item.get("description") is not None and item.get("description", "").strip()
    )
    type_info = settings.types.get(type_, {})
    blocks = _get_default_blocks(type_info, has_image, has_description)
    # Blocks defined somewhere else
    item_blocks = item.pop("_blocks_", [])
    if blocks or item_blocks:
        blocks.extend(item_blocks)
        orig_type = item.get("_orig_type", "")
        if processor := BLOCKS_ORIG_TYPE.get(orig_type):
            blocks = processor(item, blocks)
        text = item.get("text", {})
        src = text.get("data", "") if text else ""
        blocks_info = volto_blocks(source=src, default_blocks=blocks)
        item.update(blocks_info)
    yield item
