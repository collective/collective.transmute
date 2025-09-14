"""
Pipeline steps for handling Volto blocks in ``collective.transmute``.

This module provides functions and async generator steps for processing, normalizing,
and generating Volto blocks for Plone items in the transformation pipeline. These steps
handle block layouts for collections, folders, and other types, and support block
variation and customization.
"""

from collective.html2blocks.converter import volto_blocks
from collective.transmute import _types as t


def _blocks_collection(
    item: t.PloneItem, blocks: list[t.VoltoBlock]
) -> list[t.VoltoBlock]:
    """
    Add a listing block to a collection or topic item.

    Parameters
    ----------
    item : PloneItem
        The item to process.
    blocks : list[VoltoBlock]
        The list of blocks to append to.

    Returns
    -------
    list[VoltoBlock]
        The updated list of blocks.
    """
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
                "descending" if item.get("sort_reversed") else "ascending"
            )
            querystring["sort_order_boolean"] = bool(item.get("sort_reversed"))

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


def _blocks_folder(item: t.PloneItem, blocks: list[t.VoltoBlock]) -> list[t.VoltoBlock]:
    """
    Add a listing block to a folder item, using possible variations.

    Parameters
    ----------
    item : PloneItem
        The item to process.
    blocks : list[VoltoBlock]
        The list of blocks to append to.

    Returns
    -------
    list[VoltoBlock]
        The updated list of blocks.
    """
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
) -> list[t.VoltoBlock]:
    """
    Get the default blocks for an item type, filtering by image and
    description presence.

    Parameters
    ----------
    type_info : dict
        Type information from settings.
    has_image : bool
        Whether the item has an image.
    has_description : bool
        Whether the item has a description.

    Returns
    -------
    list[VoltoBlock]
        The list of default blocks for the item.
    """
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
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """
    Process and generate Volto blocks for an item, updating its block layout.

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
        The updated item with Volto blocks and blocks_layout.

    Example
    -------
    >>> async for result in process_blocks(item, state, settings):
    ...     print(result['blocks'])
    """
    type_ = item["@type"]
    has_image = bool(item.get("image"))
    has_description = has_description = bool(
        item.get("description") is not None and item.get("description", "").strip()
    )
    type_info = settings.types.get(type_, {})
    blocks = _get_default_blocks(type_info, has_image, has_description)
    additional_blocks: list[t.VoltoBlock] = []
    # Blocks defined somewhere else
    item_blocks: list[t.VoltoBlock] = item.pop("_blocks_", [])
    if blocks or item_blocks:
        blocks.extend(item_blocks)
        orig_type = item.get("_orig_type", type_)
        if processor := BLOCKS_ORIG_TYPE.get(orig_type):
            additional_blocks = processor(item, additional_blocks)
        text = item.get("text", {})
        src = text.get("data", "") if text else ""
        blocks_info = volto_blocks(
            source=src, default_blocks=blocks, additional_blocks=additional_blocks
        )
        item["blocks"], item["blocks_layout"] = (
            blocks_info.get("blocks", {}),
            blocks_info.get("blocks_layout", {}),
        )
    yield item
