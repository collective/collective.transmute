from collective.transmute.steps import constraints
from collective.transmute.utils import portal_types

import pytest


@pytest.fixture
def patch_portal_type(monkeypatch):
    """Replace fix_portal_type with a simple identity-like mapping."""
    mapping = {
        "Document": "Document",
        "File": "File",
        "News Item": "News Item",
        "Folder": "Document",
        "Topic": "Document",
        "": "",
    }

    def fake(type_: str) -> str:
        return mapping.get(type_, type_)

    monkeypatch.setattr(portal_types, "fix_portal_type", fake)
    monkeypatch.setattr(constraints, "fix_portal_type", fake)


@pytest.fixture
def base_item() -> dict:
    return {
        "@id": "/my-folder",
        "@type": "Folder",
        "UID": "abc123",
        "id": "my-folder",
    }


class TestProcessConstraintsNoConstraints:
    async def test_item_without_constraints(
        self, base_item, pipeline_state, transmute_settings, patch_portal_type
    ):
        results = []
        async for item in constraints.process_constraints(
            base_item, pipeline_state, transmute_settings
        ):
            results.append(item)
        assert results == [base_item]
        assert "exportimport.constrains" not in results[0]


class TestProcessConstraintsWithConstraints:
    async def test_normalizes_constraint_types(
        self, base_item, pipeline_state, transmute_settings, patch_portal_type
    ):
        base_item["exportimport.constrains"] = {
            "locally_allowed_types": ["Document", "File"],
            "immediately_addable_types": ["Document"],
        }
        results = []
        async for item in constraints.process_constraints(
            base_item, pipeline_state, transmute_settings
        ):
            results.append(item)
        result = results[0]
        assert "exportimport.constrains" in result
        assert set(result["exportimport.constrains"]["locally_allowed_types"]) == {
            "Document",
            "File",
        }
        assert result["exportimport.constrains"]["immediately_addable_types"] == [
            "Document"
        ]

    async def test_removes_empty_string_values(
        self, base_item, pipeline_state, transmute_settings, patch_portal_type
    ):
        base_item["exportimport.constrains"] = {
            "locally_allowed_types": ["Document", "", "File"],
        }
        results = []
        async for item in constraints.process_constraints(
            base_item, pipeline_state, transmute_settings
        ):
            results.append(item)
        allowed = results[0]["exportimport.constrains"]["locally_allowed_types"]
        assert "" not in allowed
        assert set(allowed) == {"Document", "File"}

    async def test_deduplicates_values(
        self, base_item, pipeline_state, transmute_settings, patch_portal_type
    ):
        base_item["exportimport.constrains"] = {
            "locally_allowed_types": ["Folder", "Topic"],  # both map to Document
        }
        results = []
        async for item in constraints.process_constraints(
            base_item, pipeline_state, transmute_settings
        ):
            results.append(item)
        allowed = results[0]["exportimport.constrains"]["locally_allowed_types"]
        assert allowed == ["Document"]
