from collective.transmute.steps import basic_metadata

import pytest


@pytest.mark.parametrize(
    "idx,base_item,attr,expected",
    [
        [
            0,
            {
                "@id": "/Plone/mein_pfad/PortableNetworkGraphics.png",
                "@type": "Image",
                "UID": "8db21fe29aba466abfb20278144ce9cf",
                "id": "PortableNetworkGraphics.png",
                "title": "",
                "image": {
                    "content-type": "image/png",
                    "encoding": "base64",
                    "filename": "Portable Network Graphics.png",
                    "blob_path": "",
                },
            },
            "title",
            "Portable Network Graphics.png",
        ],
        [
            0,
            {
                "@id": "/Plone/mein_pfad/AdobePortableDocumentFormat.pdf",
                "@type": "File",
                "UID": "8db21fe29aba466abfb20278144ce9cf",
                "id": "AdobePortableDocumentFormat.pdf",
                "title": "",
                "file": {
                    "content-type": "application/pdf",
                    "encoding": "base64",
                    "filename": "Adobe Portable Document Format.pdf",
                    "blob_path": "",
                },
            },
            "title",
            "Adobe Portable Document Format.pdf",
        ],
        [
            0,
            {
                "@id": "/Plone/mein_pfad/PortableNetworkGraphics.png",
                "@type": "Image",
                "UID": "8db21fe29aba466abfb20278144ce9cf",
                "id": "PortableNetworkGraphics.png",
                "title": "",
            },
            "title",
            "PortableNetworkGraphics.png",
        ],
    ],
)
async def test_process_title(
    pipeline_state, transmute_settings, base_item, idx, attr, expected
):
    results = []
    async for item in basic_metadata.process_title(
        base_item, pipeline_state, transmute_settings
    ):
        results.append(item)

    assert len(results) > idx
    assert results[idx][attr] == expected
