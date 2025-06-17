import pytest


@pytest.fixture
def transmute_config() -> str:
    return "simple.toml"


@pytest.mark.parametrize(
    "key,expected",
    [
        ["config.debug", True],
        ["config.report", 2000],
        ["principals.default", "User"],
        ["review_state.filter.allowed", ("visible", "published")],
        [
            "paths.export_prefixes",
            ("http://localhost:8080/Plone", "http://staging.foo"),
        ],
        [
            "paths.cleanup",
            {"/foo": "/bar", "/_": "/"},
        ],
        ["images.to_preview_image_link", ("News Item",)],
        ["paths.filter.allowed", {"/bar"}],
        ["paths.filter.drop", {"/bar/hidden", "/bar/hidden2", "/bar/hidden3"}],
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
        [
            "types.News Item.blocks",
            [{"@type": "title"}, {"@type": "leadimage"}, {"@type": "description"}],
        ],
    ],
)
def test_settings_values(transmute_settings, key: str, expected):
    value = transmute_settings
    parts = key.split(".")
    value = getattr(transmute_settings, parts[0])
    for part in parts[1:]:
        value = value.get(part)
    assert value == expected


def test_settings_is_debug(transmute_settings):
    assert transmute_settings.is_debug is True
