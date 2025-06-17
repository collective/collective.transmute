from .settings import TransmuteSettings
from dataclasses import dataclass


__all__ = ["ContextObject"]


@dataclass
class ContextObject:
    """Context object used by cli."""

    settings: TransmuteSettings
