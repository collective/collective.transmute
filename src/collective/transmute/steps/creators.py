from collective.transmute import _types as t


async def process_creators(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    """Process list of creators for an item.

    Configuration should be added to transmute.toml

    ```toml
    [principals]
    default='Plone'
    remove=['admin']
    ```
    """
    remove = settings.principals["remove"]
    default = [
        settings.principals["default"],
    ]
    current = item.get("creators", [])
    creators = [creator for creator in current if creator not in remove]
    if not creators:
        creators = default
    item["creators"] = creators
    yield item
