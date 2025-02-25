from collections.abc import AsyncGenerator
from collective.transmute._types import MetadataInfo
from collective.transmute._types import SourceFiles
from collective.transmute.utils import files
from dataclasses import asdict
from pathlib import Path


async def initialize_metadata(src_files: SourceFiles, dst: Path) -> MetadataInfo:
    path = dst / "__metadata__.json"
    metadata_files = src_files.metadata
    data = {}
    async for filename, content in files.json_reader(metadata_files):
        key = filename.replace("export_", "").replace(".json", "")
        data[key] = content

    # Process default_pages
    if "defaultpages" in data:
        default_page = {
            item["uuid"]: item["default_page_uuid"] for item in data["defaultpages"]
        }
        local_permissions: dict[str, dict] = {}
    # Process local_roles
    local_roles: dict[str, dict] = {
        item["uuid"]: {"local_roles": item["localroles"]} for item in data["localroles"]
    }
    ordering: dict[str, dict] = {
        item["uuid"]: item["order"] for item in data["ordering"]
    }
    relations: list[dict] = data["relations"]

    return MetadataInfo(
        path=path,
        default_page=default_page,
        local_permissions=local_permissions,
        local_roles=local_roles,
        ordering=ordering,
        relations=relations,
    )


async def prepare_metadata_file(
    metadata: MetadataInfo, debug: bool = False
) -> AsyncGenerator[tuple[dict, Path]]:
    data: dict = asdict(metadata)
    path: Path = data.pop("path")
    if debug:
        data["__seen__"] = list(data["__seen__"])
        debug_path = path.parent / "__debug_metadata__.json"
        yield data, debug_path
    seen = data.pop("__seen__", [])
    remove = [key for key in data if key.startswith("__") and key != "__version__"]
    data["default_page"] = {k: v for k, v in data["default_page"].items() if k in seen}
    data["ordering"] = {k: v for k, v in data["ordering"].items() if k in seen}
    data["local_roles"] = {k: v for k, v in data["local_roles"].items() if k in seen}
    data["relations"] = []
    for item in remove:
        data.pop(item)
    yield data, path
