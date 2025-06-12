from collections.abc import AsyncGenerator
from collective.transmute import _types as t
from collective.transmute.settings import pb_config
from collective.transmute.utils import files
from dataclasses import asdict
from pathlib import Path


async def initialize_metadata(src_files: t.SourceFiles, dst: Path) -> t.MetadataInfo:
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

    return t.MetadataInfo(
        path=path,
        default_page=default_page,
        local_permissions=local_permissions,
        local_roles=local_roles,
        ordering=ordering,
        relations=relations,
    )


async def prepare_metadata_file(
    metadata: t.MetadataInfo, state: t.PipelineState, debug: bool = False
) -> AsyncGenerator[tuple[dict | list, Path]]:
    data: dict = asdict(metadata)
    path: Path = data.pop("path")
    fix_relations: dict[str, str] = data.pop("__fix_relations__", {})
    # Handle relations data
    async for rel_data, rel_path in prepare_relations_data(
        data["relations"], fix_relations, path, state
    ):
        yield rel_data, rel_path
    if debug:
        data["__seen__"] = list(state.seen)
        debug_path = path.parent / "__debug_metadata__.json"
        yield data, debug_path
    remove = [key for key in data if key.startswith("__") and key != "__version__"]
    if not bool(pb_config.default_pages.keep):
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
) -> AsyncGenerator[tuple[list[dict], Path]]:
    """
    {
    "from_uuid": "1afdd8784e734695be956a17d535f2bc",
    "relationship": "relatedItems",
    "to_uuid": "fb6afaac3f7941c39870ad71259d3e72"
    },
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
                "to_uuid": from_uuid,
            })
    path = (metadata_path.parent.parent / "relations.json").resolve()
    yield data, path
