from collective.transmute import _types as t
from collective.transmute.utils.default_page import handle_default_page


async def process_default_page(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    metadata = state.metadata
    item_uid = item["UID"]
    if metadata:
        if parent_item := metadata.__processing_default_page__.pop(item_uid, None):
            parent_uid = parent_item["UID"]
            keys_from_parent = settings.default_pages["keys_from_parent"]
            item = handle_default_page(parent_item, item, keys_from_parent)
            metadata.__fix_relations__[item_uid] = parent_uid
            yield item
        elif default_page_uid := metadata.default_page.pop(item_uid, None):
            metadata.__processing_default_page__[default_page_uid] = item
            yield None
        else:
            yield item
    else:
        # If no metadata, we cannot process default pages
        yield item
