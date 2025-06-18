from collective.transmute import _types as t


_DROP_KEYS: dict[bool, set[str]] = {}


def get_drop_keys(has_blocks: bool, settings: t.TransmuteSettings) -> set[str]:
    if has_blocks not in _DROP_KEYS:
        drop_keys: set[str] = set(settings.sanitize["drop_keys"])
        if has_blocks:
            block_keys: set[str] = set(settings.sanitize["block_keys"])
            drop_keys = drop_keys | block_keys
        _DROP_KEYS[has_blocks] = drop_keys
    return _DROP_KEYS[has_blocks]


async def process_cleanup(
    item: t.PloneItem, metadata: t.MetadataInfo, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    has_blocks = "blocks" in item
    drop_keys = get_drop_keys(has_blocks, settings)
    item = {k: v for k, v in item.items() if k not in drop_keys}
    yield item
