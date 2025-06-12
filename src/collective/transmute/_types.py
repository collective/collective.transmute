from collections import defaultdict
from collections.abc import AsyncGenerator
from collections.abc import Callable
from collections.abc import Iterator
from collective.transmute import logger
from dataclasses import dataclass
from dataclasses import field
from dynaconf.base import LazySettings
from pathlib import Path
from rich.console import Console
from rich.progress import Progress
from typing import NotRequired
from typing import TypedDict

import logging
import os


type Settings = LazySettings


@dataclass
class SourceFiles:
    metadata: list[Path]
    content: list[Path]


@dataclass
class ItemFiles:
    data: str
    blob_files: list[str]


class ConsolePanel(Console):
    def __init__(self, *args, **kwargs):
        console_file = open(os.devnull, "w")  # noQA: SIM115
        super().__init__(*args, markup=True, record=True, file=console_file, **kwargs)

    def __rich_console__(self, console, options):
        texts = self.export_text(clear=False).split("\n")
        yield from texts[-options.height :]


@dataclass
class ConsoleArea:
    main: ConsolePanel
    side: ConsolePanel
    ui: bool = True

    def disable_ui(self):
        """Disable ui for the consoles."""
        self.ui = False
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        logger.addHandler(console)

    def print(self, message: str, panel_id: str = "main") -> None:
        """Print to one of the consoles."""
        if self.ui:
            console: ConsolePanel = getattr(self, panel_id)
            console.print(message)
        else:
            logger.info(message)

    def print_log(self, message: str, panel_id: str = "main") -> None:
        """Print to one of the consoles."""
        if self.ui:
            self.print(message, panel_id)
        logger.info(message)

    def debug(self, message: str, panel_id: str = "main") -> None:
        """Write a message to the debug logger."""
        logger.debug(message)


@dataclass
class PipelineProgress:
    processed: Progress
    processed_id: str
    dropped: Progress
    dropped_id: str

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
    processed: Progress
    processed_id: str

    def advance(self, task: str = "processed") -> None:
        progress = getattr(self, task)
        task_id = getattr(self, f"{task}_id")
        progress.advance(task_id)


@dataclass
class PipelineItemReport(TypedDict):
    filename: str
    src_path: str
    src_uid: str
    src_type: str
    dst_path: str
    dst_uid: str
    dst_type: str
    last_step: str


@dataclass
class PipelineState:
    total: int
    processed: int
    exported: defaultdict[str, int]
    dropped: defaultdict[str, int]
    progress: PipelineProgress
    seen: set = field(default_factory=set)
    uids: dict = field(default_factory=dict)
    path_transforms: list[PipelineItemReport] = field(default_factory=list)


@dataclass
class ReportState:
    files: Iterator
    types: defaultdict[str, int]
    creators: defaultdict[str, int]
    states: defaultdict[str, int]
    layout: dict[str, defaultdict[str, int]]
    type_report: defaultdict[str, list]
    progress: PipelineProgress

    def to_dict(self) -> dict[str, int | dict]:
        """Return report as dictionary."""
        data = {}
        for key in ("types", "creators", "states", "layout"):
            value = getattr(self, key)
            data[key] = value
        return data


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
        "image": NotRequired[dict[str, str | int]],
        "image_caption": NotRequired[str],
        "language": NotRequired[str],
    },
)

PloneItemGenerator = AsyncGenerator[PloneItem | None]

PipelineStep = Callable[[], PloneItemGenerator]
ItemProcessor = Callable[[], PloneItem]
