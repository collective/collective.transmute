from collections.abc import AsyncGenerator
from collective.html2blocks._types import BlocksLayout
from collective.html2blocks._types import VoltoBlock
from collective.html2blocks._types import VoltoBlocksInfo  # noqa: F401
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import NotRequired
from typing import TypedDict


__all__ = [
    "MetadataInfo",
    "PloneItem",
    "PloneItemGenerator",
]


@dataclass
class MetadataInfo:
    path: Path
    __version__: str = "1.0.0"
    __processing_default_page__: dict = field(default_factory=dict, repr=False)
    __fix_relations__: dict = field(default_factory=dict, repr=False)
    _blob_files_: list = field(default_factory=list, repr=False)
    _data_files_: list = field(default_factory=list, repr=False)
    default_page: dict = field(default_factory=dict, repr=False)
    local_permissions: dict = field(default_factory=dict, repr=False)
    local_roles: dict = field(default_factory=dict, repr=False)
    ordering: dict = field(default_factory=dict, repr=False)
    relations: list = field(default_factory=list, repr=False)
    redirects: dict = field(default_factory=dict, repr=False)


class WorkflowHistoryEntry(TypedDict):
    """A single entry in a workflow history."""

    action: str | None
    actor: str
    comments: str
    review_state: str
    time: str


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
        "remoteUrl": NotRequired[str],
        "language": NotRequired[str],
        "text": NotRequired[dict[str, str]],
        "nav_title": NotRequired[str],
        "query": NotRequired[list],
        "blocks": NotRequired[dict[str, VoltoBlock]],
        "blocks_layout": NotRequired[BlocksLayout],
        "exclude_from_nav": NotRequired[bool],
        "review_state": NotRequired[str],
        "workflow_history": NotRequired[dict[str, list[WorkflowHistoryEntry]]],
        "_blocks_": NotRequired[list[VoltoBlock]],
        "_UID": NotRequired[str],
        "_orig_type": NotRequired[str],
        "_is_new_item": NotRequired[bool],
        "_blob_files_": NotRequired[dict[str, dict[str, str]]],
        "_@id": NotRequired[str],
    },
)

PloneItemGenerator = AsyncGenerator[PloneItem | None]
