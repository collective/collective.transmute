"""
Data utilities for ``collective.transmute``.

This module provides helper functions for sorting and manipulating data structures
used in the transformation pipeline. Functions here are designed to be reusable
across steps and reporting.
"""


def sort_data_by_value(
    data: dict[str, int], reverse: bool = True
) -> tuple[tuple[str, int], ...]:
    """
    Sort a dictionary by its values and return a tuple of key-value pairs.

    Parameters
    ----------
    data : dict[str, int]
        The dictionary to sort.
    reverse : bool, optional
        Whether to sort in descending order (default: True).

    Returns
    -------
    tuple[tuple[str, int], ...]
        A tuple of (key, value) pairs sorted by value.

    Example
    -------
    .. code-block:: pycon

        >>> data = {'a': 2, 'b': 5, 'c': 1}
        >>> sort_data_by_value(data)
        (('b', 5), ('a', 2), ('c', 1))
    """
    return tuple(sorted(data.items(), key=lambda x: x[1], reverse=reverse))
