import pytest


@pytest.mark.parametrize(
    "key,expected",
    [
        ["config.debug", bool],
        ["config.report", int],
        ["principals.default", str],
        ["principals.remove", tuple],
        ["pipeline.steps", tuple],
        ["pipeline.do_not_add_drop", tuple],
        ["review_state.filter.allowed", tuple],
        ["paths.cleanup", dict],
        ["paths.filter.allowed", set],
        ["paths.filter.drop", set],
    ],
)
def test_settings(transmute_settings, key: str, expected):
    value = transmute_settings
    parts = key.split(".")
    value = getattr(transmute_settings, parts[0])
    for part in parts[1:]:
        value = value.get(part)
    assert isinstance(value, expected)


def test_settings_is_debug_default(transmute_settings):
    assert transmute_settings.is_debug is False
