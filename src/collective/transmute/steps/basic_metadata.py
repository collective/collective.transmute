from collective.transmute import _types as t


async def process_title_description(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    for field in ("title", "description"):
        cur_value = item.get(field)
        if cur_value is not None:
            item[field] = cur_value.strip()
    yield item


async def process_no_title(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    title = item.get("title", None)
    if not title:
        if blob := item.get("image") or item.get("file"):
            item["title"] = blob["filename"]
        else:
            item["title"] = item["id"]
    yield item
