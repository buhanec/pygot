"""Serialisation tools for networking and persistence."""

from __future__ import annotations

__all__ = ('camel_case', 'JSON', 'JSONMixin', 'JSONType',
           'ReplaceMixin', 'snake_case')

import dataclasses
import datetime
from enum import Enum
import functools
import importlib
import logging
from string import ascii_letters, digits
from typing import (Any, Dict, List, Mapping, Sequence, Type, TypeVar,
                    Union, cast)

import pytz

from pygot.utils import type_name

logger = logging.getLogger(__name__)

T = TypeVar('T')

_JT3 = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
_JT2 = Union[str, int, float, bool, None, Dict[str, _JT3], List[_JT3]]
_JT1 = Union[str, int, float, bool, None, Dict[str, _JT2], List[_JT2]]
_JT0 = Union[str, int, float, bool, None, Dict[str, _JT1], List[_JT1]]
JSONType = Union[str, int, float, bool, None, Dict[str, _JT0], List[_JT0]]
JSON = Dict[str, JSONType]

_MODULE_KEY = '$module'
_NAME_KEY = '$type'


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


def jsonify(obj: Any, camel_case_keys: bool = True) -> JSONType:
    """
    "JSON-ify" object.

    Attemps to serialise Python object in a fashion that would make
    JSON serialisation and deserialisation easier.

    :param obj: Python object
    :param camel_case_keys: Use camelCase keys
    :return: "JSON-ified" object
    """
    _j = functools.partial(jsonify, camel_case_keys=camel_case_keys)

    # If we explicitly have a JSON serialisation, use it
    if isinstance(obj, JSONMixin):
        json = obj.to_json()
        json[_MODULE_KEY] = type(obj).__module__
        json[_NAME_KEY] = type(obj).__name__
        return json

    # Return basic types as-is
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj

    # Recursively process collections
    if isinstance(obj, Sequence):
        return [_j(o) for o in obj]
    if isinstance(obj, Mapping):
        d = {_j(k): _j(v) for k, v in obj.items()}
        if camel_case_keys:
            d = {camel_case(k) if isinstance(k, str) else k: v
                 for k, v in d.items()}
        return d

    # Special datetime constructs
    if isinstance(obj, datetime.time):
        return _time_to_json(obj)
    if isinstance(obj, datetime.datetime):
        return _datetime_to_json(obj)
    if isinstance(obj, datetime.date):
        return _date_to_json(obj)

    # Special enum constructs
    if isinstance(obj, Enum):
        return _enum_to_json(obj)

    # Special dataclass constructs
    if dataclasses.is_dataclass(obj):
        return _dataclass_to_json(obj, camel_case_keys=camel_case_keys)

    logger.warning('Unsupported type in jsonify: %s (%r)',
                   type_name(obj), obj)
    return obj


def unjsonify(json: JSONType, camel_case_keys: bool = True) -> Any:
    """
    "un-JSON-ify" object.

    Attemps to deserialise a previously "JSON-ified" Python object back
    to its original Python object state.

    :param json: "JSON-ified" object
    :param camel_case_keys: Use camelCase keys
    :return: Python object
    """
    _uj = functools.partial(unjsonify, camel_case_keys=camel_case_keys)

    # Return basic types as-is
    if isinstance(json, (str, int, float, bool)) or json is None:
        return json

    # Recursively process collections
    if isinstance(json, Sequence):
        return [_uj(j) for j in json]
    if isinstance(json, Mapping):
        mapping = {_uj(k): _uj(v) for k, v in json.items()}

        # Check if a special type, otherwise return as mapping
        module = mapping.pop(_MODULE_KEY, None)
        name = mapping.pop(_NAME_KEY, None)

        if module is None or name is None:
            if camel_case_keys:
                return {snake_case(k) if isinstance(k, str) else k: v
                        for k, v in mapping.items()}
            return mapping

        try:
            cls = getattr(importlib.import_module(module), name)
        except (ImportError, AttributeError) as e:
            raise ValueError(f'Could not locate: {module}.{name}') from e

        # If we explicitly have JSON deserialisation method, use it
        if isinstance(cls, type) and issubclass(cls, JSONMixin):
            return cls.from_json(mapping)

        # If we have an enum, get correct one
        if isinstance(cls, type) and issubclass(cls, Enum):
            return getattr(cls, mapping['name'])

        # Otherwise use as kwargs
        try:
            if camel_case_keys:
                return cls(**{snake_case(k) if isinstance(k, str) else k: v
                              for k, v in mapping.items()})
            return cls(**mapping)
        except (TypeError, ValueError) as e:
            raise ValueError(f'Bad arguments for {type_name(cls)}: {e}') from e

    logger.warning('Unsupported type in unjsonify: %s (%r)',
                   type_name(json), json)
    return json


def _date_to_json(date: datetime.date) -> JSON:
    return {
        _MODULE_KEY: datetime.date.__module__,
        _NAME_KEY: datetime.date.__name__,
        'year': date.year,
        'month': date.month,
        'day': date.day
    }


def _time_to_json(time: datetime.time) -> JSON:
    return {
        _MODULE_KEY: datetime.time.__module__,
        _NAME_KEY: datetime.time.__name__,
        'hour': time.hour,
        'minute': time.minute,
        'second': time.second,
        'microsecond': time.microsecond
    }


def _timezone_to_json(zone: datetime.tzinfo) -> JSON:
    if zone is datetime.timezone.utc:
        zone = pytz.utc
    if not isinstance(zone, pytz.BaseTzInfo):
        raise ValueError('Cannot serialise non-pytz timezones')
    return {
        _MODULE_KEY: pytz.timezone.__module__,
        _NAME_KEY: pytz.timezone.__name__,
        'zone': zone.zone
    }


def _enum_to_json(enum: Enum) -> JSON:
    return {
        _MODULE_KEY: type(enum).__module__,
        _NAME_KEY: type(enum).__name__,
        'name': enum.name
    }


def _datetime_to_json(dt: datetime.datetime) -> JSON:
    if dt.tzinfo is None:
        tz = None
    else:
        try:
            tz = _timezone_to_json(dt.tzinfo)
        except ValueError:
            logger.warning('Converting unknown timezone %r to UTC', dt.tzinfo)
            dt = dt.astimezone(pytz.utc)
            tz = _timezone_to_json(dt.tzinfo)
    return {
        _MODULE_KEY: datetime.datetime.__module__,
        _NAME_KEY: datetime.datetime.__name__,
        'year': dt.year,
        'month': dt.month,
        'day': dt.day,
        'hour': dt.hour,
        'minute': dt.minute,
        'second': dt.second,
        'microsecond': dt.microsecond,
        'tzinfo': tz
    }


def _dataclass_to_json(dataclass: dataclasses.dataclass,
                       camel_case_keys: bool = True) -> JSON:
    json = {camel_case(k) if camel_case_keys else k: jsonify(v)
            for k, v in dataclasses.asdict(dataclass).items()}
    json[_MODULE_KEY] = type(dataclass).__module__
    json[_NAME_KEY] = type(dataclass).__name__
    return json


class JSONMixin:
    """Dataclass mixin for JSON serialisation and deserialisation."""

    def to_json(self) -> JSON:
        """
        Generate serialisable JSON structure.

        :return: Serialisable JSON structure
        """
        self_dict = dataclasses.asdict(cast(dataclasses.dataclass, self))
        return {camel_case(k): v for k, v in self_dict.items()}

    @classmethod
    def from_json(cls: Type[T], json: JSON) -> T:
        """
        Deserialise original dataclass from JSON structure.

        :param json: Serialisable JSON structure
        :return: Deserialised original dataclass
        """
        return cls(**{snake_case(k): v for k, v in json.items()})


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
