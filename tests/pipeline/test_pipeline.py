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
        ("import/content/32a753eb768f1fb942a0b30536011c65/data.json", True),
    ],
)
def test_pipeline_results(pipeline_result, filename: str, expected: bool):
    """Test pipeline execution."""
    path = (pipeline_result / filename).resolve()
    assert path.exists() is expected


@pytest.mark.parametrize(
    "filename,path,expected",
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
        (
            "import/content/32a753eb768f1fb942a0b30536011c65/data.json",
            "@id",
            "/my-folder/my-subfolder/recent",
        ),
    ],
)
def test_pipeline_results_values(
    pipeline_result, load_json, traverse, filename: str, path: str, expected: str
):
    """Test pipeline execution."""
    data = load_json((pipeline_result / filename).resolve())
    value = traverse(data, path)
    assert value == expected, f"{value} != {expected}"


@pytest.mark.parametrize(
    "uid,path,expected",
    [
        ("32a753eb768f1fb942a0b30536011c65", "0/@type", "title"),
        ("32a753eb768f1fb942a0b30536011c65", "1/@type", "listing"),
        ("32a753eb768f1fb942a0b30536011c65", "1/b_size", 10),
        ("32a753eb768f1fb942a0b30536011c65", "1/headline", ""),
        ("32a753eb768f1fb942a0b30536011c65", "1/headlineTag", "h2"),
        ("32a753eb768f1fb942a0b30536011c65", "1/limit", 1000),
        ("32a753eb768f1fb942a0b30536011c65", "1/querystring/sort_on", "modified"),
        ("32a753eb768f1fb942a0b30536011c65", "1/querystring/sort_order", "descending"),
        ("32a753eb768f1fb942a0b30536011c65", "1/querystring/sort_order_boolean", True),
        # Fix path value (UID to path)
        (
            "32a753eb768f1fb942a0b30536011c65",
            "1/querystring/query/2/v",
            "/my-folder/my-subfolder",
        ),
        # Remove duplicated items
        ("32a753eb768f1fb942a0b30536011c65", "len:1/querystring/query/1/v", 4),
        # Handle date between operation
        ("42a753eb768f1fb942a0b30536011c65", "1/querystring/query/1/i", "effective"),
        (
            "42a753eb768f1fb942a0b30536011c65",
            "1/querystring/query/1/o",
            "plone.app.querystring.operation.date.largerThan",
        ),
        (
            "42a753eb768f1fb942a0b30536011c65",
            "1/querystring/query/1/v",
            "2014-03-26T23:00:00+00:00",
        ),
    ],
)
def test_pipeline_results_blocks(
    pipeline_result, blocks_data, traverse, uid: str, path: str, expected: str
):
    """Test pipeline execution."""
    data = blocks_data(pipeline_result, uid)
    value = traverse(data, path)
    assert value == expected, f"{value} != {expected}"
