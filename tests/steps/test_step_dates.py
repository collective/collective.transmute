from collective.transmute.steps import dates

import pytest


@pytest.fixture
def patch_filters(monkeypatch):
    """Inject date filters without relying on the cached settings loader."""

    def _patch(filters: tuple[tuple[str, str], ...]):
        monkeypatch.setattr(dates, "_date_filters_from_settings", lambda: filters)

    return _patch


@pytest.fixture
def base_item() -> dict:
    return {
        "@id": "/my-folder/my-document",
        "@type": "Document",
        "UID": "abc123",
        "id": "my-document",
        "title": "My Document",
    }


class TestFilterByDateNoFilters:
    """When no filters are configured, items are always kept."""

    async def test_no_filters_keeps_item(
        self, base_item, pipeline_state, transmute_settings, patch_filters
    ):
        patch_filters(())
        results = []
        async for item in dates.filter_by_date(
            base_item, pipeline_state, transmute_settings
        ):
            results.append(item)
        assert results == [base_item]


class TestFilterByDateKeeps:
    """Items newer than the threshold are kept."""

    @pytest.mark.parametrize(
        "field,threshold,value",
        [
            ("created", "2020-01-01T00:00:00", "2020-06-15T12:00:00"),
            ("modified", "2019-01-01T00:00:00", "2023-11-30T08:45:00"),
            ("effective", "2015-01-01T00:00:00", "2015-01-01T00:00:01"),
        ],
    )
    async def test_newer_item_kept(
        self,
        base_item,
        pipeline_state,
        transmute_settings,
        patch_filters,
        field,
        threshold,
        value,
    ):
        patch_filters(((field, threshold),))
        base_item[field] = value
        results = []
        async for item in dates.filter_by_date(
            base_item, pipeline_state, transmute_settings
        ):
            results.append(item)
        assert results == [base_item]


class TestFilterByDateDrops:
    """Items older than the threshold are dropped."""

    @pytest.mark.parametrize(
        "field,threshold,value",
        [
            ("created", "2020-01-01T00:00:00", "2019-12-31T23:59:59"),
            ("modified", "2019-01-01T00:00:00", "2015-05-15T08:00:00"),
            ("effective", "2015-01-01T00:00:00", "2014-12-31T23:59:59"),
        ],
    )
    async def test_older_item_dropped(
        self,
        base_item,
        pipeline_state,
        transmute_settings,
        patch_filters,
        field,
        threshold,
        value,
    ):
        patch_filters(((field, threshold),))
        base_item[field] = value
        results = []
        async for item in dates.filter_by_date(
            base_item, pipeline_state, transmute_settings
        ):
            results.append(item)
        assert results == [None]


class TestFilterByDateMissingField:
    """Items missing the filter field are kept (no value to compare)."""

    async def test_missing_field_keeps_item(
        self, base_item, pipeline_state, transmute_settings, patch_filters
    ):
        patch_filters((("created", "2020-01-01T00:00:00"),))
        # base_item has no "created" field
        results = []
        async for item in dates.filter_by_date(
            base_item, pipeline_state, transmute_settings
        ):
            results.append(item)
        assert results == [base_item]


class TestFilterByDateMultipleFilters:
    """Multiple filters: any field older than its threshold drops the item."""

    async def test_any_older_field_drops(
        self, base_item, pipeline_state, transmute_settings, patch_filters
    ):
        patch_filters((
            ("created", "2020-01-01T00:00:00"),
            ("modified", "2019-01-01T00:00:00"),
        ))
        base_item["created"] = "2022-01-01T00:00:00"  # newer, ok
        base_item["modified"] = "2010-01-01T00:00:00"  # older, should drop
        results = []
        async for item in dates.filter_by_date(
            base_item, pipeline_state, transmute_settings
        ):
            results.append(item)
        assert results == [None]

    async def test_all_newer_keeps_item(
        self, base_item, pipeline_state, transmute_settings, patch_filters
    ):
        patch_filters((
            ("created", "2020-01-01T00:00:00"),
            ("modified", "2019-01-01T00:00:00"),
        ))
        base_item["created"] = "2022-01-01T00:00:00"
        base_item["modified"] = "2023-01-01T00:00:00"
        results = []
        async for item in dates.filter_by_date(
            base_item, pipeline_state, transmute_settings
        ):
            results.append(item)
        assert results == [base_item]
