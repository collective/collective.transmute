from collective.transmute import _types as t


async def process_title_description(
    item: t.PloneItem, metadata: t.MetadataInfo, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    for field in ("title", "description"):
        cur_value = item.get(field)
        if cur_value is not None:
            item[field] = cur_value.strip()
    yield item
