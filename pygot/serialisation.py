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
import math
from string import ascii_letters, digits
from typing import (Any, Dict, List, Mapping, Optional, Sequence, Type,
                    TypeVar, Union, cast)

import orjson
import pytz
from starlette.responses import JSONResponse

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


# We have dispatcher functions that may not use all arguments.
# pylint: disable=unused-argument


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


@functools.singledispatch
def jsonify(obj: Any,
            camel_case_keys: bool = True,
            arg_struct: bool = True) -> JSONType:
    """
    "JSON-ify" object.

    Attemps to serialise Python object in a fashion that would make
    JSON serialisation and deserialisation easier.

    :param obj: Python object
    :param camel_case_keys: Use camelCase keys
    :param arg_struct: Provide structure with arguments for re-creation
    :return: "JSON-ified" object
    """
    if dataclasses.is_dataclass(obj):
        return _jsonify_dataclass(obj,
                                  camel_case_keys=camel_case_keys,
                                  arg_struct=arg_struct)
    logger.warning('Unsupported type in jsonify: %s (%r)',
                   type_name(obj), obj)
    return obj


@jsonify.register
def _jsonify_jsonmixin(obj: JSONMixin,
                       camel_case_keys: bool = True,
                       arg_struct: bool = True) -> JSONType:
    json = obj.to_json()
    if arg_struct:
        json[_MODULE_KEY] = type(obj).__module__
        json[_NAME_KEY] = type(obj).__name__
    return json


@jsonify.register
def _jsonify_float(obj: float,
                   camel_case_keys: bool = True,
                   arg_struct: bool = True) -> JSONType:
    if math.isinf(obj):
        if obj > 0:
            replacement = '+inf'
        else:
            replacement = '-inf'
    elif math.isnan(obj):
        replacement = 'nan'
    else:
        return obj
    if arg_struct and isinstance(replacement, str):
        return {_MODULE_KEY: float.__module__,
                _NAME_KEY: float.__name__,
                'x': replacement}
    return replacement


@jsonify.register(list)
@jsonify.register(tuple)
def _jsonify_sequence(obj: Sequence[Any],
                      camel_case_keys: bool = True,
                      arg_struct: bool = True) -> JSONType:
    return [jsonify(o,
                    camel_case_keys=camel_case_keys,
                    arg_struct=arg_struct) for o in obj]


@jsonify.register(dict)
def _jsonify_mapping(obj: Mapping[str, Any],
                     camel_case_keys: bool = True,
                     arg_struct: bool = True) -> JSONType:
    _j = functools.partial(jsonify,
                           camel_case_keys=camel_case_keys,
                           arg_struct=arg_struct)
    d = {_j(k): _j(v) for k, v in obj.items()}
    if camel_case_keys:
        d = {camel_case(k) if isinstance(k, str) else k: v
             for k, v in d.items()}
    return d


def date_time(year: int,
              month: int,
              day: int,
              hour: int,
              minute: int,
              second: int,
              microsecond: int,
              timezone: Optional[str]) -> datetime.datetime:
    """
    Create `date.datetime` object using meta form.

    :param year: Year
    :param month: Month
    :param day: Day
    :param hour: Hour
    :param minute: Minute
    :param second: Second
    :param microsecond: Microsecond
    :param timezone: Timezone
    :return: `datetime.date` instance
    """
    dt = datetime.datetime(year=year,
                           month=month,
                           day=day,
                           hour=hour,
                           minute=minute,
                           second=second,
                           microsecond=microsecond)
    if timezone is None:
        return dt
    return pytz.timezone(timezone).localize(dt)


@jsonify.register
def _jsonify_datetime(obj: datetime.datetime,
                      camel_case_keys: bool = True,
                      arg_struct: bool = True) -> JSONType:
    if not arg_struct:
        return obj.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    if obj.tzinfo is datetime.timezone.utc:
        obj = obj.replace(tzinfo=pytz.utc)
    if obj.tzinfo is not None and not isinstance(obj.tzinfo, pytz.BaseTzInfo):
        logger.warning('Converting unknown timezone %r to UTC', obj.tzinfo)
        obj = obj.astimezone(pytz.utc)
    return {
        _MODULE_KEY: date_time.__module__,
        _NAME_KEY: date_time.__name__,
        'year': obj.year,
        'month': obj.month,
        'day': obj.day,
        'hour': obj.hour,
        'minute': obj.minute,
        'second': obj.second,
        'microsecond': obj.microsecond,
        'timezone': obj.tzinfo.zone if obj.tzinfo else None,
    }


@jsonify.register
def _jsonify_date(obj: datetime.date,
                  camel_case_keys: bool = True,
                  arg_struct: bool = True) -> JSONType:
    if not arg_struct:
        return obj.isoformat()
    return {
        _MODULE_KEY: datetime.date.__module__,
        _NAME_KEY: datetime.date.__name__,
        'year': obj.year,
        'month': obj.month,
        'day': obj.day
    }


@jsonify.register
def _jsonify_time(obj: datetime.time,
                  camel_case_keys: bool = True,
                  arg_struct: bool = True) -> JSONType:
    if not arg_struct:
        return obj.strftime('%H:%M:%S.%f')
    return {
        _MODULE_KEY: datetime.time.__module__,
        _NAME_KEY: datetime.time.__name__,
        'hour': obj.hour,
        'minute': obj.minute,
        'second': obj.second,
        'microsecond': obj.microsecond
    }


@jsonify.register
def _jsonify_enum(obj: Enum,
                  camel_case_keys: bool = True,
                  arg_struct: bool = True) -> JSONType:
    if not arg_struct:
        return f'{type_name(obj)}.{obj.name}'
    return {
        _MODULE_KEY: type(obj).__module__,
        _NAME_KEY: type(obj).__name__,
        'name': obj.name,
        'value': jsonify(obj.value,
                         camel_case_keys=camel_case_keys,
                         arg_struct=arg_struct),
    }


def _jsonify_dataclass(obj: dataclasses.dataclass,
                       camel_case_keys: bool = True,
                       arg_struct: bool = True) -> JSONType:
    d = {}
    for f in dataclasses.fields(obj):
        if camel_case_keys:
            k = camel_case(f.name)
        else:
            k = f.name
        v = getattr(obj, f.name)
        d[k] = jsonify(v,
                       camel_case_keys=camel_case_keys,
                       arg_struct=arg_struct)
    if arg_struct:
        d[_MODULE_KEY] = type(obj).__module__
        d[_NAME_KEY] = type(obj).__name__
    return d


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

        # Float takes no keyword args
        if cls is float:
            return float(mapping['x'])

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


class ReplaceMixin:
    """
    Allows for immutable instance creation using replacement values.

    TODO: Why is this here?
    """

    def replace(self: T, **kwargs: Any) -> T:
        """
        Create new instance with replaced attribute values.

        :param kwargs: Replacement attribute values
        :return: New instance with replaced values
        """
        new_kwargs = dataclasses.asdict(self)
        new_kwargs.update(kwargs)
        return type(self)(**new_kwargs)


class ORJSONResponse(JSONResponse):
    """JSON response using orjson and serialisation."""

    media_type = 'application/json'

    def render(self, content: Any) -> bytes:
        return orjson.dumps(jsonify(content))
