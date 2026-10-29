from collective.transmute.settings import get_settings
from collective.transmute.settings.parse import SettingsError

import pytest


@pytest.fixture
def write_converter(test_dir):
    def func(table: str) -> None:
        path = test_dir / "transmute.toml"
        path.write_text(path.read_text() + f"\n[steps.blocks.converter]\n{table}\n")

    return func


def test_converter_default_is_empty(test_dir):
    settings = get_settings(test_dir)
    assert settings.steps["blocks"]["converter"] == {}


@pytest.mark.parametrize(
    "table,expected",
    [
        [
            'codeBlock = { style = "light" }\nslateTable = false',
            {"codeBlock": {"style": "light"}, "slateTable": False},
        ],
        ["codeBlock = true", {"codeBlock": True}],
    ],
)
def test_converter_valid(write_converter, test_dir, table, expected):
    write_converter(table)
    settings = get_settings(test_dir)
    assert settings.steps["blocks"]["converter"] == expected


@pytest.mark.parametrize(
    "table,message",
    [
        ["nope = true", "Unknown block type nope"],
        ["codeBlock = { nope = 1 }", "Unknown option nope for block type codeBlock"],
        [
            "codeBlock = { style = 1 }",
            "Option style of block type codeBlock must be str",
        ],
        ["slate = false", "Block type slate cannot be disabled"],
        ['codeBlock = "light"', "must be true, false or a dict of options"],
    ],
)
def test_converter_invalid_stops_settings(write_converter, test_dir, table, message):
    write_converter(table)
    with pytest.raises(SettingsError, match=message) as exc:
        get_settings(test_dir)
    assert "transmute.toml" in str(exc.value)
