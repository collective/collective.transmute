from collective.transmute.pipeline import _prepare_report_items

import pytest


@pytest.fixture
def src_item():
    return {
        "filename": "1745.json",
        "src_path": "/my-folder/my-document",
        "src_type": "Document",
        "src_uid": "abc123",
        "src_workflow": "simple_publication_workflow",
        "src_state": "published",
        "src_level": 2,
    }


@pytest.fixture
def processed_item():
    return {
        "@id": "/my-folder/my-document",
        "@type": "Document",
        "UID": "abc123",
        "id": "my-document",
        "review_state": "published",
        "workflow_history": {
            "simple_publication_workflow": [],
        },
    }


@pytest.fixture
def new_child_item():
    return {
        "@id": "/my-folder/my-document/image",
        "@type": "Image",
        "UID": "def456",
        "id": "image",
        "review_state": "published",
        "workflow_history": {
            "simple_publication_workflow": [],
        },
        "_is_new_item": True,
    }


class TestPrepareReportItemsDoesNotMutateSrcItem:
    """Ensure _prepare_report_items does not mutate the original src_item."""

    def test_processed_item(self, src_item, processed_item):
        original = dict(src_item)
        _prepare_report_items(processed_item, "process_blocks", False, src_item)
        assert src_item == original

    def test_dropped_item(self, src_item):
        original = dict(src_item)
        _prepare_report_items(None, "process_paths", False, src_item)
        assert src_item == original

    def test_new_child_item(self, src_item, new_child_item):
        original = dict(src_item)
        _prepare_report_items(new_child_item, "process_blocks", True, src_item)
        assert src_item == original


class TestNewItemPreservesSourceMetadata:
    """New (child) items should carry the parent's source metadata."""

    def test_preserves_src_type(self, src_item, new_child_item):
        report_src, _ = _prepare_report_items(
            new_child_item, "process_blocks", True, src_item
        )
        assert report_src["src_type"] == "Document"

    def test_preserves_src_uid(self, src_item, new_child_item):
        report_src, _ = _prepare_report_items(
            new_child_item, "process_blocks", True, src_item
        )
        assert report_src["src_uid"] == "abc123"

    def test_preserves_src_state(self, src_item, new_child_item):
        report_src, _ = _prepare_report_items(
            new_child_item, "process_blocks", True, src_item
        )
        assert report_src["src_state"] == "published"

    def test_preserves_src_level(self, src_item, new_child_item):
        report_src, _ = _prepare_report_items(
            new_child_item, "process_blocks", True, src_item
        )
        assert report_src["src_level"] == 2

    def test_preserves_filename(self, src_item, new_child_item):
        report_src, _ = _prepare_report_items(
            new_child_item, "process_blocks", True, src_item
        )
        assert report_src["filename"] == "1745.json"

    def test_preserves_src_workflow(self, src_item, new_child_item):
        report_src, _ = _prepare_report_items(
            new_child_item, "process_blocks", True, src_item
        )
        assert report_src["src_workflow"] == "simple_publication_workflow"


class TestMultiYieldPreservesSourceMetadata:
    """Simulates a processor yielding multiple items from one source."""

    def test_second_item_has_correct_src_type(
        self, src_item, new_child_item, processed_item
    ):
        """After processing a new child, the original item's src_type is intact."""
        # First yield: the new child item
        _prepare_report_items(new_child_item, "process_blocks", True, src_item)
        # Second yield: the original (modified) item
        report_src, _ = _prepare_report_items(
            processed_item, "process_blocks", False, src_item
        )
        assert report_src["src_type"] == "Document"

    def test_second_item_has_correct_src_uid(
        self, src_item, new_child_item, processed_item
    ):
        _prepare_report_items(new_child_item, "process_blocks", True, src_item)
        report_src, _ = _prepare_report_items(
            processed_item, "process_blocks", False, src_item
        )
        assert report_src["src_uid"] == "abc123"

    def test_second_item_has_correct_src_state(
        self, src_item, new_child_item, processed_item
    ):
        _prepare_report_items(new_child_item, "process_blocks", True, src_item)
        report_src, _ = _prepare_report_items(
            processed_item, "process_blocks", False, src_item
        )
        assert report_src["src_state"] == "published"
