from collective.transmute import _types as t
from collective.transmute.utils import item as utils


def get_conversion_types(settings: t.TransmuteSettings) -> tuple[str, ...]:
    """Content types that will have the image to preview_image_link conversion."""
    return settings.images["to_preview_image_link"]


async def process_image_to_preview_image_link(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    type_ = item["@type"]
    metadata = state.metadata
    if type_ not in get_conversion_types(settings):
        yield item
    else:
        image = item.get("image", None)
        if isinstance(image, dict) and metadata:
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
