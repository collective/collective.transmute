from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "write_report,filename,expected",
    [
        (True, "transmute.toml", True),
        (False, "transmute.toml", True),
        (True, "report_transmute.csv", True),
        (False, "report_transmute.csv", False),
    ],
)
def test_pipeline(
    pipeline_runner, test_dir, write_report: bool, filename: str, expected: bool
):
    """Test pipeline execution."""
    pipeline_runner(write_report=write_report)
    filepath = (test_dir / filename).resolve()
    assert filepath.exists() is expected


@pytest.fixture
def pipeline_result(pipeline_runner, test_dir) -> Path:
    pipeline_runner(write_report=True)
    return test_dir


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("import/relations.json", True),
        ("import/content/__metadata__.json", True),
        ("import/content/cbebd70218b348f68d6bb1b7dd7830c4/data.json", True),
        ("import/content/714cbe2b3fe74c608d4ae20a608eab67/data.json", False),
        ("import/content/2d2db4d11ef58cfb8e2611abb08582f1/data.json", True),
    ],
)
def test_pipeline_results(pipeline_result, filename: str, expected: bool):
    """Test pipeline execution."""
    path = (pipeline_result / filename).resolve()
    assert path.exists() is expected


@pytest.mark.parametrize(
    "filename,key,expected",
    [
        (
            "import/content/cbebd70218b348f68d6bb1b7dd7830c4/data.json",
            "@id",
            "/my-folder",
        ),
        (
            "import/content/cbebd70218b348f68d6bb1b7dd7830c4/data.json",
            "@type",
            "Document",
        ),
        (
            "import/content/cbebd70218b348f68d6bb1b7dd7830c4/data.json",
            "UID",
            "cbebd70218b348f68d6bb1b7dd7830c4",
        ),
        (
            "import/content/2d2db4d11ef58cfb8e2611abb08582f1/data.json",
            "@type",
            "Document",
        ),
        (
            "import/content/2d2db4d11ef58cfb8e2611abb08582f1/data.json",
            "UID",
            "2d2db4d11ef58cfb8e2611abb08582f1",
        ),
        (
            "import/content/2d2db4d11ef58cfb8e2611abb08582f1/data.json",
            "@id",
            "/my-folder/my-subfolder",
        ),
    ],
)
def test_pipeline_results_values(
    pipeline_result, load_json, filename: str, key: str, expected: str
):
    """Test pipeline execution."""
    path = (pipeline_result / filename).resolve()
    data = load_json(path)
    assert data[key] == expected
