from tomlkit.exceptions import ConvertError
from tomlkit.items import Array
from tomlkit.items import Item
from tomlkit.items import Trivia

import tomlkit


class SetItem(Array):
    def unwrap(self) -> list[str]:
        return list(self)


def set_encoder(obj: set) -> Item:
    if isinstance(obj, set):
        trivia = Trivia()
        return SetItem(value=list(obj), trivia=trivia)
    else:
        # we cannot convert this, but give other custom converters a
        # chance to run
        raise ConvertError


def register_encoders():
    """Register custom encoders for tomlkit."""
    tomlkit.register_encoder(set_encoder)
