from collective.transmute import _types as t


def _merge_items(
    parent_item: t.PloneItem, item: t.PloneItem, keys_from_parent: tuple[str, ...]
) -> t.PloneItem:
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
    """Handle default page by merging parent item into the current item."""
    # If the default page item is a Link, we handle it differently
    item.pop("layout", None)
    remote_url = item.pop("remoteUrl")
    text = {"data": f"<div><a href='{remote_url}'>{remote_url}</a></div>"}
    item["@type"] = "Document"
    item["text"] = text
    return item


def handle_default_page(
    parent_item: t.PloneItem, item: t.PloneItem, keys_from_parent: tuple[str, ...]
) -> t.PloneItem:
    """Handle default page by merging parent item into the current item."""
    portal_type = item.get("@type")
    if portal_type == "Link":
        item = _handle_link(item)
    return _merge_items(parent_item, item, keys_from_parent)
