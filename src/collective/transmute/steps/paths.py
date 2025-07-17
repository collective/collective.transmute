from collective.transmute import _types as t


def _is_valid_path(path: str, allowed: set[str], drop: set[str]) -> bool:
    """Check if path is allowed to be processed."""
    status = True
    for prefix in drop:
        if path.startswith(prefix):
            return False
    if allowed:
        status = False
        for prefix in allowed:
            if path.startswith(prefix):
                return True
    return status


async def process_paths(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    id_ = item["@id"]
    path_filter = settings.paths["filter"]
    allowed = path_filter["allowed"]
    drop = path_filter["drop"]
    if not _is_valid_path(id_, allowed, drop):
        yield None
    else:
        yield item
