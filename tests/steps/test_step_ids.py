from collective.transmute.steps import ids

import pytest


@pytest.mark.parametrize(
    "base_item,path",
    [
        [{"@id": "http://localhost:8080/Plone/foo"}, "/foo"],
        [{"@id": "http://localhost:8080/Plone/ foo"}, "/ foo"],
    ],
)
async def test_process_export_prefix(
    pipeline_state, transmute_settings, base_item, path: str
):
    results = []
    async for item in ids.process_export_prefix(
        base_item, pipeline_state, transmute_settings
    ):
        results.append(item)
    assert len(results) == 1
    result = results[0]
    assert result["@id"] == path


@pytest.mark.parametrize(
    "base_item,path,id_",
    [
        [{"@id": "/foo", "id": "foo"}, "/foo", "foo"],
        [{"@id": "/%20foo", "id": " foo"}, "/foo", "foo"],
        [{"@id": "/ foo", "id": " foo"}, "/foo", "foo"],
        [{"@id": "/-foo", "id": "-foo"}, "/foo", "foo"],
        [{"@id": "/_foo", "id": "_foo"}, "/foo", "foo"],
        [
            {"@id": "/Boletins%20de%20Servico", "id": "Boletins%20de%20Servico"},
            "/Boletins_de_Servico",
            "Boletins_de_Servico",
        ],
        [{"@id": "/foo/bar foo/foo", "id": "foo"}, "/foo/bar_foo/foo", "foo"],
        [
            {"@id": "/_foo bar", "id": "_foo bar"},
            "/foo_bar",
            "foo_bar",
        ],
    ],
)
async def test_process_ids(
    pipeline_state, transmute_settings, base_item, path: str, id_: str
):
    results = []
    async for item in ids.process_ids(base_item, pipeline_state, transmute_settings):
        results.append(item)
    assert len(results) == 1
    result = results[0]
    assert result["@id"] == path
    assert result["id"] == id_


@pytest.mark.parametrize(
    "id_,expected",
    [
        [" foo ", "foo"],
        ["__ foo __", "foo"],
        ["_document", "document"],
        ["file with spaces.docx", "file_with_spaces.docx"],
        ["foo-", "foo"],
    ],
)
def test_fix_short_id(id_: str, expected: str):
    result = ids.fix_short_id(id_)
    assert result == expected
