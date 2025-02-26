from collections.abc import AsyncGenerator
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from dynaconf.base import LazySettings
from pathlib import Path
from typing import TypedDict


type Settings = LazySettings


@dataclass
class SourceFiles:
    metadata: list[Path]
    content: list[Path]


@dataclass
class ItemFiles:
    data: str
    blob_files: list[str]


@dataclass
class MetadataInfo:
    path: Path
    __version__: str = "1.0.0"
    __seen__: set = field(default_factory=set)
    __processing_default_page__: dict = field(default_factory=dict)
    __fix_relations__: dict = field(default_factory=dict)
    _blob_files_: list = field(default_factory=list)
    _data_files_: list = field(default_factory=list)
    default_page: dict = field(default_factory=dict)
    local_permissions: dict = field(default_factory=dict)
    local_roles: dict = field(default_factory=dict)
    ordering: dict = field(default_factory=dict)
    relations: dict = field(default_factory=dict)


PloneItem = TypedDict("PloneItem", {"@id": str, "@type": str, "UID": str, "id": str})

PloneItemGenerator = AsyncGenerator[PloneItem | None]

PipelineStep = Callable[[], PloneItemGenerator]
ItemProcessor = Callable[[], PloneItem]
