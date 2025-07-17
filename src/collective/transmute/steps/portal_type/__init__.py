from collective.transmute import _types as t
from collective.transmute.utils import load_processor


_PROCESSORS: dict[str, t.ItemProcessor] = {}


async def _pre_process(
    item: t.PloneItem, settings: t.TransmuteSettings, state: t.PipelineState
) -> t.PloneItemGenerator:
    """Pre-process an item."""
    type_ = item["@type"]
    processor = _PROCESSORS.get(type_)
    if not processor:
        # Load the processor for the type
        processor = load_processor(type_, settings)
        _PROCESSORS[type_] = processor
    async for processed in processor(item, state):
        yield processed


async def process_type(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    types = settings.types
    types_path = settings.paths.get("portal_type", {})
    async for processed in _pre_process(item, settings, state):
        if processed:
            id_ = processed["@id"]
            type_ = processed["@type"]
            # Get the new type mapping
            new_type = types.get(type_, {}).get("portal_type")
            # Check if we have a specific mapping via type
            new_type = types_path.get(id_, new_type)
            if not new_type:
                # Dropping content
                yield None
            else:
                processed["@type"] = new_type
                processed["_orig_type"] = type_
                yield processed
        else:
            # If the item is None, we yield None
            yield None
