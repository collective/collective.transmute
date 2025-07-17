from collective.transmute import _types as t


BLOBS_KEYS = [
    "file",
    "image",
]


async def process_blobs(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    item["_blob_files_"] = {}
    for key in BLOBS_KEYS:
        data = item.pop(key, None)
        if not isinstance(data, dict):
            continue
        item["_blob_files_"][key] = data
    yield item
