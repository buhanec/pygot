"""Serialisation tests."""

from __future__ import annotations

import dataclasses
import datetime
from enum import Enum
from typing import Any, Optional, Type, TypeVar

import pytest
import pytz

from pygot import serialisation, utils

T = TypeVar('T')


@pytest.mark.parametrize('string, expected', [
    ('key', 'key'),
    ('keyWord', 'key_word'),
    ('KeyWord', 'key_word'),
    ('manyKeyWord', 'many_key_word'),
    ('duplicateKey_', 'duplicate_key_'),
    ('_secretKey', '_secret_key'),
    ('', ''),
    ('KEY', 'key'),
    ('one2three', 'one2three'),
    ('one2Three', 'one2_three'),
])
def test_snake_case(string: str, expected: str) -> None:
    assert serialisation.snake_case(string) == expected


@pytest.mark.parametrize('string', [
    'key!',
    'älen',
    'key word',
    'sophie@tan',
])
def test_snake_case_non_ascii(string: str) -> None:
    with pytest.raises(ValueError):
        serialisation.snake_case(string)


@pytest.mark.parametrize('string, expected', [
    ('key', 'key'),
    ('aaAAaaAAa', 'aaaaaaaaa'),
    ('key_word', 'keyWord'),
    ('key_Word', 'keyWord'),
    ('Key_Word', 'keyWord'),
    ('many_Key_word', 'manyKeyWord'),
    ('duplicate_key_', 'duplicateKey_'),
    ('_secret_key', '_secretKey'),
    ('', ''),
    ('KEY', 'key'),
    ('one_2_three', 'one2Three'),
    ('one_2three', 'one2three'),
])
def test_camel_case(string: str, expected: str) -> None:
    assert serialisation.camel_case(string) == expected


@pytest.mark.parametrize('string', [
    'key!',
    'älen',
    'key word',
    'sophie@tan',
])
def test_camel_case_non_ascii(string: str) -> None:
    with pytest.raises(ValueError):
        serialisation.camel_case(string)


@dataclasses.dataclass(frozen=True)
class DummyDataclass(serialisation.JSONMixin):
    """Dummy dataclass with JSON types."""

    int_var: int
    str_var: str
    float_var: float
    bool_var: bool
    optional_var: Optional[str]
    empty_var: Optional[str]
    default_var: str = 'abc'


def test_json_mixin_serialisation() -> None:
    dummy = DummyDataclass(int_var=123,
                           str_var='one two three',
                           float_var=1.23,
                           bool_var=True,
                           optional_var='I am here',
                           empty_var=None)

    expected_json = {
        'intVar': 123,
        'strVar': 'one two three',
        'floatVar': 1.23,
        'boolVar': True,
        'optionalVar': 'I am here',
        'emptyVar': None,
        'defaultVar': 'abc',
    }

    assert dummy.to_json() == expected_json


def test_json_mixin_deserialisation() -> None:
    dummy = DummyDataclass(int_var=123,
                           str_var='one two three',
                           float_var=1.23,
                           bool_var=True,
                           optional_var='I am here',
                           empty_var=None)

    expected_json = {
        'intVar': 123,
        'strVar': 'one two three',
        'floatVar': 1.23,
        'boolVar': True,
        'optionalVar': 'I am here',
        'emptyVar': None,
        'defaultVar': 'abc',
    }

    assert DummyDataclass.from_json(expected_json) == dummy


@dataclasses.dataclass(frozen=True)
class ReplaceDummyDataclass(serialisation.ReplaceMixin):
    """Dummy replaceable attribute dataclass type."""

    a: int
    b: str


def test_replace_mixin() -> None:
    a = ReplaceDummyDataclass(123, '123')
    a_ref = ReplaceDummyDataclass(123, '123')

    assert a == a_ref

    b = a.replace(a=321)
    b_ref = ReplaceDummyDataclass(321, '123')

    assert a == a_ref
    assert b == b_ref

    c = b.replace(a=123, b='321')
    c_ref = ReplaceDummyDataclass(123, '321')

    assert a == a_ref
    assert b == b_ref
    assert c == c_ref


class _CustomTZ(datetime.tzinfo):
    """Simple custom minute-based timezones."""

    def __init__(self, offset: int):
        self.offset = offset

    def tzname(self, _):
        if self.offset >= 0:
            return f'UTC+{self.offset}...minutes'
        return f'UTC-{self.offset}...minutes'

    def utcoffset(self, _):
        return datetime.timedelta(minutes=-self.offset)

    def dst(self, _):
        return 0

    def __eq__(self, other):
        return isinstance(other, _CustomTZ) and other.offset == self.offset


class _CustomEnum(Enum):
    """Custom timezone enum."""

    UTC_PLUS_10 = _CustomTZ(+10)
    UTC_MINUS_10 = _CustomTZ(-10)


@dataclasses.dataclass()
class _Dataclass:
    """Test case dataclass."""

    number: int
    text: str
    a_random_var: bool


@dataclasses.dataclass()
class _JsonDataclass(serialisation.JSONMixin, _Dataclass):
    """Test case dataclass."""

    def to_json(self) -> serialisation.JSON:
        return {'text': self.number,
                'number': self.text,
                'a': ['random_thing', {'var': self.a_random_var}]}

    @classmethod
    def from_json(cls: Type[T], json: serialisation.JSON) -> T:
        return cls(number=json['text'],
                   text=json['number'],
                   a_random_var=json['a'][1]['var'])


@pytest.mark.parametrize('obj, expected', [
    # Basic "JSON" types
    ('123', '123'),
    (123, 123),
    (123.0, 123.0),
    (True, True),
    (None, None),
    # Complex "JSON" types
    ({'str': '123', 'int': 123, 'float': 123.0, 'bool': False, 'null': None},
     {'str': '123', 'int': 123, 'float': 123.0, 'bool': False, 'null': None}),
    (['123', 123, 123.0, False, None], ['123', 123, 123.0, False, None]),
    ({'dict': {'one': 1, 'two': 2.0}, 'list': [True, False, None]},
     {'dict': {'one': 1, 'two': 2.0}, 'list': [True, False, None]}),
    ({'some_really': {'really': {'quite_nested': 'thing'}}},
     {'someReally': {'really': {'quiteNested': 'thing'}}}),
    # Datetimes
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682,
      'tzinfo': None}),
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682,
                       tzinfo=pytz.timezone('Europe/Ljubljana')),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682,
      'tzinfo': {'$module': 'pytz',
                 '$type': 'timezone',
                 'zone': 'Europe/Ljubljana'}}),
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682,
                       tzinfo=datetime.timezone.utc),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682,
      'tzinfo': {'$module': 'pytz',
                 '$type': 'timezone',
                 'zone': 'UTC'}}),
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682,
                       tzinfo=_CustomTZ(+10)),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 15,
      'second': 40,
      'microsecond': 682,
      'tzinfo': {'$module': 'pytz',
                 '$type': 'timezone',
                 'zone': 'UTC'}}),
    (datetime.date(2020, 4, 10),
     {'$module': 'datetime',
      '$type': 'date',
      'year': 2020,
      'month': 4,
      'day': 10}),
    (datetime.time(18, 5, 40, 682),
     {'$module': 'datetime',
      '$type': 'time',
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682}),
    # Test enum
    (_CustomEnum.UTC_MINUS_10, {'$module': _CustomEnum.__module__,
                                '$type': _CustomEnum.__name__,
                                'name': 'UTC_MINUS_10'}),
    # Dataclass
    (_Dataclass(number=123,
                text='abc',
                a_random_var=True),
     {'$module': _Dataclass.__module__,
      '$type': _Dataclass.__name__,
      'number': 123,
      'text': 'abc',
      'aRandomVar': True}),
    (_JsonDataclass(number=123,
                    text='abc',
                    a_random_var=True),
     {'$module': _JsonDataclass.__module__,
      '$type': _JsonDataclass.__name__,
      'number': 'abc',
      'text': 123,
      'a': ['random_thing', {'var': True}]}),
    # Unsupported types
    ({1, 2, 3}, {1, 2, 3}),
    (_CustomTZ(+10), _CustomTZ(+10)),
], ids=utils.type_name)
def test_jsonify(obj: Any, expected: Any) -> None:
    assert serialisation.jsonify(obj) == expected


@pytest.mark.parametrize('obj, expected', [
    # Basic "JSON" types
    ('123', '123'),
    (123, 123),
    (123.0, 123.0),
    (True, True),
    (None, None),
    # Complex "JSON" types
    ({'str': '123', 'int': 123, 'float': 123.0, 'bool': False, 'null': None},
     {'str': '123', 'int': 123, 'float': 123.0, 'bool': False, 'null': None}),
    (['123', 123, 123.0, False, None], ['123', 123, 123.0, False, None]),
    ({'dict': {'one': 1, 'two': 2.0}, 'list': [True, False, None]},
     {'dict': {'one': 1, 'two': 2.0}, 'list': [True, False, None]}),
    ({'someReally': {'really': {'quite_nested': 'thing'}}},
     {'someReally': {'really': {'quite_nested': 'thing'}}}),
    # Datetimes
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682,
      'tzinfo': None}),
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682,
                       tzinfo=pytz.timezone('Europe/Ljubljana')),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682,
      'tzinfo': {'$module': 'pytz',
                 '$type': 'timezone',
                 'zone': 'Europe/Ljubljana'}}),
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682,
                       tzinfo=datetime.timezone.utc),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682,
      'tzinfo': {'$module': 'pytz',
                 '$type': 'timezone',
                 'zone': 'UTC'}}),
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682,
                       tzinfo=_CustomTZ(+10)),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 15,
      'second': 40,
      'microsecond': 682,
      'tzinfo': {'$module': 'pytz',
                 '$type': 'timezone',
                 'zone': 'UTC'}}),
    (datetime.date(2020, 4, 10),
     {'$module': 'datetime',
      '$type': 'date',
      'year': 2020,
      'month': 4,
      'day': 10}),
    (datetime.time(18, 5, 40, 682),
     {'$module': 'datetime',
      '$type': 'time',
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682}),
    # Test enum
    (_CustomEnum.UTC_MINUS_10, {'$module': _CustomEnum.__module__,
                                '$type': _CustomEnum.__name__,
                                'name': 'UTC_MINUS_10'}),
    # Dataclass
    (_Dataclass(number=123,
                text='abc',
                a_random_var=True),
     {'$module': _Dataclass.__module__,
      '$type': _Dataclass.__name__,
      'number': 123,
      'text': 'abc',
      'a_random_var': True}),
    (_JsonDataclass(number=123,
                    text='abc',
                    a_random_var=True),
     {'$module': _JsonDataclass.__module__,
      '$type': _JsonDataclass.__name__,
      'number': 'abc',
      'text': 123,
      'a': ['random_thing', {'var': True}]}),
    # Unsupported types
    ({1, 2, 3}, {1, 2, 3}),
    (_CustomTZ(+10), _CustomTZ(+10)),
], ids=utils.type_name)
def test_jsonify_no_camel_case(obj: Any, expected: Any) -> None:
    assert serialisation.jsonify(obj, camel_case_keys=False) == expected


@pytest.mark.parametrize('expected, obj', [
    # Basic "JSON" types
    ('123', '123'),
    (123, 123),
    (123.0, 123.0),
    (True, True),
    (None, None),
    # Complex "JSON" types
    ({'str': '123', 'int': 123, 'float': 123.0, 'bool': False, 'null': None},
     {'str': '123', 'int': 123, 'float': 123.0, 'bool': False, 'null': None}),
    (['123', 123, 123.0, False, None], ['123', 123, 123.0, False, None]),
    ({'dict': {'one': 1, 'two': 2.0}, 'list': [True, False, None]},
     {'dict': {'one': 1, 'two': 2.0}, 'list': [True, False, None]}),
    ({'some_really': {'really': {'quite_nested': 'thing'}}},
     {'someReally': {'really': {'quiteNested': 'thing'}}}),
    # Datetimes
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682,
      'tzinfo': None}),
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682,
                       tzinfo=pytz.timezone('Europe/Ljubljana')),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682,
      'tzinfo': {'$module': 'pytz',
                 '$type': 'timezone',
                 'zone': 'Europe/Ljubljana'}}),
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682,
                       tzinfo=datetime.timezone.utc),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682,
      'tzinfo': {'$module': 'pytz',
                 '$type': 'timezone',
                 'zone': 'UTC'}}),
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682,
                       tzinfo=_CustomTZ(+10)),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 15,
      'second': 40,
      'microsecond': 682,
      'tzinfo': {'$module': 'pytz',
                 '$type': 'timezone',
                 'zone': 'UTC'}}),
    (datetime.date(2020, 4, 10),
     {'$module': 'datetime',
      '$type': 'date',
      'year': 2020,
      'month': 4,
      'day': 10}),
    (datetime.time(18, 5, 40, 682),
     {'$module': 'datetime',
      '$type': 'time',
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682}),
    # Test enum
    (_CustomEnum.UTC_MINUS_10, {'$module': _CustomEnum.__module__,
                                '$type': _CustomEnum.__name__,
                                'name': 'UTC_MINUS_10'}),
    # Dataclass
    (_Dataclass(number=123,
                text='abc',
                a_random_var=True),
     {'$module': _Dataclass.__module__,
      '$type': _Dataclass.__name__,
      'number': 123,
      'text': 'abc',
      'aRandomVar': True}),
    (_JsonDataclass(number=123,
                    text='abc',
                    a_random_var=True),
     {'$module': _JsonDataclass.__module__,
      '$type': _JsonDataclass.__name__,
      'number': 'abc',
      'text': 123,
      'a': ['random_thing', {'var': True}]}),
    # Unsupported types
    ({1, 2, 3}, {1, 2, 3}),
    (_CustomTZ(+10), _CustomTZ(+10)),
], ids=utils.type_name)
def test_unjsonify(obj: Any, expected: Any) -> None:
    assert serialisation.unjsonify(obj) == expected


@pytest.mark.parametrize('expected, obj', [
    # Basic "JSON" types
    ('123', '123'),
    (123, 123),
    (123.0, 123.0),
    (True, True),
    (None, None),
    # Complex "JSON" types
    ({'str': '123', 'int': 123, 'float': 123.0, 'bool': False, 'null': None},
     {'str': '123', 'int': 123, 'float': 123.0, 'bool': False, 'null': None}),
    (['123', 123, 123.0, False, None], ['123', 123, 123.0, False, None]),
    ({'dict': {'one': 1, 'two': 2.0}, 'list': [True, False, None]},
     {'dict': {'one': 1, 'two': 2.0}, 'list': [True, False, None]}),
    ({'someReally': {'really': {'quite_nested': 'thing'}}},
     {'someReally': {'really': {'quite_nested': 'thing'}}}),
    # Datetimes
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682,
      'tzinfo': None}),
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682,
                       tzinfo=pytz.timezone('Europe/Ljubljana')),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682,
      'tzinfo': {'$module': 'pytz',
                 '$type': 'timezone',
                 'zone': 'Europe/Ljubljana'}}),
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682,
                       tzinfo=datetime.timezone.utc),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682,
      'tzinfo': {'$module': 'pytz',
                 '$type': 'timezone',
                 'zone': 'UTC'}}),
    (datetime.datetime(2020, 4, 10, 18, 5, 40, 682,
                       tzinfo=_CustomTZ(+10)),
     {'$module': 'datetime',
      '$type': 'datetime',
      'year': 2020,
      'month': 4,
      'day': 10,
      'hour': 18,
      'minute': 15,
      'second': 40,
      'microsecond': 682,
      'tzinfo': {'$module': 'pytz',
                 '$type': 'timezone',
                 'zone': 'UTC'}}),
    (datetime.date(2020, 4, 10),
     {'$module': 'datetime',
      '$type': 'date',
      'year': 2020,
      'month': 4,
      'day': 10}),
    (datetime.time(18, 5, 40, 682),
     {'$module': 'datetime',
      '$type': 'time',
      'hour': 18,
      'minute': 5,
      'second': 40,
      'microsecond': 682}),
    # Test enum
    (_CustomEnum.UTC_MINUS_10, {'$module': _CustomEnum.__module__,
                                '$type': _CustomEnum.__name__,
                                'name': 'UTC_MINUS_10'}),
    # Dataclass
    (_Dataclass(number=123,
                text='abc',
                a_random_var=True),
     {'$module': _Dataclass.__module__,
      '$type': _Dataclass.__name__,
      'number': 123,
      'text': 'abc',
      'a_random_var': True}),
    (_JsonDataclass(number=123,
                    text='abc',
                    a_random_var=True),
     {'$module': _JsonDataclass.__module__,
      '$type': _JsonDataclass.__name__,
      'number': 'abc',
      'text': 123,
      'a': ['random_thing', {'var': True}]}),
    # Unsupported types
    ({1, 2, 3}, {1, 2, 3}),
    (_CustomTZ(+10), _CustomTZ(+10)),
], ids=utils.type_name)
def test_unjsonify_no_camel_case(obj: Any, expected: Any) -> None:
    assert serialisation.unjsonify(obj, camel_case_keys=False) == expected


@pytest.mark.parametrize('obj', [
    # No such module
    {'$module': 'string',
     '$type': 'lalalalalala'},
    # Incorrect args
    {'$module': 'datetime',
     '$type': 'date',
     'year': 2020,
     'month': 2020,
     'day': 2020},
    # Not even args
    {'$module': 'datetime',
     '$type': 'time',
     14: 'hour',
     10: 'minute'},
], ids=utils.type_name)
def test_unjsonify_bad_args(obj: Any) -> None:
    with pytest.raises(ValueError):
        serialisation.unjsonify(obj)
    with pytest.raises(ValueError):
        serialisation.unjsonify(obj, camel_case_keys=False)
