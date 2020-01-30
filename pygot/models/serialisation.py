"""Serialisation tools for networking and persistence."""

from __future__ import annotations

__all__ = ('camel_case', 'IdentifiableMixin', 'JSON', 'JSONMixin',
           'JSONType', 'ReplaceMixin', 'snake_case')

from abc import abstractmethod
import dataclasses
from string import ascii_letters, digits
from typing import Any, Dict, List, Union, Generic, TypeVar, Type

T = TypeVar('T')

_JT3 = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
_JT2 = Union[str, int, float, bool, None, Dict[str, _JT3], List[_JT3]]
_JT1 = Union[str, int, float, bool, None, Dict[str, _JT2], List[_JT2]]
_JT0 = Union[str, int, float, bool, None, Dict[str, _JT1], List[_JT1]]
JSONType = Union[str, int, float, bool, None, Dict[str, _JT0], List[_JT0]]
JSON = Dict[str, JSONType]


def snake_case(string: str) -> str:
    """
    Convert a string from camelCase to snake_case.

    TODO: Handling non-ASCII characters better.

    :param string: camelCase input
    :return: snake_case output
    """
    if set(string) - set(ascii_letters + digits + '_'):
        raise ValueError('Identifiers must only have ASCII characters')
    output = []

    # Flag whether we are in an uppercase series of characters
    uppercase = True

    for c in string:
        # Just add non-alpha as-is
        if not c.isalpha():
            output.append(c)
            uppercase = False

        # Lower clears uppercase flag and added as-is
        elif c.islower():
            output.append(c)
            uppercase = False

        # Upper added as lower (with a preceding _ if not in series)
        else:
            if not uppercase:
                output.append('_')
            output.append(c.lower())
            uppercase = True

    return ''.join(output)


def camel_case(string: str) -> str:
    """
    Convert a string from snake_case to camelCase.

    TODO: Handling non-ASCII characters better.

    :param string: snake_case input
    :return: camelCase output
    """
    if set(string) - set(ascii_letters + digits + '_'):
        raise ValueError('Identifiers must only have ASCII characters')

    if not string:
        return string

    words = string.lower().split('_')
    output = []

    first_word = True
    for word in words:
        if not word:
            output.append('_')
        elif first_word:
            output.append(word)
            first_word = False
        else:
            output.append(word.capitalize())

    return ''.join(output)


class IdentifiableMixin(Generic[T]):
    """Mixin for objects that are identifiable by ID."""

    @property
    @abstractmethod
    def id(self) -> T:
        """
        Unique ID for a static instance.

        :return: Unique ID
        """
        return NotImplemented

    @classmethod
    @abstractmethod
    def from_id(cls: Type[T], instance_id: T) -> T:
        """
        Resolve static instance from unique ID.

        :param instance_id: Unique ID
        :return: Static instance
        """
        return NotImplemented


@dataclasses.dataclass(frozen=True)
class JSONMixin:
    """Dataclass mixin for JSON serialisation and deserialisation."""

    def to_json(self) -> JSON:
        """
        Generate serialisable JSON structure.

        :return: Serialisable JSON structure
        """
        return {camel_case(k): v for k, v in dataclasses.asdict(self).items()}

    @classmethod
    def from_json(cls: Type[T], json: JSON) -> T:
        """
        Deserialise original dataclass from JSON structure.

        :param json: Serialisable JSON structure
        :return: Deserialised original dataclass
        """
        return cls(**{snake_case(k): v for k, v in json.items()})


@dataclasses.dataclass(frozen=True)
class ReplaceMixin:
    """Allows for immutable instance creation using replacement values."""

    def replace(self: T, **kwargs: Any) -> T:
        """
        Create new instance with replaced attribute values.

        :param kwargs: Replacement attribute values
        :return: New instance with replaced values
        """
        new_kwargs = dataclasses.asdict(self)
        new_kwargs.update(kwargs)
        return type(self)(**new_kwargs)
