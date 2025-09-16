"""
Export/import utilities for ``collective.transmute``.

This module provides asynchronous helper functions for preparing and handling
metadata and relations during the transformation pipeline. Functions here are used
for reading, processing, and writing metadata and relations files, according to the
format expected by ``plone.exportimport``.
"""

from .redirects import initialize_redirects
from collections.abc import AsyncGenerator
from collective.transmute import _types as t
from collective.transmute.utils import files
from collective.transmute.utils import redirects as redirect_utils
from dataclasses import asdict
from pathlib import Path


async def initialize_metadata(src_files: t.SourceFiles, dst: Path) -> t.MetadataInfo:
    """
    Initialize and load metadata from source files into a ``MetadataInfo`` object.

    Parameters
    ----------
    src_files : SourceFiles
        The source files containing metadata.
    dst : Path
        The destination path for metadata.

    Returns
    -------
    MetadataInfo
        The loaded metadata information object.
    """
    path = dst / "__metadata__.json"
    metadata_files = src_files.metadata
    data = {}
    async for filename, content in files.json_reader(metadata_files):
        key = filename.replace("export_", "").replace(".json", "")
        data[key] = content

    # Process default_pages
    default_page = {
        item["uuid"]: item["default_page_uuid"] for item in data.get("defaultpages", [])
    }
    local_permissions: dict[str, dict] = {}
    # Process local_roles
    local_roles: dict[str, dict] = {
        item["uuid"]: {"local_roles": item["localroles"]}
        for item in data.get("localroles", [])
    }
    ordering: dict[str, dict] = {
        item["uuid"]: item["order"] for item in data.get("ordering", [])
    }
    relations: list[dict] = data.get("relations", [])
    redirects: dict[str, str] = initialize_redirects(data.get("redirects", {}))

    return t.MetadataInfo(
        path=path,
        default_page=default_page,
        local_permissions=local_permissions,
        local_roles=local_roles,
        ordering=ordering,
        relations=relations,
        redirects=redirects,
    )


async def prepare_metadata_file(
    metadata: t.MetadataInfo, state: t.PipelineState, settings: t.TransmuteSettings
) -> AsyncGenerator[tuple[dict | list, Path], None]:
    """
    Prepare and yield metadata files for export, including debug and relations data.

    Parameters
    ----------
    metadata : MetadataInfo
        The metadata information object.
    state : PipelineState
        The pipeline state object.
    settings : TransmuteSettings
        The transmute settings object.

    Yields
    ------
    tuple[dict | list, Path]
        Tuples of data and their corresponding file paths.
    """
    data: dict = asdict(metadata)
    path: Path = data.pop("path")
    fix_relations: dict[str, str] = data.pop("__fix_relations__", {})
    # Handle relations data
    relations = data.pop("relations", [])
    async for rel_data, rel_path in prepare_relations_data(
        relations, fix_relations, path, state
    ):
        yield rel_data, rel_path
    # Handle redirects data
    redirects: dict[str, str] = data.pop("redirects", {})
    async for red_data, red_path in prepare_redirects_data(
        redirects, path, state.paths, settings.site_root["dest"]
    ):
        yield red_data, red_path

    if settings.is_debug:
        data["__seen__"] = list(state.seen)
        debug_path = path.parent / "__debug_metadata__.json"
        yield data, debug_path
    remove = [key for key in data if key.startswith("__") and key != "__version__"]
    if not bool(settings.default_pages["keep"]):
        # Remove default_page from list
        data["default_page"] = {}
    for key in ["default_page", "ordering", "local_roles"]:
        data[key] = {k: v for k, v in data[key].items() if k in state.uids}
    data["relations"] = []
    for item in remove:
        data.pop(item)
    yield data, path


async def prepare_relations_data(
    relations: list[dict[str, str]],
    to_fix: dict[str, str],
    metadata_path: Path,
    state: t.PipelineState,
) -> AsyncGenerator[tuple[list[dict], Path], None]:
    """
    Prepare and yield relations data for export.

    Parameters
    ----------
    relations : list[dict[str, str]]
        List of relations dictionaries.
    to_fix : dict[str, str]
        Mapping of UUIDs to fix.
    metadata_path : Path
        Path to the metadata file.
    state : PipelineState
        The pipeline state object.

    Yields
    ------
    tuple[list[dict], Path]
        Tuples of relations data and their corresponding file paths.
    """

    def final_uid(item: dict, attr: str) -> str | None:
        uid = item.get(attr, "")
        if uid:
            uid = uids.get(uid, to_fix.get(uid))
        return uid if uid else None

    data = []
    uids = state.uids
    for item in relations:
        from_uuid: str | None = final_uid(item, "from_uuid")
        to_uuid: str | None = final_uid(item, "to_uuid")
        from_attribute: str = item.get("relationship", item.get("from_attribute", ""))
        if from_uuid and to_uuid and from_attribute and from_uuid != to_uuid:
            data.append({
                "from_attribute": from_attribute,
                "from_uuid": from_uuid,
                "to_uuid": to_uuid,
            })
    path = (metadata_path.parent.parent / "relations.json").resolve()
    yield data, path


async def prepare_redirects_data(
    redirects: dict[str, str],
    metadata_path: Path,
    state_paths: list[tuple[str, str, str]],
    site_root: str,
) -> AsyncGenerator[tuple[dict[str, str], Path], None]:
    """
    Prepare and yield redirects data for export as a JSON file.

    This function takes a mapping of redirects and yields it with the output file
    path. The output file is named 'redirects.json' and is used by plone.exportimport.

    Args:
        redirects (dict[str, str]):
            Mapping of source paths to destination paths.
        metadata_path (Path):
            Path to the metadata file. Used to determine output location.
        state_paths (list[tuple[str, str, str]]):
            List of valid paths from the pipeline state.
        site_root (str):
            The root path for the destination site.

    Yields:
        tuple[dict[str, str], Path]:
            The filtered redirects mapping and the output file path.

    Example:
        >>> async for result in prepare_redirects_data(
        ...     redirects, metadata_path, state_paths, site_root
        ... ):
        ...     data, path = result
        ...     print(path)
    """
    valid_paths = {f"{site_root}{p[0]}" for p in state_paths}
    data = redirect_utils.filter_redirects(redirects, valid_paths)
    path = (metadata_path.parent.parent / "redirects.json").resolve()
    yield data, path
