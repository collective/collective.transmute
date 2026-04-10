from collective.transmute.steps import uids

import pytest


@pytest.fixture
def base_item() -> dict:
    return {
        "@id": "/my-folder/my-document",
        "@type": "Document",
        "UID": "abc123",
        "id": "my-document",
        "title": "My Document",
    }


class TestDropItemByUidInitialization:
    """The step initializes the drop_uids annotation if missing."""

    async def test_creates_annotation_when_missing(
        self, base_item, pipeline_state, transmute_settings
    ):
        assert "drop_uids" not in pipeline_state.annotations
        results = []
        async for item in uids.drop_item_by_uid(
            base_item, pipeline_state, transmute_settings
        ):
            results.append(item)
        assert "drop_uids" in pipeline_state.annotations


class TestDropItemByUidEmpty:
    """Empty drop list keeps all items."""

    async def test_empty_drop_list_keeps_item(
        self, base_item, pipeline_state, transmute_settings
    ):
        pipeline_state.annotations["drop_uids"] = {}
        results = []
        async for item in uids.drop_item_by_uid(
            base_item, pipeline_state, transmute_settings
        ):
            results.append(item)
        assert results == [base_item]


class TestDropItemByUidMatching:
    """Items whose UID is in the drop list are dropped."""

    async def test_matching_uid_drops_item(
        self, base_item, pipeline_state, transmute_settings
    ):
        pipeline_state.annotations["drop_uids"] = {"abc123": True}
        results = []
        async for item in uids.drop_item_by_uid(
            base_item, pipeline_state, transmute_settings
        ):
            results.append(item)
        assert results == [None]

    async def test_matching_uid_consumes_entry(
        self, base_item, pipeline_state, transmute_settings
    ):
        """The drop list entry is removed after use (pop)."""
        pipeline_state.annotations["drop_uids"] = {"abc123": True}
        async for _ in uids.drop_item_by_uid(
            base_item, pipeline_state, transmute_settings
        ):
            pass
        assert "abc123" not in pipeline_state.annotations["drop_uids"]


class TestDropItemByUidNonMatching:
    """Items whose UID is not in the drop list are kept."""

    async def test_non_matching_uid_keeps_item(
        self, base_item, pipeline_state, transmute_settings
    ):
        pipeline_state.annotations["drop_uids"] = {"other-uid": True}
        results = []
        async for item in uids.drop_item_by_uid(
            base_item, pipeline_state, transmute_settings
        ):
            results.append(item)
        assert results == [base_item]

    async def test_non_matching_leaves_drop_list_intact(
        self, base_item, pipeline_state, transmute_settings
    ):
        pipeline_state.annotations["drop_uids"] = {"other-uid": True}
        async for _ in uids.drop_item_by_uid(
            base_item, pipeline_state, transmute_settings
        ):
            pass
        assert pipeline_state.annotations["drop_uids"] == {"other-uid": True}
