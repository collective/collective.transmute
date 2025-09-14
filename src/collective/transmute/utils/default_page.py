"""
Default page utilities for ``collective.transmute``.

This module provides helper functions for handling and merging default page items
in the transformation pipeline. Functions here are designed to support merging parent
item data into default pages, and to handle special cases such as Link types.
Docstrings and type annotations are provided for Sphinx autodoc.
"""

from collective.transmute import _types as t


def _merge_items(
    parent_item: t.PloneItem, item: t.PloneItem, keys_from_parent: tuple[str, ...]
) -> t.PloneItem:
    """
    Merge selected keys from the parent item into the current item.

    Parameters
    ----------
    parent_item : PloneItem
        The parent item whose keys will be merged.
    item : PloneItem
        The current item to update.
    keys_from_parent : tuple[str, ...]
        Keys to copy from the parent item.

    Returns
    -------
    PloneItem
        The updated item with merged keys and parent UID.
    """
    filtered = {k: v for k, v in parent_item.items() if k in keys_from_parent}
    # Keep old UID here
    parent_item_uid = parent_item["UID"]
    item["_UID"] = str(item.pop("UID"))
    # Populate nav_title from parent title
    current_title = item.get("nav_title", item.get("title", ""))
    item["nav_title"] = parent_item.get("title", current_title)
    item.update(filtered)
    # Enforce parent UID as the current item UID
    item["UID"] = parent_item_uid
    return item


def _handle_link(item: t.PloneItem) -> t.PloneItem:
    """
    Handle default page when the item is a Link type.

    Parameters
    ----------
    item : PloneItem
        The item to process as a Link.

    Returns
    -------
    PloneItem
        The updated item converted to a Document type with link text.
    """
    item.pop("layout", None)
    remote_url = item.pop("remoteUrl")
    text = {
        "data": f"<div><span>Link:<a href='{remote_url}'>{remote_url}</a></span></div>"
    }
    item["@type"] = "Document"
    item["text"] = text
    return item


def handle_default_page(
    parent_item: t.PloneItem, item: t.PloneItem, keys_from_parent: tuple[str, ...]
) -> t.PloneItem:
    """
    Handle default page by merging parent item into the current item.

    If the item is a Link, it is converted to a Document with link text.
    Otherwise, selected keys from the parent are merged into the item.

    Parameters
    ----------
    parent_item : PloneItem
        The parent item whose keys will be merged.
    item : PloneItem
        The current item to update.
    keys_from_parent : tuple[str, ...]
        Keys to copy from the parent item.

    Returns
    -------
    PloneItem
        The updated item with merged keys and parent UID.
    """
    portal_type = item.get("@type")
    if portal_type == "Link":
        item = _handle_link(item)
    return _merge_items(parent_item, item, keys_from_parent)
