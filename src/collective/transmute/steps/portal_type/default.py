from collective.transmute import _types as t


async def processor(item: t.PloneItem, state: t.PipelineState) -> t.PloneItemGenerator:
    """Process a PloneItem."""
    yield item
