from dataclasses import dataclass
from pathlib import Path


@dataclass
class SourceFiles:
    metadata: list[Path]
    content: list[Path]


@dataclass
class ItemFiles:
    data: str
    blob_files: list[str]
