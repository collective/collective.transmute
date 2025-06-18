import pytest


@pytest.fixture
def transmute_config() -> str:
    return "bare.toml"


@pytest.mark.parametrize(
    "key,expected",
    [
        ["config.debug", False],
        ["config.report", 5000],
        ["principals.default", "Plone"],
        ["review_state.filter.allowed", ("published",)],
        ["paths.export_prefixes", ("http://localhost:8080/Plone",)],
        ["paths.cleanup", {"/_": "/"}],
        ["images.to_preview_image_link", ()],
        ["paths.filter.allowed", set()],
        ["paths.filter.drop", set()],
        ["types.processor", "collective.transmute.steps.portal_type.default.processor"],
        ["types.Document.portal_type", "Document"],
        ["types.Event.portal_type", "Event"],
        ["types.File.portal_type", "File"],
        ["types.Link.portal_type", "Link"],
        ["types.Folder.portal_type", "Document"],
        ["types.Collection.portal_type", "Document"],
        [
            "types.Collection.processor",
            "collective.transmute.steps.portal_type.collection.processor",
        ],
        ["types.Image.portal_type", "Image"],
        ["types.News Item.portal_type", "News Item"],
        ["types.News Item.blocks", [{"@type": "title"}, {"@type": "description"}]],
        ["default_pages.keep", False],
        ["default_pages.keys_from_parent", ("@id", "id")],
    ],
)
def test_settings_values(transmute_settings, key: str, expected):
    value = transmute_settings
    parts = key.split(".")
    value = getattr(transmute_settings, parts[0])
    for part in parts[1:]:
        value = value.get(part)
    assert value == expected
