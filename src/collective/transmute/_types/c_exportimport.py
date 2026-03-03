from typing import NotRequired
from typing import TypedDict


class LocalRoles(TypedDict):
    """LocalRoles export/import schema"""

    uuid: str
    block: NotRequired[int]
    localroles: NotRequired[dict[str, list[str]]]
