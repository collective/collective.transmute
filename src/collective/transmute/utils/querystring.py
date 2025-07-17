from .portal_types import fix_portal_type
from collective.transmute import _types as t

import re


_PATH_UID_PATTERN = re.compile(r"UID##(?P<UID>.*)##")


def parse_path_value(value: str) -> str:
    """Parse a path value to ensure it is a valid URL."""
    parts = value.split(":")
    path = parts[0]
    if "/" not in path and len(path) == 32:
        value = value.replace(path, f"UID##{path}##")
    return value


def _process_date_between(raw_value: list[str]) -> tuple[str, list[str] | str]:
    """Process date between operation."""
    oper = "plone.app.querystring.operation.date.between"
    if len(raw_value) != 2:
        raise ValueError("Date between operation requires two values.")
    from_, to_ = raw_value
    if from_ is None and to_ is None:
        oper = ""
        value = []
    elif from_ is None:
        oper = "plone.app.querystring.operation.date.lessThan"
        value = to_
    elif to_ is None:
        oper = "plone.app.querystring.operation.date.largerThan"
        value = from_
    else:
        value = [from_, to_]
    return oper, value


def cleanup_querystring(query: list[dict]) -> tuple[list[dict], bool]:
    """Cleanup the querystring of a collection-like object or listing block."""
    post_processing = False
    query = query if query else []
    new_query = []
    for item in query:
        index = item["i"]
        oper = item["o"]
        value = item["v"]
        match index:
            case "portal_type":
                value = [fix_portal_type(v) for v in value]
                value = [v for v in value if v.strip()]
            case "section":
                value = None
        match oper:
            # Volto is not happy with `selection.is`
            case "plone.app.querystring.operation.selection.is":
                oper = "plone.app.querystring.operation.selection.any"
                value = list(set(value))
            case "plone.app.querystring.operation.selection.any":
                oper = "plone.app.querystring.operation.selection.any"
                value = list(set(value))
            case "plone.app.querystring.operation.date.between":
                oper, value = _process_date_between(value)
            case "plone.app.querystring.operation.string.path":
                value = parse_path_value(str(value))
                post_processing = value.startswith("UID##")
        if oper and value:
            item["v"] = value
            item["o"] = oper
            new_query.append(item)
    return new_query, post_processing


def post_process_querystring(query: list[dict], state: t.PipelineState) -> list[dict]:
    """Post-process a querystring."""
    query = query if query else []
    new_query = []
    for item in query:
        oper = item["o"]
        value = item["v"]
        match oper:
            case "plone.app.querystring.operation.string.path":
                value = str(value)
                if match := re.match(_PATH_UID_PATTERN, value):
                    uid = match.group("UID")
                    if path := state.uid_path.get(uid):
                        value = re.sub(_PATH_UID_PATTERN, path, value)
                    else:
                        # Path not found, keep original value
                        value = re.sub(_PATH_UID_PATTERN, uid, value)
        if value:
            item["v"] = value
            item["o"] = oper
            new_query.append(item)
    return new_query
