from collective.transmute import _types as t
from collective.transmute.utils.portal_types import fix_portal_type


async def process_constraints(
    item: t.PloneItem, metadata: t.MetadataInfo, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    """Fixes exportimport constraints for an Item."""
    key = "exportimport.constrains"
    if old_constrains := item.pop(key, None):
        constrains = {}
        for c_type, value in old_constrains.items():
            value = {fix_portal_type(v) for v in value}
            # Remove empty value
            if "" in value:
                value.remove("")
            constrains[c_type] = list(value)
        item[key] = constrains
    yield item
