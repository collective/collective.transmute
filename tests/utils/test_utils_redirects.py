from collections.abc import Generator
from collective.transmute import _types as t
from collective.transmute.utils import redirects as utils

import pytest


@pytest.fixture
def patched_settings(transmute_settings) -> Generator[t.TransmuteSettings, None, None]:
    orig = transmute_settings.site_root["src"]
    transmute_settings.site_root["src"] = "/ifpb"
    yield transmute_settings
    transmute_settings.site_root["src"] = orig


@pytest.fixture
def source_redirects(load_json_resource) -> dict[str, str]:
    return load_json_resource("export_redirects.json")


@pytest.fixture
def redirects(patched_settings, source_redirects) -> dict[str, str]:
    func = utils.initialize_redirects
    return func(source_redirects, settings=patched_settings)


def test_initialize_redirects(patched_settings, source_redirects):
    func = utils.initialize_redirects
    result = func(source_redirects, settings=patched_settings)
    assert len(result) == 3
    keys = [k for k in list(result.keys()) if k.startswith("/Plone/")]
    assert len(keys) == 3
    values = [k for k in list(result.values()) if k.startswith("/Plone/")]
    assert len(values) == 3


@pytest.mark.parametrize(
    "src,dest,expected_src,expected_dest",
    [
        ("/foo/bar", "/bar/foo", "/Plone/foo/bar", "/Plone/bar/foo"),
        ("/Plone/foo/bar", "/bar/foo", "/Plone/foo/bar", "/Plone/bar/foo"),
        ("/Plone/foo/bar", "/Plone/bar/foo", "/Plone/foo/bar", "/Plone/bar/foo"),
    ],
)
def test_add_redirect(
    patched_settings, redirects, src, dest, expected_src, expected_dest
):
    site_root = patched_settings.site_root["dest"]
    func = utils.add_redirect
    func(redirects, src, dest, site_root)

    assert len(redirects) == 4
    keys = [k for k in list(redirects.keys()) if k.startswith("/Plone/")]
    assert len(keys) == 4
    assert expected_src in keys
    values = [k for k in list(redirects.values()) if k.startswith("/Plone/")]
    assert len(values) == 4
    assert expected_dest in values


@pytest.mark.parametrize(
    "valid_paths,expected_count",
    [
        ({"/Plone/foo/bar", "/Plone/assuntos/concurso-publico"}, 1),
    ],
)
def test_filter_redirects(redirects, valid_paths, expected_count):
    func = utils.filter_redirects
    result = func(redirects, valid_paths)

    assert len(result) == expected_count
