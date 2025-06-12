from collective.transmute import _types as t
from collective.transmute.settings import pb_config
from collective.transmute.utils import item as utils
from functools import cache


@cache
def get_conversion_types() -> list[str]:
    """Content types that will have the image to preview_image_link conversion."""
    return pb_config.images.to_preview_image_link.get("types", [])


async def process_image_to_preview_image_link(
    item: t.PloneItem, metadata: t.MetadataInfo
) -> t.PloneItemGenerator:
    type_ = item["@type"]
    if type_ not in get_conversion_types():
        yield item
    else:
        image = item.get("image", None)
        if isinstance(image, dict):
            image = utils.create_image_from_item(item)
            # Register the relation between the items
            utils.add_relation(item, image, "preview_image_link", metadata)
            # Return the new image
            yield image
            yield item
        else:
            item.pop("image", None)
            item.pop("image_caption", None)
            yield item
