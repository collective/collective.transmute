from collective.transmute.pipeline.pipeline import _add_to_drop

import pytest


@pytest.fixture
def settings_factory(transmute_settings):
    def factory(**overrides):
        settings = transmute_settings
        for key, value in overrides.items():
            parts = key.split(".")
            target = settings
            for part in parts[:-1]:
                target = (
                    target[part] if isinstance(target, dict) else getattr(target, part)
                )
            target[parts[-1]] = value
        return settings

    return factory


@pytest.mark.parametrize(
    "overrides,path,expected",
    [
        ({"paths.filter.allowed": {}}, "/foo/bar/foo", True),
        ({"paths.filter.allowed": {"/foo/bar"}}, "/foo/bar/foo", True),
        ({"paths.filter.allowed": {"/foo/bar"}}, "/bar/bar/foo", False),
    ],
)
def test__add_to_drop(settings_factory, path, overrides, expected):
    """Test _add_to_drop logic."""
    settings = settings_factory(**overrides)
    func = _add_to_drop
    func(path, settings)
    assert (path in settings.paths["filter"]["drop"]) is expected
