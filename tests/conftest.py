from collective.transmute import _types as t
from collective.transmute import layout
from pathlib import Path
from typing import Any

import asyncio
import json
import pytest


RESOURCES = Path(__file__).parent / "_resources"


def write_transmute_config(filename: str, dst_path: Path) -> Path:
    path = RESOURCES / "transmute_conf" / filename
    dst = dst_path / "transmute.toml"
    dst.write_text(path.read_text())
    return path


@pytest.fixture(scope="session")
def load_json():
    def func(filepath: str | Path) -> dict:
        path = Path(filepath)
        return json.loads(path.read_text())

    return func


@pytest.fixture(scope="session")
def load_json_resource(load_json):
    def func(filename: str) -> dict:
        path = RESOURCES / filename
        return load_json(path)

    return func


@pytest.fixture(scope="session")
def load_data_file_uid():
    def func(base_path: Path, uid: str) -> dict:
        path_str = f"import/content/{uid}/data.json"
        path = base_path / path_str
        return json.loads(path.read_text())

    return func


@pytest.fixture
def transmute_config() -> str:
    return "complete.toml"


@pytest.fixture(autouse=True)
def test_dir(monkeypatch, tmp_path, transmute_config) -> Path:
    monkeypatch.chdir(tmp_path)
    write_transmute_config(transmute_config, tmp_path)
    return tmp_path


@pytest.fixture
def copy_transmute_config(test_dir):
    def func(filename: str) -> Path:
        return write_transmute_config(filename, test_dir)

    return func


@pytest.fixture
def test_src() -> Path:
    return RESOURCES / "export"


@pytest.fixture
def test_dst(test_dir) -> Path:
    dst = test_dir / "import"
    content = (dst / "content").resolve()
    content.mkdir(parents=True, exist_ok=True)
    return dst


@pytest.fixture
def app_layout() -> layout.ApplicationLayout:
    return layout.TransmuteLayout(title="Test Run")


@pytest.fixture
def src_files(test_src) -> t.SourceFiles:
    from collective.transmute.utils import files as file_utils

    return file_utils.get_src_files(test_src)


@pytest.fixture
def pipeline_state(app_layout, src_files) -> t.PipelineState:
    from collective.transmute.commands.transmute import _create_state

    total = len(src_files.content)
    return _create_state(app_layout, total=total)


@pytest.fixture
def pipeline_runner(
    app_layout, src_files, pipeline_state, copy_transmute_config, test_dst
):
    from collective.transmute.pipeline import pipeline

    def func(
        trasmute_config: str = "complete.toml",
        write_report: bool = False,
    ) -> None:
        # Write transmute configuration
        copy_transmute_config(trasmute_config)
        consoles = app_layout.consoles
        consoles.no_ui = True
        app_layout.update_layout(pipeline_state)
        asyncio.run(
            pipeline(src_files, test_dst, pipeline_state, write_report, consoles)
        )

    return func


@pytest.fixture
def transmute_settings(test_dir) -> t.TransmuteSettings:
    from collective.transmute.settings import get_settings

    return get_settings(test_dir)


@pytest.fixture
def traverse():
    def func(data: dict | list, path: str) -> Any:
        func = None
        path = path.split(":")
        if len(path) == 2:
            func, path = path
        else:
            path = path[0]
        parts = [part for part in path.split("/") if part.strip()]
        value = data
        for part in parts:
            if isinstance(value, list):
                part = int(part)
            value = value[part]
        match func:
            # Add other functions here
            case "len":
                value = len(value)
            case "type":
                # This makes it easier to compare
                value = type(value).__name__
            case "is_uuid4":
                value = len(value) == 32 and value[15] == "4"
            case "keys":
                value = list(value.keys())
        return value

    return func


@pytest.fixture
def blocks_data(load_data_file_uid):
    def func(base_path: Path, uid: str) -> list[dict]:
        data = load_data_file_uid(base_path, uid)
        blocks = data.get("blocks", {})
        layout = data.get("blocks_layout", {}).get("items", [])
        blocks_data = [blocks.get(uid) for uid in layout if uid in blocks]
        return blocks_data

    return func
