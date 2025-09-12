"""
File utilities for collective.transmute.

This module provides asynchronous and synchronous helper functions for reading,
writing, exporting, and removing files and data structures used in the transformation
pipeline. Functions here support JSON, CSV, and binary blob operations, and are
documented for Sphinx autodoc.
"""

from aiofiles.os import makedirs
from base64 import b64decode
from collections.abc import AsyncGenerator
from collections.abc import Iterable
from collections.abc import Iterator
from collective.transmute import _types as t
from collective.transmute import get_logger
from collective.transmute.utils import exportimport as ei_utils
from pathlib import Path

import aiofiles
import csv
import json
import orjson
import shutil


SUFFIX = ".json"


def json_dumps(data: dict | list) -> bytes:
    """
    Dump a dictionary or list to a JSON-formatted bytes object.

    Parameters
    ----------
    data : dict or list
        The data to serialize to JSON.

    Returns
    -------
    bytes
        The JSON-encoded data as bytes.
    """
    try:
        # Handles recursion of 255 levels
        response: bytes = orjson.dumps(data, option=orjson.OPT_INDENT_2)
    except orjson.JSONEncodeError:
        response = json.dumps(data, indent=2).encode("utf-8")
    return response


async def json_dump(data: dict | list, path: Path) -> Path:
    """
    Dump JSON data to a file asynchronously.

    Parameters
    ----------
    data : dict or list
        The data to serialize and write.
    path : Path
        The file path to write to.

    Returns
    -------
    Path
        The path to the written file.
    """
    async with aiofiles.open(path, "wb") as f:
        await f.write(json_dumps(data))
    return path


async def csv_dump(data: dict | list, header: list[str], path: Path) -> Path:
    """
    Dump data to a CSV file.

    Parameters
    ----------
    data : dict or list
        The data to write to CSV.
    header : list[str]
        The list of column headers.
    path : Path
        The file path to write to.

    Returns
    -------
    Path
        The path to the written CSV file.
    """
    with open(path, "w") as f:
        writer = csv.DictWriter(f, header)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    return path


def check_path(path: Path) -> bool:
    """
    Check if a path exists.

    Parameters
    ----------
    path : Path
        The path to check.

    Returns
    -------
    bool
        True if the path exists, False otherwise.
    """
    path = path.resolve()
    return path.exists()


def check_paths(src: Path, dst: Path) -> bool:
    """
    Check if both source and destination paths exist.

    Parameters
    ----------
    src : Path
        The source path.
    dst : Path
        The destination path.

    Returns
    -------
    bool
        True if both paths exist.

    Raises
    ------
    RuntimeError
        If either path does not exist.
    """
    if not check_path(src):
        raise RuntimeError(f"{src} does not exist")
    if not check_path(dst):
        raise RuntimeError(f"{dst} does not exist")
    return True


def _sort_content_files(content: list[Path]) -> list[Path]:
    """
    Order content files numerically by filename.

    Parameters
    ----------
    content : list[Path]
        List of file paths to sort.

    Returns
    -------
    list[Path]
        Sorted list of file paths.
    """

    def key(filepath: Path) -> str:
        name, _ = filepath.name.split(".")
        return f"{int(name):07d}"

    result = sorted(content, key=lambda x: key(x))
    return result


def get_src_files(src: Path) -> t.SourceFiles:
    """
    Return a SourceFiles object containing metadata and content files from a directory.

    Parameters
    ----------
    src : Path
        The source directory to scan.

    Returns
    -------
    SourceFiles
        An object containing lists of metadata and content files.
    """
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


async def json_reader(
    files: Iterable[Path],
) -> AsyncGenerator[tuple[str, t.PloneItem], None]:
    """
    Asynchronously read JSON files and yield filename and data.

    Parameters
    ----------
    files : Iterable[Path]
        Iterable of file paths to read.

    Yields
    ------
    tuple[str, PloneItem]
        Filename and loaded JSON data.
    """
    for filepath in files:
        filename = filepath.name
        async with aiofiles.open(filepath, "rb") as f:
            data = await f.read()
            yield filename, orjson.loads(data.decode("utf-8"))


async def export_blob(field: str, blob: dict, content_path: Path, item_id: str) -> dict:
    """
    Export a binary blob to disk and update its metadata.

    Parameters
    ----------
    field : str
        The field name for the blob.
    blob : dict
        The blob metadata and data.
    content_path : Path
        The parent content path.
    item_id : str
        The item identifier.

    Returns
    -------
    dict
        The updated blob metadata including the blob path.
    """
    await makedirs(content_path / field, exist_ok=True)
    filename = blob["filename"] or item_id
    data = b64decode(blob.pop("data").encode("utf-8"))
    filepath: Path = content_path / field / filename
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(data)
    blob["blob_path"] = f"{filepath.relative_to(content_path.parent)}"
    return blob


async def export_item(item: t.PloneItem, parent_folder: Path) -> t.ItemFiles:
    """
    Export an item and its blobs to disk.

    Parameters
    ----------
    item : PloneItem
        The item to export.
    parent_folder : Path
        The parent folder for the item.

    Returns
    -------
    ItemFiles
        An object containing the data file path and blob file paths.
    """
    # Return blobs created here
    blob_files = []
    uid = item.get("UID")
    item_id = item.get("id")
    content_folder = parent_folder / f"{uid}"
    data_path: Path = content_folder / "data.json"
    blobs = item.pop("_blob_files_", {}) or {}
    for field, value in blobs.items():
        blob = await export_blob(field, value, content_folder, item_id)
        blob_files.append(blob["blob_path"])
        item[field] = blob
    await makedirs(content_folder, exist_ok=True)
    # Remove internal keys
    item_dict = {key: value for key, value in item.items() if not key.startswith("_")}
    async with aiofiles.open(data_path, "wb") as f:
        await f.write(json_dumps(item_dict))
    return t.ItemFiles(f"{data_path.relative_to(parent_folder)}", blob_files)


async def export_metadata(
    metadata: t.MetadataInfo,
    state: t.PipelineState,
    consoles: t.ConsoleArea,
    settings: t.TransmuteSettings,
) -> Path:
    """
    Export metadata to disk, including debug and relations files if needed.

    Parameters
    ----------
    metadata : MetadataInfo
        The metadata information object.
    state : PipelineState
        The pipeline state object.
    consoles : ConsoleArea
        The console area for logging.
    settings : TransmuteSettings
        The transmute settings object.

    Returns
    -------
    Path
        The path to the last written metadata file.
    """
    consoles.print_log("Writing metadata files")
    async for data, path in ei_utils.prepare_metadata_file(metadata, state, settings):
        async with aiofiles.open(path, "wb") as f:
            await f.write(json_dumps(data))
            consoles.debug(f"Wrote {path}")
    return path


def remove_data(path: Path, consoles: t.ConsoleArea | None = None):
    """
    Remove all data inside a given path, including files and directories.

    Parameters
    ----------
    path : Path
        The path whose contents will be removed.
    consoles : ConsoleArea, optional
        The console area for logging (default: None).
    """
    logger = get_logger()
    report = consoles.print_log if consoles else logger.debug
    contents: Iterator[Path] = path.glob("*")
    for content in contents:
        if content.is_dir():
            shutil.rmtree(content, True)
            report(f" - Removed directory {content}")
        else:
            content.unlink()
            report(f" - Removed file {content}")
