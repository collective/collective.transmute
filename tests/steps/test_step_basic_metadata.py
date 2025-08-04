from collective.transmute.steps import basic_metadata

import pytest


@pytest.mark.parametrize(
    "idx,base_item,attr,expected",
    [
        [
            0,
            {
                "@id": "/Plone/mein_pfad/GruppenfotoKlausurtagung780x474.png",
                "@type": "Image",
                "UID": "8db21fe29aba466abfb20278144ce9cf",
                "id": "GruppenfotoKlausurtagung780x474.png",
                "title": "",
                "image": {
                    "content-type": "image/png",
                    "encoding": "base64",
                    "filename": "Gruppenfoto Klausurtagung 780x474.png",
                    "blob_path": "",
                },
            },
            "title",
            "Gruppenfoto Klausurtagung 780x474.png",
        ],
        [
            0,
            {
                "@id": "/Plone/mein_pfad/GruppenfotoKlausurtagung780x474.png",
                "@type": "Image",
                "UID": "8db21fe29aba466abfb20278144ce9cf",
                "id": "GruppenfotoKlausurtagung780x474.png",
                "title": "",
            },
            "title",
            "GruppenfotoKlausurtagung780x474.png",
        ],
    ],
)
async def test_process_no_title(
    pipeline_state, transmute_settings, base_item, idx, attr, expected
):
    results = []
    async for item in basic_metadata.process_no_title(
        base_item, pipeline_state, transmute_settings
    ):
        results.append(item)

    assert len(results) > idx
    assert results[idx][attr] == expected
