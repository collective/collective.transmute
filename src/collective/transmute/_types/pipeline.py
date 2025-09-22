from .console import ConsoleArea
from .plone import MetadataInfo
from .plone import PloneItem
from .plone import PloneItemGenerator
from .settings import TransmuteSettings
from collections import defaultdict
from collections.abc import AsyncGenerator
from collections.abc import Iterator
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from rich.progress import Progress
from typing import Any
from typing import Protocol
from typing import TypedDict


__all__ = [
    "ItemProcessor",
    "PipelineItemReport",
    "PipelineProgress",
    "PipelineState",
    "PipelineStep",
    "PrepareStep",
    "PrepareStepGenerator",
    "ReportProgress",
    "ReportState",
    "ReportStep",
]


@dataclass
class PipelineProgress:
    """
    Tracks progress for processed and dropped items in the pipeline.
    """

    processed: Progress
    """Progress bar for processed items."""
    processed_id: str
    """Task ID for processed items."""
    dropped: Progress
    """Progress bar for dropped items."""
    dropped_id: str
    """Task ID for dropped items."""

    def advance(self, task: str) -> None:
        progress = getattr(self, task)
        task_id = getattr(self, f"{task}_id")
        progress.advance(task_id)

    def total(self, task: str, total: int) -> None:
        progress = getattr(self, task)
        task_id = getattr(self, f"{task}_id")
        progress.update(task_id, total=total)


@dataclass
class ReportProgress:
    """
    Tracks progress for processed items in reporting steps.
    """

    processed: Progress
    """Progress bar for processed items."""
    processed_id: str
    """Task ID for processed items."""

    def advance(self, task: str = "processed") -> None:
        progress = getattr(self, task)
        task_id = getattr(self, f"{task}_id")
        progress.advance(task_id)


@dataclass
class PipelineItemReport(TypedDict):
    """
    Report for a single item processed by the pipeline.
    """

    filename: str
    """Original file name of the item."""
    src_path: str
    """Source path in the portal."""
    src_uid: str
    """Source UID for the item."""
    src_type: str
    """Source portal type."""
    dst_path: str
    """Destination path in the portal."""
    dst_uid: str
    """Destination UID for the item."""
    dst_type: str
    """Destination portal type."""
    last_step: str
    """Name of the last pipeline step for the item."""
    status: str
    """Status of the item after processing. Either dropped or processed."""
    src_level: int
    """
    Level of the item in the source hierarchy.

    A value `0` means the item is at the root of the portal.
    If level is `-1`, the source item did not exist.
    """
    dst_level: int
    """
    Level of the item in the destination hierarchy.

    A value `0` means the item is at the root of the portal.
    If level is `-1`, the source item did not exist.
    """


@dataclass
class PipelineState:
    """
    State of the current pipeline run.
    """

    total: int
    """
    Total number of items to process.

    Can be updated during run if one of the steps in the pipeline
    creates new items.
    """
    processed: int
    """Number of items processed so far."""
    exported: defaultdict[str, int]
    """Count of exported items by type."""
    dropped: defaultdict[str, int]
    """Count of dropped items by type."""
    progress: PipelineProgress = field(repr=False)
    """Progress tracking for pipeline tasks."""
    seen: set = field(default_factory=set, repr=False)
    """Set of seen item identifiers."""
    uids: dict = field(default_factory=dict, repr=False)
    """
    Mapping of UIDs to items.

    This is used to track items that could have changed their UIDs during the
    run. One possible case is when we merge the default page of an item with the
    item itself.
    """
    uid_path: dict = field(default_factory=dict, repr=False)
    """Mapping of UIDs to paths."""
    path_transforms: list[PipelineItemReport] = field(default_factory=list, repr=False)
    """List of item path transformations."""
    paths: list[tuple[str, str, str]] = field(default_factory=list, repr=False)
    """List of item paths and related info."""
    post_processing: dict[str, list[str]] = field(default_factory=dict, repr=False)
    """Items scheduled for post-processing."""
    annotations: dict[str, dict[str, Any]] = field(default_factory=dict, repr=False)
    """Additional annotations for items."""
    metadata: MetadataInfo | None = field(default=None, repr=False)
    """Metadata for the pipeline run."""
    write_report: bool = field(default=True, repr=True)
    """Flag to control if we should write the paths report."""


@dataclass
class ReportState:
    """
    State and summary for reporting on pipeline results.
    """

    files: Iterator
    """Iterator over files to report on."""
    types: defaultdict[str, int]
    """Count of items by type."""
    creators: defaultdict[str, int]
    """Count of items by creator."""
    states: defaultdict[str, int]
    """Count of items by review state."""
    subjects: defaultdict[str, int]
    """Count of items by subject/tag."""
    layout: dict[str, defaultdict[str, int]]
    """Layout view usage per type."""
    type_report: defaultdict[str, list]
    """Detailed report by type."""
    progress: PipelineProgress
    """Progress tracking for reporting."""

    def to_dict(self) -> dict[str, int | dict]:
        """
        Return report as dictionary.
        """
        data = {}
        for key in ("types", "creators", "states", "layout", "subjects"):
            value = getattr(self, key)
            data[key] = value
        return data


class PipelineStep(Protocol):
    """
    Protocol for a pipeline step function.

    A pipeline step processes a single item, updating state and yielding results.
    """

    __name__: str

    def __call__(
        self, item: PloneItem, state: PipelineState, settings: TransmuteSettings
    ) -> PloneItemGenerator:
        """
        Process a single item in the pipeline.

        Args:
            item (PloneItem): The item to process.
            state (PipelineState): The current pipeline state.
            settings (TransmuteSettings): The pipeline settings.

        Returns:
            PloneItemGenerator: An async generator yielding processed items.
        """
        ...


class ItemProcessor(Protocol):
    """
    Protocol for a processor function for a single item.

    An item processor processes a single item and returns the result.
    """

    __name__: str

    def __call__(self, item: PloneItem, state: PipelineState) -> PloneItem:
        """
        Process a single item.

        Args:
            item (PloneItem): The item to process.
            state (PipelineState): The current pipeline state.

        Returns:
            PloneItem: The processed item.
        """
        ...


PrepareStepGenerator = AsyncGenerator[bool]


class PrepareStep(Protocol):
    __name__: str

    def __call__(
        self, state: PipelineState, settings: TransmuteSettings
    ) -> AsyncGenerator[bool]: ...


ReportItemGenerator = AsyncGenerator[Path | None]


class ReportStep(Protocol):
    __name__: str

    def __call__(
        self, state: PipelineState, settings: TransmuteSettings, consoles: ConsoleArea
    ) -> ReportItemGenerator: ...
