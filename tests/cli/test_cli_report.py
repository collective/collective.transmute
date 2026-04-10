from collective.transmute import _types as t
from collective.transmute import layout
from collective.transmute.commands.report import _create_report
from collective.transmute.commands.report import _write_type_report

import asyncio
import csv
import pytest


@pytest.fixture
def report_layout() -> layout.ApplicationLayout:
    return layout.ReportLayout(title="Test Report")


@pytest.fixture
def report_state(report_layout, src_files) -> t.ReportState:
    from collective.transmute.commands.report import _create_state

    return _create_state(report_layout, src_files.content)


class TestCreateReport:
    """Tests for _create_report with type reports."""

    def test_type_report_includes_source_file(self, report_state, tmp_path):
        """Type report entries include the source_file field."""
        report_types = ["Folder"]
        asyncio.run(_create_report(tmp_path, report_state, report_types))
        entries = report_state.type_report.get("Folder", [])
        assert len(entries) > 0
        for entry in entries:
            assert "source_file" in entry
            assert entry["source_file"]

    def test_type_report_includes_review_state(self, report_state, tmp_path):
        """Type report entries include the review_state field."""
        report_types = ["Folder"]
        asyncio.run(_create_report(tmp_path, report_state, report_types))
        entries = report_state.type_report.get("Folder", [])
        assert len(entries) > 0
        for entry in entries:
            assert "review_state" in entry
            assert entry["review_state"]

    def test_type_report_entry_keys(self, report_state, tmp_path):
        """Type report entries have all expected keys."""
        expected_keys = {"source_file", "@id", "UID", "@type", "title", "review_state"}
        report_types = ["Folder"]
        asyncio.run(_create_report(tmp_path, report_state, report_types))
        entries = report_state.type_report.get("Folder", [])
        assert len(entries) > 0
        for entry in entries:
            assert set(entry.keys()) == expected_keys


class TestWriteTypeReport:
    """Tests for _write_type_report CSV output."""

    def test_csv_headers(self, report_state, tmp_path):
        """CSV file has the correct headers including source_file and review_state."""
        report_types = ["Folder"]
        asyncio.run(_create_report(tmp_path, report_state, report_types))
        csv_path = asyncio.run(_write_type_report(tmp_path, "Folder", report_state))
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            assert reader.fieldnames == [
                "source_file",
                "@id",
                "UID",
                "@type",
                "title",
                "review_state",
            ]

    def test_csv_source_file_is_first_column(self, report_state, tmp_path):
        """source_file is the first column in the CSV."""
        report_types = ["Folder"]
        asyncio.run(_create_report(tmp_path, report_state, report_types))
        csv_path = asyncio.run(_write_type_report(tmp_path, "Folder", report_state))
        with open(csv_path) as f:
            reader = csv.reader(f)
            headers = next(reader)
            assert headers[0] == "source_file"

    def test_csv_rows_have_source_file_values(self, report_state, tmp_path):
        """Each CSV row has a non-empty source_file value."""
        report_types = ["Folder"]
        asyncio.run(_create_report(tmp_path, report_state, report_types))
        csv_path = asyncio.run(_write_type_report(tmp_path, "Folder", report_state))
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) > 0
            for row in rows:
                assert row["source_file"]

    def test_csv_rows_have_review_state_values(self, report_state, tmp_path):
        """Each CSV row has a non-empty review_state value."""
        report_types = ["Folder"]
        asyncio.run(_create_report(tmp_path, report_state, report_types))
        csv_path = asyncio.run(_write_type_report(tmp_path, "Folder", report_state))
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) > 0
            for row in rows:
                assert row["review_state"]
