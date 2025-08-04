from collective.transmute.steps import basic_metadata

import pytest


class TestNoTitle:
    @pytest.fixture(autouse=True)
    def _setup(self, pipeline_state, transmute_settings):
        self.pipeline_state = pipeline_state
        self.settings = transmute_settings
        self.func = basic_metadata.process_no_title

    @pytest.mark.parametrize(
        "idx,item,attr,expected",
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
    async def test_no_title(self, item, idx, attr, expected):
        results = []
        async for processed_item in self.func(item, self.pipeline_state, self.settings):
            results.append(processed_item)

        assert len(results) > idx
        assert results[idx][attr] == expected
