"""
Settings utilities for ``collective.transmute``.

This module provides helper classes and functions for handling custom TOML encoding
and registration of encoders for settings serialization. Functions and classes
support custom data types in configuration files.
"""

from tomlkit.exceptions import ConvertError
from tomlkit.items import Array
from tomlkit.items import Item
from tomlkit.items import Table
from tomlkit.items import Trivia
from tomlkit.items import item
from tomlkit.toml_document import TOMLDocument

import tomlkit


class SetItem(Array):
    """
    TOMLKit ``Array`` subclass for encoding Python sets as TOML arrays.

    Returns
    -------
    list[str]
        The set converted to a list of strings.
    """

    def unwrap(self) -> list[str]:
        """
        Unwrap the set item to a list of strings.

        Returns
        -------
        list[str]
            The set as a list of strings.
        """
        return list(self)


def set_encoder(obj: set) -> Item:
    """
    Encode a Python set as a TOMLKit Item (``Array``).

    Parameters
    ----------
    obj : set
        The set to encode.

    Returns
    -------
    Item
        The TOMLKit Item representing the set.

    Raises
    ------
    ConvertError
        If the object is not a set.
    """
    if isinstance(obj, set):
        trivia = Trivia()
        return SetItem(value=list(obj), trivia=trivia, multiline=True)
    else:
        # we cannot convert this, but give other custom converters a
        # chance to run
        raise ConvertError


def register_encoders():
    """
    Register custom encoders for tomlkit to handle Python sets.

    Example
    -------
    .. code-block:: pycon

        >>> register_encoders()
    """
    tomlkit.register_encoder(set_encoder)


def _fix_arrays(table: Table) -> Table:
    """
    Ensure all arrays in the table are multiline.
    """
    for key, value in table.items():
        if isinstance(value, Table):
            table[key] = _fix_arrays(value)
        elif isinstance(value, Array):
            value._multiline = True
            table[key] = value
    return table


def settings_to_toml(data: dict) -> TOMLDocument:
    """
    Convert a dictionary containing the settings to a TOMLDocument.

    Parameters
    ----------
    data : dict
        The dictionary to convert.

    Returns
    -------
    TOMLDocument
        The resulting TOMLDocument.
    """
    document = TOMLDocument()
    for key, raw_value in data.items():
        document[key] = item(raw_value)

    for key, value in document.items():
        if isinstance(value, Table):
            document[key] = _fix_arrays(value)
    return document
