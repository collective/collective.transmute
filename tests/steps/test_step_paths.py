from collective.transmute.steps import paths

import pytest


@pytest.fixture
def patch_paths_filter(monkeypatch, transmute_settings):
    """Return a helper to inject allowed/drop lists into settings."""

    def _patch(allowed: list[str], drop: list[str]):
        transmute_settings.paths["filter"] = {"allowed": allowed, "drop": drop}
        return transmute_settings

    return _patch


@pytest.fixture
def base_item() -> dict:
    return {
        "@id": "/my-folder/my-document",
        "@type": "Document",
        "UID": "abc123",
        "id": "my-document",
    }


class TestIsValidPath:
    def test_no_filters_allows(self):
        dropped = {}
        assert paths._is_valid_path("/anything", set(), set(), dropped) is True

    def test_drop_prefix_blocks(self):
        dropped = {}
        dropped.setdefault("/private", 0)
        assert (
            paths._is_valid_path("/private/foo", set(), {"/private"}, dropped) is False
        )
        assert dropped["/private"] == 1

    def test_allowed_prefix_passes(self):
        dropped = {}
        assert paths._is_valid_path("/public/foo", {"/public"}, set(), dropped) is True

    def test_not_in_allowed_blocked(self):
        dropped = {}
        assert paths._is_valid_path("/other", {"/public"}, set(), dropped) is False

    def test_drop_checked_before_allowed(self):
        dropped = {}
        dropped.setdefault("/public/private", 0)
        # path matches allowed /public but also drop /public/private
        result = paths._is_valid_path(
            "/public/private/item", {"/public"}, {"/public/private"}, dropped
        )
        assert result is False
        assert dropped["/public/private"] == 1


class TestProcessPathsNoFilters:
    async def test_keeps_item_when_no_filters(
        self, base_item, pipeline_state, patch_paths_filter
    ):
        settings = patch_paths_filter([], [])
        results = []
        async for item in paths.process_paths(base_item, pipeline_state, settings):
            results.append(item)
        assert results == [base_item]


class TestProcessPathsAllowed:
    async def test_keeps_matching_path(
        self, base_item, pipeline_state, patch_paths_filter
    ):
        settings = patch_paths_filter(["/my-folder"], [])
        results = []
        async for item in paths.process_paths(base_item, pipeline_state, settings):
            results.append(item)
        assert results == [base_item]

    async def test_drops_non_matching_path(
        self, base_item, pipeline_state, patch_paths_filter
    ):
        settings = patch_paths_filter(["/other"], [])
        results = []
        async for item in paths.process_paths(base_item, pipeline_state, settings):
            results.append(item)
        assert results == [None]


class TestProcessPathsDrop:
    async def test_drops_matching_prefix(
        self, base_item, pipeline_state, patch_paths_filter
    ):
        settings = patch_paths_filter([], ["/my-folder"])
        results = []
        async for item in paths.process_paths(base_item, pipeline_state, settings):
            results.append(item)
        assert results == [None]

    async def test_tracks_dropped_count(
        self, base_item, pipeline_state, patch_paths_filter
    ):
        settings = patch_paths_filter([], ["/my-folder"])
        async for _ in paths.process_paths(base_item, pipeline_state, settings):
            pass
        dropped = pipeline_state.annotations["dropped_by_path_prefix"]
        assert dropped["/my-folder"] == 1


class TestProcessPathsAnnotationInitialization:
    async def test_creates_annotation_if_missing(
        self, base_item, pipeline_state, patch_paths_filter
    ):
        settings = patch_paths_filter([], [])
        assert "dropped_by_path_prefix" not in pipeline_state.annotations
        async for _ in paths.process_paths(base_item, pipeline_state, settings):
            pass
        assert "dropped_by_path_prefix" in pipeline_state.annotations
