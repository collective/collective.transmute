"""
Portal type utilities for ``collective.transmute``.

This module provides helper functions for mapping and fixing portal types
based on settings in the transformation pipeline. Functions support type
normalization and lookup.
"""

from collective.transmute.settings import get_settings
from functools import cache


@cache
def fix_portal_type(type_: str) -> str:
    """
    Return the mapped portal type for a given type using settings.

    Parameters
    ----------
    type_ : str
        The type to map to a portal type.

    Returns
    -------
    str
        The mapped portal type, or an empty string if not found.

    Example
    -------
    .. code-block:: pycon

        >>> fix_portal_type('Document')
        'Document'  # or mapped value from settings
    """
    settings = get_settings()
    return settings.types.get(type_, {}).get("portal_type", "")
