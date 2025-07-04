from collections.abc import AsyncGenerator
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import NotRequired
from typing import TypedDict


__all__ = [
    "ItemProcessor",
    "MetadataInfo",
    "PloneItem",
    "PloneItemGenerator",
]


@dataclass
class MetadataInfo:
    path: Path
    __version__: str = "1.0.0"
    __processing_default_page__: dict = field(default_factory=dict)
    __fix_relations__: dict = field(default_factory=dict)
    _blob_files_: list = field(default_factory=list)
    _data_files_: list = field(default_factory=list)
    default_page: dict = field(default_factory=dict)
    local_permissions: dict = field(default_factory=dict)
    local_roles: dict = field(default_factory=dict)
    ordering: dict = field(default_factory=dict)
    relations: list = field(default_factory=list)


PloneItem = TypedDict(
    "PloneItem",
    {
        "@id": str,
        "@type": str,
        "UID": str,
        "id": str,
        "title": NotRequired[str],
        "description": NotRequired[str],
        "creators": NotRequired[list[str]],
        "image": NotRequired[dict[str, str | int]],
        "image_caption": NotRequired[str],
        "language": NotRequired[str],
        "text": NotRequired[dict[str, str]],
        "nav_title": NotRequired[str],
        "_UID": NotRequired[str],
        "exclude_from_nav": NotRequired[bool],
        "_is_new_item": NotRequired[bool],
        "_blob_files_": NotRequired[dict[str, dict[str, str]]],
    },
)

PloneItemGenerator = AsyncGenerator[PloneItem | None]

ItemProcessor = Callable[[PloneItem], PloneItem]
