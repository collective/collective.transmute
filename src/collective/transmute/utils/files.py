from aiofiles.os import makedirs
from base64 import b64decode
from collections.abc import Generator
from collections.abc import Iterator
from collective.transmute import _types as t
from collective.transmute import logger
from collective.transmute import settings
from collective.transmute.utils import exportimport as ei_utils
from pathlib import Path

import aiofiles
import json
import orjson
import shutil


SUFFIX = ".json"


def json_dumps(data: dict | list) -> bytes:
    """Dump to JSON."""
    try:
        # Handles recursion of 255 levels
        response: bytes = orjson.dumps(data, option=orjson.OPT_INDENT_2)
    except orjson.JSONEncodeError:
        response = json.dumps(data, indent=2).encode("utf-8")
    return response


async def json_dump(data: dict | list, path: Path) -> Path:
    """Dump JSON to file."""
    async with aiofiles.open(path, "wb") as f:
        await f.write(json_dumps(data))
    return path


def check_path(path: Path) -> bool:
    """Check if path exists."""
    path = path.resolve()
    return path.exists()


def _sort_content_files(content: list[Path]) -> list[Path]:
    """Order files"""

    def key(filepath: Path) -> str:
        name, _ = filepath.name.split(".")
        return f"{int(name):07d}"

    result = sorted(content, key=lambda x: key(x))
    return result


def get_src_files(src: Path) -> t.SourceFiles:
    """Return a list of files in the src directory."""
    metadata = []
    content = []
    for filepath in src.glob("**/*.json"):
        filepath = filepath.resolve()
        name = filepath.name
        if name.startswith("export_") or name in ("errors.json", "paths.json"):
            metadata.append(filepath)
        else:
            content.append(filepath)
    content = _sort_content_files(content)
    return t.SourceFiles(metadata, content)


async def json_reader(files: Iterator):
    for filepath in files:
        filename = filepath.name
        async with aiofiles.open(filepath, "rb") as f:
            data = await f.read()
            yield filename, orjson.loads(data.decode("utf-8"))


async def export_blob(field: str, blob: dict, content_path: Path, item_id: str) -> dict:
    await makedirs(content_path / field, exist_ok=True)
    filename = blob["filename"] or item_id
    data = b64decode(blob.pop("data").encode("utf-8"))
    filepath: Path = content_path / field / filename
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(data)
    blob["blob_path"] = f"{filepath.relative_to(content_path.parent)}"
    return blob


async def export_item(item: dict, parent_folder: Path) -> t.ItemFiles:
    """Given an item, write to the final destination."""
    # Return blobs created here
    blob_files = []
    uid = item.get("UID")
    item_id = item.get("id")
    blobs = item.pop("_blob_files_")
    # TODO: Handle default content for portal
    content_folder = parent_folder / f"{uid}"
    data_path: Path = content_folder / "data.json"
    if blobs:
        for field, value in blobs.items():
            blob = await export_blob(field, value, content_folder, item_id)
            blob_files.append(blob["blob_path"])
            item[field] = blob
    else:
        await makedirs(content_folder, exist_ok=True)
    # Remove internal keys
    item = {key: value for key, value in item.items() if not key.startswith("_")}
    async with aiofiles.open(data_path, "wb") as f:
        await f.write(json_dumps(item))
    return t.ItemFiles(f"{data_path.relative_to(parent_folder)}", blob_files)


async def export_metadata(metadata: t.MetadataInfo) -> Path:
    """Export metadata."""
    async for data, path in ei_utils.prepare_metadata_file(metadata, settings.is_debug):
        async with aiofiles.open(path, "wb") as f:
            await f.write(json_dumps(data))
            logger.debug(f"Wrote {path}")
    return path


def remove_data(path: Path):
    """Remove all data inside a given path."""
    logger.info(f"Removing all content in {path}")
    contents: Generator[Path] = path.glob("*")
    for content in contents:
        if content.is_dir():
            shutil.rmtree(content, True)
            logger.debug(f" - Removed directory {content}")
        else:
            content.unlink()
            logger.debug(f" - Removed file {content}")
