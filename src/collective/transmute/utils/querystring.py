"""
Querystring utilities for collective.transmute.

This module provides helper functions for cleaning up, deduplicating, and
post-processing querystring definitions used in Plone collections and
listing blocks. Functions are documented for Sphinx autodoc and support
normalization and transformation of querystring items and values.
"""

from .portal_types import fix_portal_type
from collective.transmute import _types as t

import re


_PATH_UID_PATTERN = re.compile(r"UID##(?P<UID>.*)##")


def parse_path_value(value: str) -> str:
    """
    Parse a path value to ensure it is a valid URL or UID reference.

    Parameters
    ----------
    value : str
        The path value to parse.

    Returns
    -------
    str
        The parsed path value, possibly converted to UID format.

    Example
    -------
    >>> parse_path_value('12345678901234567890123456789012')
    'UID##12345678901234567890123456789012##'
    """
    parts = value.split(":")
    path = parts[0]
    if "/" not in path and len(path) == 32:
        value = value.replace(path, f"UID##{path}##")
    return value


def _process_date_between(raw_value: list[str]) -> tuple[str, list[str] | str]:
    """
    Process a date between operation for querystring items.

    Parameters
    ----------
    raw_value : list[str]
        List containing two date strings.

    Returns
    -------
    tuple[str, list[str] | str]
        The operation and processed value(s).
    """
    oper = "plone.app.querystring.operation.date.between"
    if len(raw_value) != 2:
        raise ValueError("Date between operation requires two values.")
    from_, to_ = raw_value
    if from_ is None and to_ is None:
        oper = ""
        value = []
    elif from_ is None:
        oper = "plone.app.querystring.operation.date.lessThan"
        value = to_.split("T")[0]
    elif to_ is None:
        oper = "plone.app.querystring.operation.date.largerThan"
        value = from_.split("T")[0]
    else:
        value = [from_, to_]
    return oper, value


def deduplicate_value(value: list | None) -> list | None:
    """
    Deduplicate values in a list, preserving None.

    Parameters
    ----------
    value : list or None
        The list to deduplicate.

    Returns
    -------
    list or None
        The deduplicated list, or None if input is None.
    """
    return list(set(value)) if value is not None else None


def cleanup_querystring_item(item: dict) -> tuple[dict, bool]:
    """
    Cleanup a single item in a querystring definition.

    Parameters
    ----------
    item : dict
        The querystring item to clean up.

    Returns
    -------
    tuple[dict, bool]
        The cleaned item and a post-processing status flag.
    """
    prefix = "plone.app.querystring.operation"
    post_processing = False
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
        case (
            "plone.app.querystring.operation.selection.is"
            | "plone.app.querystring.operation.selection.any"
        ):
            oper = "plone.app.querystring.operation.selection.any"
            value = deduplicate_value(value)
        case "plone.app.querystring.operation.date.between":
            oper, value = _process_date_between(value)
        case "plone.app.querystring.operation.string.path":
            value = parse_path_value(str(value))
            post_processing = value.startswith("UID##")
        case "plone.app.querystring.operation.date.lessThanRelativeDate":
            if isinstance(value, int) and value < 0:
                oper = f"{prefix}.date.largerThanRelativeDate"
                value = abs(value)
    if oper and value:
        item["v"] = value
        item["o"] = oper
    else:
        item = {}
    return item, post_processing


def cleanup_querystring(query: list[dict]) -> tuple[list[dict], bool]:
    """
    Cleanup the querystring of a collection-like object or listing block.

    Parameters
    ----------
    query : list[dict]
        The querystring to clean up.

    Returns
    -------
    tuple[list[dict], bool]
        The cleaned querystring and a post-processing status flag.
    """
    post_processing = False
    query = query if query else []
    new_query = []
    for item in query:
        item, status = cleanup_querystring_item(item)
        if not item:
            continue
        post_processing = post_processing or status
        new_query.append(item)
    return new_query, post_processing


def post_process_querystring(query: list[dict], state: t.PipelineState) -> list[dict]:
    """
    Post-process a querystring, replacing UID references with actual paths.

    Parameters
    ----------
    query : list[dict]
        The querystring to post-process.
    state : PipelineState
        The pipeline state object containing UID-path mapping.

    Returns
    -------
    list[dict]
        The post-processed querystring.
    """
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
                        value = re.sub(_PATH_UID_PATTERN, uid, value)
        if value:
            item["v"] = value
            item["o"] = oper
            new_query.append(item)
    return new_query
