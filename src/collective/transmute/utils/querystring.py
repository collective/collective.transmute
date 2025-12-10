"""
Querystring utilities for ``collective.transmute``.

This module provides helper functions for cleaning up, deduplicating, and
post-processing querystring definitions used in Plone collections and
listing blocks. Functions support normalization and transformation of
querystring items and values.
"""

from .portal_types import fix_portal_type
from collective.transmute import _types as t
from typing import Any

import re


_PATH_UID_PATTERN = re.compile(r"UID##(?P<UID>.*)##")

PLACEHOLDER_TODAY = object()


def parse_path_value(value: str, src_site_root: str = "/Plone") -> str:
    """
    Parse a path value to ensure it is a valid URL or UID reference.

    Parameters
    ----------
    value : str
        The path value to parse.
    src_site_root : str
        The site root in the source dataset.

    Returns
    -------
    str
        The parsed path value, possibly converted to UID format.

    Example
    -------
    .. code-block:: pycon

        >>> parse_path_value('12345678901234567890123456789012')
        'UID##12345678901234567890123456789012##'
    """
    parts = value.split(":")
    path = parts[0]
    if "/" not in path and len(path) == 32:
        value = value.replace(path, f"UID##{path}##")
    elif path.startswith(src_site_root):
        value = value.replace(src_site_root, "")
    return value


def _process_subjects(raw_value: list[str]) -> list[str]:
    """
    Process a list of subjects and return a deduplicated list.

    Parameters
    ----------
    raw_value : list[str]
        List of subject strings.

    Returns
    -------
    list[str]
        Deduplicated list of subjects.
    """
    new_values = set()
    for subject in raw_value:
        new_values.add(subject.strip())
    return list(new_values)


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


def _process_operation(
    oper: str, value: Any, post_processing: bool, src_site_root: str
) -> tuple[str, Any, bool]:
    """
    Process a single operation and its value for querystring items.

    Parameters
    ----------
    oper : str
        The operation to process.
    value : Any
        The value associated with the operation.
    post_processing : bool
        Flag indicating if post-processing is needed.
    src_site_root : str
        The site root in the source dataset.
    """
    prefix = "plone.app.querystring.operation"
    match oper:
        case (
            "plone.app.querystring.operation.date.afterToday"
            | "plone.app.querystring.operation.date.beforeToday"
        ):
            value = PLACEHOLDER_TODAY
        case (
            "plone.app.querystring.operation.selection.is"
            | "plone.app.querystring.operation.selection.any"
        ):
            oper = "plone.app.querystring.operation.selection.any"
            value = deduplicate_value(value)
        case "plone.app.querystring.operation.date.between":
            oper, value = _process_date_between(value)
        case "plone.app.querystring.operation.string.path":
            if str(value).startswith(src_site_root):
                oper = "plone.app.querystring.operation.string.absolutePath"
            value = parse_path_value(str(value), src_site_root)
            post_processing = value.startswith("UID##")
        case "plone.app.querystring.operation.date.lessThanRelativeDate":
            if isinstance(value, int) and value < 0:
                oper = f"{prefix}.date.largerThanRelativeDate"
                value = abs(value)
    return oper, value, post_processing


def cleanup_querystring_item(item: dict, src_site_root: str) -> tuple[dict, bool]:
    """
    Clean up a single item in a querystring definition.

    Parameters
    ----------
    item : dict
        The querystring item to clean up.
    src_site_root : str
        The site root in the source dataset.

    Returns
    -------
    tuple[dict, bool]
        The cleaned item and a post-processing status flag.
    """
    post_processing = False
    index = item["i"]
    oper = item["o"]
    value = item.get("v")
    match index:
        case "portal_type":
            value = [fix_portal_type(v) for v in value] if value else []
            value = [v for v in value if v.strip()]
        case "section":
            value = None
        case "Subject":
            value = _process_subjects(value) if value else []
    oper, value, post_processing = _process_operation(
        oper, value, post_processing, src_site_root
    )
    if oper and value:
        if value is not PLACEHOLDER_TODAY:
            item["v"] = value
        item["o"] = oper
    else:
        item = {}
    return item, post_processing


def cleanup_querystring(
    query: list[dict], src_site_root: str = "/Plone"
) -> tuple[list[dict], bool]:
    """
    Clean up the querystring of a collection-like object or listing block.

    Parameters
    ----------
    query : list[dict]
        The querystring to clean up.
    src_site_root : str
        The site root in the source dataset. (defaults to "/Plone")

    Returns
    -------
    tuple[list[dict], bool]
        The cleaned querystring and a post-processing status flag.
    """
    post_processing = False
    query = query if query else []
    new_query = []
    for item in query:
        item, status = cleanup_querystring_item(item, src_site_root)
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
