"""
Settings utilities for ``collective.transmute``.

This module provides helper classes and functions for handling custom TOML encoding
and registration of encoders for settings serialization. Functions and classes are
documented for Sphinx autodoc and support custom data types in configuration files.
"""

from tomlkit.exceptions import ConvertError
from tomlkit.items import Array
from tomlkit.items import Item
from tomlkit.items import Trivia

import tomlkit


class SetItem(Array):
    """
    TOMLKit Array subclass for encoding Python sets as TOML arrays.

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
    Encode a Python set as a TOMLKit Item (Array).

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
        return SetItem(value=list(obj), trivia=trivia)
    else:
        # we cannot convert this, but give other custom converters a
        # chance to run
        raise ConvertError


def register_encoders():
    """
    Register custom encoders for tomlkit to handle Python sets.

    Example
    -------
    >>> register_encoders()
    """
    tomlkit.register_encoder(set_encoder)
