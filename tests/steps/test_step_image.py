from collective.transmute.steps import image

import pytest


@pytest.fixture
def patch_settings(monkeypatch):
    monkeypatch.setattr(image, "get_conversion_types", lambda x: ["News Item"])


@pytest.fixture
def base_news_item(load_json_resource) -> dict:
    return load_json_resource("image/news_item.json")


@pytest.fixture
def preview_image_news_item(base_news_item) -> dict:
    """News item whose image data lives in ``preview_image`` instead of ``image``."""
    item = dict(base_news_item)
    item["preview_image"] = item.pop("image")
    item["preview_image_caption"] = item.pop("image_caption")
    return item


class TestImageToPreviewLink:
    @pytest.fixture(autouse=True)
    def _setup(self, pipeline_state, patch_settings, transmute_settings):
        self.pipeline_state = pipeline_state
        self.settings = transmute_settings
        self.func = image.process_image_to_preview_image_link

    @pytest.mark.parametrize(
        "idx,attr,expected",
        [
            [0, "@type", "Image"],
            [0, "@id", "/Plone/noticias/2016/03/uma-noticia/imagem.jpg"],
            [0, "id", "imagem.jpg"],
            [0, "title", "imagem.jpg"],
            [0, "image_caption", "An Image"],
            [1, "@type", "News Item"],
            [1, "@id", "/Plone/noticias/2016/03/uma-noticia"],
        ],
    )
    async def test_create_image_item(
        self, base_news_item, idx: int, attr: str, expected: str
    ):
        results = []
        async for item in self.func(base_news_item, self.pipeline_state, self.settings):
            results.append(item)
        assert results[idx][attr] == expected

    @pytest.mark.parametrize(
        "idx,attr,expected",
        [
            [0, "image_caption", True],
            [0, "image", True],
            [1, "image_caption", False],
            [1, "image", False],
        ],
    )
    async def test_attribute_exists(
        self, base_news_item, idx: int, attr: str, expected: bool
    ):
        results = []
        async for item in self.func(base_news_item, self.pipeline_state, self.settings):
            results.append(item)
        assert (attr in results[idx]) is expected

    async def test_relation_created(self, base_news_item):
        metadata = self.pipeline_state.metadata
        total_relations = len(metadata.relations)
        results = []
        async for item in self.func(base_news_item, self.pipeline_state, self.settings):
            results.append(item)
        relations = metadata.relations
        assert len(relations) == total_relations + 1
        relation = relations[-1]
        assert relation["from_attribute"] == "preview_image_link"
        assert relation["from_uuid"] == results[1]["UID"]
        assert relation["to_uuid"] == results[0]["UID"]


class TestImageToPreviewLinkNoSettings:
    @pytest.fixture(autouse=True)
    def _setup(self, pipeline_state, transmute_settings):
        self.pipeline_state = pipeline_state
        self.settings = transmute_settings
        self.func = image.process_image_to_preview_image_link

    @pytest.mark.parametrize(
        "idx,attr,expected",
        [
            [0, "@type", "News Item"],
            [0, "@id", "/Plone/noticias/2016/03/uma-noticia"],
        ],
    )
    async def test_create_image_item(
        self, base_news_item, idx: int, attr: str, expected: str
    ):
        results = []
        async for item in self.func(base_news_item, self.pipeline_state, self.settings):
            results.append(item)
        assert len(results) == 1
        assert results[idx][attr] == expected

    @pytest.mark.parametrize(
        "idx,attr,expected",
        [
            [0, "image", True],
            [0, "image_caption", True],
        ],
    )
    async def test_attribute_exists(
        self, base_news_item, idx: int, attr: str, expected: bool
    ):
        results = []
        async for item in self.func(base_news_item, self.pipeline_state, self.settings):
            results.append(item)
        assert (attr in results[idx]) is expected

    async def test_relation_not_created(self, base_news_item):
        metadata = self.pipeline_state.metadata
        total_relations = len(metadata.relations)
        results = []
        async for item in self.func(base_news_item, self.pipeline_state, self.settings):
            results.append(item)
        relations = metadata.relations
        assert len(relations) == total_relations


class TestPreviewImageToPreviewLink:
    @pytest.fixture(autouse=True)
    def _setup(self, pipeline_state, patch_settings, transmute_settings):
        self.pipeline_state = pipeline_state
        self.settings = transmute_settings
        self.func = image.process_image_to_preview_image_link

    @pytest.mark.parametrize(
        "idx,attr,expected",
        [
            [0, "@type", "Image"],
            [0, "@id", "/Plone/noticias/2016/03/uma-noticia/imagem.jpg"],
            [0, "id", "imagem.jpg"],
            [0, "title", "imagem.jpg"],
            [0, "image_caption", "An Image"],
            [1, "@type", "News Item"],
            [1, "@id", "/Plone/noticias/2016/03/uma-noticia"],
        ],
    )
    async def test_create_image_item(
        self, preview_image_news_item, idx: int, attr: str, expected: str
    ):
        results = []
        async for item in self.func(
            preview_image_news_item, self.pipeline_state, self.settings
        ):
            results.append(item)
        assert results[idx][attr] == expected

    @pytest.mark.parametrize(
        "idx,attr,expected",
        [
            [0, "image", True],
            [0, "image_caption", True],
            [1, "preview_image", False],
            [1, "preview_image_caption", False],
        ],
    )
    async def test_attribute_exists(
        self, preview_image_news_item, idx: int, attr: str, expected: bool
    ):
        results = []
        async for item in self.func(
            preview_image_news_item, self.pipeline_state, self.settings
        ):
            results.append(item)
        assert (attr in results[idx]) is expected

    async def test_relation_created(self, preview_image_news_item):
        metadata = self.pipeline_state.metadata
        total_relations = len(metadata.relations)
        results = []
        async for item in self.func(
            preview_image_news_item, self.pipeline_state, self.settings
        ):
            results.append(item)
        relations = metadata.relations
        assert len(relations) == total_relations + 1
        relation = relations[-1]
        assert relation["from_attribute"] == "preview_image_link"
        assert relation["from_uuid"] == results[1]["UID"]
        assert relation["to_uuid"] == results[0]["UID"]

    async def test_preview_image_takes_precedence(self, preview_image_news_item):
        # Both fields present: preview_image must be the one converted.
        preview_image_news_item["image"] = {
            "content-type": "image/jpeg",
            "data": "other-image",
            "encoding": "base64",
            "filename": "outro.jpg",
        }
        preview_image_news_item["image_caption"] = "Another Image"
        results = []
        async for item in self.func(
            preview_image_news_item, self.pipeline_state, self.settings
        ):
            results.append(item)
        # Created Image comes from preview_image (imagem.jpg), not image (outro.jpg).
        assert results[0]["id"] == "imagem.jpg"
        assert results[0]["image_caption"] == "An Image"
        # Both source fields are stripped from the original item.
        original = results[1]
        assert "image" not in original
        assert "image_caption" not in original
        assert "preview_image" not in original
        assert "preview_image_caption" not in original


class TestCleanupImageFields:
    def test_removes_all_image_fields(self):
        item = {
            "@type": "News Item",
            "title": "Keep me",
            "image": {"filename": "a.jpg"},
            "image_caption": "caption",
            "preview_image": {"filename": "b.jpg"},
            "preview_image_caption": "another caption",
        }
        result = image.cleanup_image_fields(item)
        assert "image" not in result
        assert "image_caption" not in result
        assert "preview_image" not in result
        assert "preview_image_caption" not in result
        assert result["title"] == "Keep me"

    def test_returns_same_object(self):
        item = {"@type": "News Item"}
        assert image.cleanup_image_fields(item) is item

    def test_noop_when_no_image_fields(self):
        item = {"@type": "News Item", "title": "x"}
        assert image.cleanup_image_fields(item) == {
            "@type": "News Item",
            "title": "x",
        }
