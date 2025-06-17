from collective.transmute.settings import get_settings
from functools import cache


@cache
def fix_portal_type(type_: str) -> str:
    settings = get_settings()
    return settings.types.get(type_, {}).get("portal_type", "")
