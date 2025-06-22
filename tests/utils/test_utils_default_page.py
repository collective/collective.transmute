from collective.transmute.settings import get_settings
from collective.transmute.utils import default_page

import pytest


@pytest.fixture
def item_folder(load_json_resource):
    """Fixture to load a sample item for a folder."""
    return load_json_resource("default_page/folder.json")


@pytest.fixture
def item_document(load_json_resource):
    """Fixture to load a sample item for a document."""
    return load_json_resource("default_page/document.json")


@pytest.fixture
def item_link(load_json_resource):
    """Fixture to load a sample item with a link."""
    return load_json_resource("default_page/link.json")


@pytest.fixture
def keys_from_parent():
    """Fixture to load a sample item with a link."""
    settings = get_settings()
    return settings.default_pages["keys_from_parent"]


@pytest.mark.parametrize(
    "key,exists",
    [
        ("@id", True),
        ("@type", True),
        ("UID", True),
        ("title", True),
        ("remoteUrl", False),
        ("layout", False),
        ("text", True),
    ],
)
def test__handle_link_keys(item_link, key: str, exists: bool):
    """Test that _handle_link returns the expected keys."""
    func = default_page._handle_link
    result = func(item_link)
    assert (key in result) == exists, f"Key '{key}' existence mismatch: {result.keys()}"


@pytest.mark.parametrize(
    "key,expected",
    [
        ("@id", "/ingressos/compre"),
        ("@type", "Document"),
        ("UID", "1bf48fa6bf3843c892ba56a2c54bc5d6"),
        ("title", "Ingressos"),
        (
            "text",
            {
                "data": (
                    "<div><span>Link:<a href='https://pycerrado2025.eventbrite.com.br'>"
                    "https://pycerrado2025.eventbrite.com.br</a></span></div>"
                )
            },
        ),
    ],
)
def test__handle_link_value(item_link, key: str, expected):
    """Test that _handle_link returns the expected values for specific keys."""
    func = default_page._handle_link
    result = func(item_link)
    assert result[key] == expected


@pytest.mark.parametrize(
    "key,expected",
    [
        ("@id", "/ingressos"),
        ("@type", "Document"),
        ("UID", "dbf48fa6bf3843c892ba56a2c54bc5d6"),
        ("_UID", "cbf48fa6bf3843c892ba56a2c54bc5d6"),
        ("title", "Compre Já"),
        (
            "text",
            {"data": "<div><h1>Garanta já o seu ingresso!</h1></div>"},
        ),
    ],
)
def test___merge_items_value(
    item_folder, item_document, keys_from_parent, key: str, expected
):
    """Test that _merge_items returns the expected values for specific keys."""
    func = default_page._merge_items
    result = func(item_folder, item_document, keys_from_parent)
    assert result[key] == expected
