from collective.transmute import _types as t
from urllib import parse

import re


_CLEANUP: tuple[tuple[str, str], ...] | None = None


def get_paths_cleanup(settings: t.TransmuteSettings) -> tuple[tuple[str, str], ...]:
    """Return cleanup paths."""
    global _CLEANUP
    if _CLEANUP is None:
        _CLEANUP = tuple(settings.paths["cleanup"].items())
    return _CLEANUP


PATTERNS = [
    re.compile(r"^[ _-]*(?P<path>[^ _-]*)[ _-]*$"),
]


def fix_short_id(id_: str) -> str:
    for pattern in PATTERNS:
        if match := re.match(pattern, id_):
            id_ = match.groupdict()["path"]
    if " " in id_:
        id_ = id_.replace(" ", "_")
    return id_


async def process_export_prefix(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    path = item["@id"]
    for src in settings.paths["export_prefixes"]:
        if path.startswith(src):
            path = path.replace(src, "")
    item["@id"] = path
    # Used in reports
    item["_@id"] = path
    yield item


async def process_ids(
    item: t.PloneItem, state: t.PipelineState, settings: t.TransmuteSettings
) -> t.PloneItemGenerator:
    path = parse.unquote(item["@id"].replace(" ", "_"))
    cleanup_paths = get_paths_cleanup(settings)
    for src, rpl in cleanup_paths:
        if src in path:
            path = path.replace(src, rpl)

    parts = path.rsplit("/", maxsplit=-1)
    if parts:
        parts[-1] = fix_short_id(parts[-1])
        path = "/".join(parts)
        item["@id"] = path
        item["id"] = parts[-1]
    yield item
