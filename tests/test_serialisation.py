"""Serialisation tests."""

from __future__ import annotations

import dataclasses
import datetime
from enum import Enum
import math
from typing import Any, Dict, List, Mapping, Optional, Sequence, Type, TypeVar
from unittest import mock

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
        return datetime.timedelta(minutes=self.offset)

    def dst(self, _):
        return None

    def __eq__(self, other):
        return isinstance(other, _CustomTZ) and other.offset == self.offset


class _CustomEnum(Enum):
    """Custom timezone enum."""

    UTC_PLUS_10 = {'some_time': datetime.time(12, 13, 00, 456789)}
    UTC_MINUS_10 = {'some_time': datetime.time(12, 13, 00, 456789)}


@dataclasses.dataclass()
class _Dataclass:
    """Test case dataclass."""

    number: int
    text: str
    a_random_var: bool


@dataclasses.dataclass()
class _DataDict:
    """Test case dataclass."""

    dict: Dict[str, int]
    data: _Dataclass


@dataclasses.dataclass()
class _JsonDataclass(serialisation.JSONMixin, _Dataclass):
    """Test case dataclass."""

    def to_json(self) -> serialisation.JSON:
        return {'text': self.number,
                'number': self.text,
                'a': [{'random_var': self.a_random_var}]}

    @classmethod
    def from_json(cls: Type[T], json: serialisation.JSON) -> T:
        return cls(number=json['text'],
                   text=json['number'],
                   a_random_var=json['a'][0]['random_var'])


# Mapping of test case ID -> [py, vanilla, camel case, camel case + meta, meta]
_TEST_CASES: Dict[str, List[Any]] = {
    'string': [
        'abc',
        'abc',
        'abc',
        'abc',
        'abc',
    ],
    'int-pos': [
        123,
        123,
        123,
        123,
        123,
    ],
    'int-zero': [
        0,
        0,
        0,
        0,
        0,
    ],
    'int-neg': [
        -123,
        -123,
        -123,
        -123,
        -123,
    ],
    'float-pos': [
        123.0,
        123.0,
        123.0,
        123.0,
        123.0,
    ],
    'float-zero': [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    ],
    'float-neg-zero': [
        -0.0,
        -0.0,
        -0.0,
        -0.0,
        -0.0,
    ],
    'float-neg': [
        -123.0,
        -123.0,
        -123.0,
        -123.0,
        -123.0,
    ],
    'float-nan': [
        float('nan'),
        'nan',
        'nan',
        {'$module': float.__module__,
         '$type': float.__name__,
         'x': 'nan'},
        {'$module': float.__module__,
         '$type': float.__name__,
         'x': 'nan'},
    ],
    'float-inf': [
        float('inf'),
        '+inf',
        '+inf',
        {'$module': float.__module__,
         '$type': float.__name__,
         'x': '+inf'},
        {'$module': float.__module__,
         '$type': float.__name__,
         'x': '+inf'},
    ],
    'float-neg-inf': [
        -float('inf'),
        '-inf',
        '-inf',
        {'$module': float.__module__,
         '$type': float.__name__,
         'x': '-inf'},
        {'$module': float.__module__,
         '$type': float.__name__,
         'x': '-inf'},
    ],
    'bool-true': [
        True,
        True,
        True,
        True,
        True,
    ],
    'bool-false': [
        False,
        False,
        False,
        False,
        False,
    ],
    'sequence-float': [
        [-float('inf'), -123.0, -0.0, 0.0, 123.0, float('inf')],
        ['-inf', -123.0, -0.0, 0.0, 123.0, '+inf'],
        ['-inf', -123.0, -0.0, 0.0, 123.0, '+inf'],
        [{'$module': float.__module__,
          '$type': float.__name__,
          'x': '-inf'},
         -123.0, -0.0, 0.0, 123.0,
         {'$module': float.__module__,
          '$type': float.__name__,
          'x': '+inf'},
         ],
        [{'$module': float.__module__,
          '$type': float.__name__,
          'x': '-inf'},
         -123.0, -0.0, 0.0, 123.0,
         {'$module': float.__module__,
          '$type': float.__name__,
          'x': '+inf'},
         ],
    ],
    'sequence-nested-int': [
        [[-1, 0, 1], [-2, 0, 2]],
        [[-1, 0, 1], [-2, 0, 2]],
        [[-1, 0, 1], [-2, 0, 2]],
        [[-1, 0, 1], [-2, 0, 2]],
        [[-1, 0, 1], [-2, 0, 2]],
    ],
    'dict-int': [
        {'a_cat': 1, 'b_yourself': 2, 'c_the_sea': 3},
        {'a_cat': 1, 'b_yourself': 2, 'c_the_sea': 3},
        {'aCat': 1, 'bYourself': 2, 'cTheSea': 3},
        {'a_cat': 1, 'b_yourself': 2, 'c_the_sea': 3},
        {'aCat': 1, 'bYourself': 2, 'cTheSea': 3},
    ],
    'sequence-nested-dict': [
        [{'nested_key': 123,
          'other_nested_key': {'super_nested': float('nan')}}],
        [{'nested_key': 123, 'other_nested_key': {'super_nested': 'nan'}}],
        [{'nestedKey': 123, 'otherNestedKey': {'superNested': 'nan'}}],
        [{'nested_key': 123,
          'other_nested_key': {'super_nested': {'$module': float.__module__,
                                                '$type': float.__name__,
                                                'x': 'nan'}}}],
        [{'nestedKey': 123,
          'otherNestedKey': {'superNested': {'$module': float.__module__,
                                             '$type': float.__name__,
                                             'x': 'nan'}}}],
    ],
    'datetime-utc': [
        datetime.datetime(2020, 4, 29, 14, 15, 16, 789, pytz.utc),
        '2020-04-29T14:15:16.000789+0000',
        '2020-04-29T14:15:16.000789+0000',
        {'$module': serialisation.date_time.__module__,
         '$type': serialisation.date_time.__name__,
         'year': 2020,
         'month': 4,
         'day': 29,
         'hour': 14,
         'minute': 15,
         'second': 16,
         'microsecond': 789,
         'timezone': 'UTC'},
        {'$module': serialisation.date_time.__module__,
         '$type': serialisation.date_time.__name__,
         'year': 2020,
         'month': 4,
         'day': 29,
         'hour': 14,
         'minute': 15,
         'second': 16,
         'microsecond': 789,
         'timezone': 'UTC'},
    ],
    'datetime-ljubljana': [
        pytz.timezone('Europe/Ljubljana').localize(
            datetime.datetime(2020, 4, 29, 14, 15, 16, 789)),
        '2020-04-29T14:15:16.000789+0200',
        '2020-04-29T14:15:16.000789+0200',
        {'$module': serialisation.date_time.__module__,
         '$type': serialisation.date_time.__name__,
         'year': 2020,
         'month': 4,
         'day': 29,
         'hour': 14,
         'minute': 15,
         'second': 16,
         'microsecond': 789,
         'timezone': 'Europe/Ljubljana'},
        {'$module': serialisation.date_time.__module__,
         '$type': serialisation.date_time.__name__,
         'year': 2020,
         'month': 4,
         'day': 29,
         'hour': 14,
         'minute': 15,
         'second': 16,
         'microsecond': 789,
         'timezone': 'Europe/Ljubljana'},
    ],
    'datetime-no-tz': [
        datetime.datetime(2020, 4, 29, 14, 15, 16, 789),
        '2020-04-29T14:15:16.000789',
        '2020-04-29T14:15:16.000789',
        {'$module': serialisation.date_time.__module__,
         '$type': serialisation.date_time.__name__,
         'year': 2020,
         'month': 4,
         'day': 29,
         'hour': 14,
         'minute': 15,
         'second': 16,
         'microsecond': 789,
         'timezone': None},
        {'$module': serialisation.date_time.__module__,
         '$type': serialisation.date_time.__name__,
         'year': 2020,
         'month': 4,
         'day': 29,
         'hour': 14,
         'minute': 15,
         'second': 16,
         'microsecond': 789,
         'timezone': None},
    ],
    'datetime-native-utc': [
        datetime.datetime(2020, 4, 29, 14, 15, 16, 789, datetime.timezone.utc),
        '2020-04-29T14:15:16.000789+0000',
        '2020-04-29T14:15:16.000789+0000',
        {'$module': serialisation.date_time.__module__,
         '$type': serialisation.date_time.__name__,
         'year': 2020,
         'month': 4,
         'day': 29,
         'hour': 14,
         'minute': 15,
         'second': 16,
         'microsecond': 789,
         'timezone': 'UTC'},
        {'$module': serialisation.date_time.__module__,
         '$type': serialisation.date_time.__name__,
         'year': 2020,
         'month': 4,
         'day': 29,
         'hour': 14,
         'minute': 15,
         'second': 16,
         'microsecond': 789,
         'timezone': 'UTC'},
    ],
    'datetime-native-custom-tz': [
        datetime.datetime(2020, 4, 29, 14, 15, 16, 789, _CustomTZ(+10)),
        '2020-04-29T14:15:16.000789+0010',
        '2020-04-29T14:15:16.000789+0010',
        {'$module': serialisation.date_time.__module__,
         '$type': serialisation.date_time.__name__,
         'year': 2020,
         'month': 4,
         'day': 29,
         'hour': 14,
         'minute': 5,
         'second': 16,
         'microsecond': 789,
         'timezone': 'UTC'},
        {'$module': serialisation.date_time.__module__,
         '$type': serialisation.date_time.__name__,
         'year': 2020,
         'month': 4,
         'day': 29,
         'hour': 14,
         'minute': 5,
         'second': 16,
         'microsecond': 789,
         'timezone': 'UTC'},
    ],
    'date': [
        datetime.date(1969, 6, 9),
        '1969-06-09',
        '1969-06-09',
        {'$module': datetime.date.__module__,
         '$type': datetime.date.__name__,
         'year': 1969,
         'month': 6,
         'day': 9},
        {'$module': datetime.date.__module__,
         '$type': datetime.date.__name__,
         'year': 1969,
         'month': 6,
         'day': 9},
    ],
    'time': [
        datetime.time(12, 34, 56, 789),
        '12:34:56.000789',
        '12:34:56.000789',
        {'$module': datetime.time.__module__,
         '$type': datetime.time.__name__,
         'hour': 12,
         'minute': 34,
         'second': 56,
         'microsecond': 789},
        {'$module': datetime.time.__module__,
         '$type': datetime.time.__name__,
         'hour': 12,
         'minute': 34,
         'second': 56,
         'microsecond': 789},
    ],
    'dataclass': [
        _Dataclass(number=123,
                   text='abc',
                   a_random_var=True),
        {'number': 123,
         'text': 'abc',
         'a_random_var': True},
        {'number': 123,
         'text': 'abc',
         'aRandomVar': True},
        {'$module': _Dataclass.__module__,
         '$type': _Dataclass.__name__,
         'number': 123,
         'text': 'abc',
         'a_random_var': True},
        {'$module': _Dataclass.__module__,
         '$type': _Dataclass.__name__,
         'number': 123,
         'text': 'abc',
         'aRandomVar': True},
    ],
    'dataclass-nested': [
        _DataDict(dict={'a_int': 1, 'b_float': -0.0},
                  data=_Dataclass(number=1,
                                  text='str',
                                  a_random_var=False)),
        {'dict': {'a_int': 1, 'b_float': -0.0},
         'data': {'number': 1, 'text': 'str', 'a_random_var': False}},
        {'dict': {'aInt': 1, 'bFloat': -0.0},
         'data': {'number': 1, 'text': 'str', 'aRandomVar': False}},
        {'$module': _DataDict.__module__,
         '$type': _DataDict.__name__,
         'dict': {'a_int': 1, 'b_float': -0.0},
         'data': {'$module': _Dataclass.__module__,
                  '$type': _Dataclass.__name__,
                  'number': 1,
                  'text': 'str',
                  'a_random_var': False}},
        {'$module': _DataDict.__module__,
         '$type': _DataDict.__name__,
         'dict': {'aInt': 1, 'bFloat': -0.0},
         'data': {'$module': _Dataclass.__module__,
                  '$type': _Dataclass.__name__,
                  'number': 1,
                  'text': 'str',
                  'aRandomVar': False}},
    ],
    'enum': [
        _CustomEnum.UTC_MINUS_10,
        f'{utils.type_name(_CustomEnum)}.{_CustomEnum.UTC_MINUS_10.name}',
        f'{utils.type_name(_CustomEnum)}.{_CustomEnum.UTC_MINUS_10.name}',
        {'$module': _CustomEnum.__module__,
         '$type': _CustomEnum.__name__,
         'name': _CustomEnum.UTC_MINUS_10.name,
         'value': {'some_time': {'$module': datetime.time.__module__,
                                 '$type': datetime.time.__name__,
                                 'hour': 12,
                                 'minute': 13,
                                 'second': 00,
                                 'microsecond': 456789}}},
        {'$module': _CustomEnum.__module__,
         '$type': _CustomEnum.__name__,
         'name': _CustomEnum.UTC_MINUS_10.name,
         'value': {'someTime': {'$module': datetime.time.__module__,
                                '$type': datetime.time.__name__,
                                'hour': 12,
                                'minute': 13,
                                'second': 00,
                                'microsecond': 456789}}}
    ],
    'jsonmixin': [
        _JsonDataclass(number=1, text='text', a_random_var=True),
        {'text': 1,
         'number': 'text',
         'a': [{'random_var': True}]},
        {'text': 1,
         'number': 'text',
         'a': [{'random_var': True}]},
        {'$module': _JsonDataclass.__module__,
         '$type': _JsonDataclass.__name__,
         'text': 1,
         'number': 'text',
         'a': [{'random_var': True}]},
        {'$module': _JsonDataclass.__module__,
         '$type': _JsonDataclass.__name__,
         'text': 1,
         'number': 'text',
         'a': [{'random_var': True}]},
    ],
    'unsupported-set': [
        {1, 2, 3},
        {1, 2, 3},
        {1, 2, 3},
        {1, 2, 3},
        {1, 2, 3},
    ],
    'unsupported-tz': [
        _CustomTZ(+15),
        _CustomTZ(+15),
        _CustomTZ(+15),
        _CustomTZ(+15),
        _CustomTZ(+15),
    ]
}

_EXCEPTIONAL_CASES = {
    'bad-class': [{'$module': 'datetime',
                   '$type': 'foo_bar',
                   'year': 2020,
                   'month': 4,
                   'day': 29}, ValueError],
    'bad-args': [{'$module': 'datetime',
                  '$type': 'date',
                  'year': 2020,
                  'month': 4,
                  'day': 29,
                  'planet': 'Earth'}, ValueError],
}

_FakeNan = type('nan', tuple(), dict())


def _replace_nan(obj: Any) -> Any:
    if isinstance(obj, float) and math.isnan(obj):
        return _FakeNan
    if isinstance(obj, Mapping):
        return {_replace_nan(k): _replace_nan(v)
                for k, v in obj.items()}
    if not isinstance(obj, str) and isinstance(obj, Sequence):
        return [_replace_nan(v) for v in obj]
    return obj


@pytest.mark.parametrize('obj, expected',
                         [(x[0], x[1]) for x in _TEST_CASES.values()],
                         ids=list(_TEST_CASES))
def test_jsonify_snake_simple(obj: Any, expected: Any) -> None:
    val = serialisation.jsonify(obj, camel_case_keys=False, arg_struct=False)
    try:
        assert val == expected
    except AssertionError:
        pass
    else:
        return
    assert _replace_nan(val) == _replace_nan(expected)


@pytest.mark.parametrize('obj, expected',
                         [(x[0], x[2]) for x in _TEST_CASES.values()],
                         ids=list(_TEST_CASES))
def test_jsonify_camel_simple(obj: Any, expected: Any) -> None:
    val = serialisation.jsonify(obj, camel_case_keys=True, arg_struct=False)
    try:
        assert val == expected
    except AssertionError:
        pass
    else:
        return
    assert _replace_nan(val) == _replace_nan(expected)


@pytest.mark.parametrize('obj, expected',
                         [(x[0], x[3]) for x in _TEST_CASES.values()],
                         ids=list(_TEST_CASES))
def test_jsonify_snake_meta(obj: Any, expected: Any) -> None:
    val = serialisation.jsonify(obj, camel_case_keys=False, arg_struct=True)
    try:
        assert val == expected
    except AssertionError:
        pass
    else:
        return
    assert _replace_nan(val) == _replace_nan(expected)


@pytest.mark.parametrize('obj, expected',
                         [(x[0], x[4]) for x in _TEST_CASES.values()],
                         ids=list(_TEST_CASES))
def test_jsonify_camel_meta(obj: Any, expected: Any) -> None:
    val = serialisation.jsonify(obj, camel_case_keys=True, arg_struct=True)
    try:
        assert val == expected
    except AssertionError:
        pass
    else:
        return
    assert _replace_nan(val) == _replace_nan(expected)


@pytest.mark.parametrize('obj, expected',
                         [(x[0], x[4]) for x in _TEST_CASES.values()],
                         ids=list(_TEST_CASES))
def test_jsonify(obj: Any, expected: Any) -> None:
    val = serialisation.jsonify(obj)
    try:
        assert val == expected
    except AssertionError:
        pass
    else:
        return
    assert _replace_nan(val) == _replace_nan(expected)


@pytest.mark.parametrize('obj, expected',
                         [(x[3], x[0]) for i, x in _TEST_CASES.items()],
                         ids=list(_TEST_CASES))
def test_unjsonify_snake(obj: Any, expected: Any) -> None:
    val = serialisation.unjsonify(obj, camel_case_keys=False)
    try:
        assert val == expected
    except AssertionError:
        pass
    else:
        return
    assert _replace_nan(val) == _replace_nan(expected)


@pytest.mark.parametrize('obj, expected',
                         [(x[4], x[0]) for i, x in _TEST_CASES.items()],
                         ids=list(_TEST_CASES))
def test_unjsonify_camel(obj: Any, expected: Any) -> None:
    val = serialisation.unjsonify(obj, camel_case_keys=True)
    try:
        assert val == expected
    except AssertionError:
        pass
    else:
        return
    assert _replace_nan(val) == _replace_nan(expected)


@pytest.mark.parametrize('obj, expected',
                         [(x[4], x[0]) for i, x in _TEST_CASES.items()],
                         ids=list(_TEST_CASES))
def test_unjsonify(obj: Any, expected: Any) -> None:
    val = serialisation.unjsonify(obj)
    try:
        assert val == expected
    except AssertionError:
        pass
    else:
        return
    assert _replace_nan(val) == _replace_nan(expected)


@pytest.mark.parametrize('obj, expected',
                         _EXCEPTIONAL_CASES.values(),
                         ids=list(_EXCEPTIONAL_CASES))
def test_unjsonify_snake_raises(obj: Any, expected: Any) -> None:
    with pytest.raises(expected):
        serialisation.unjsonify(obj, camel_case_keys=False)


@pytest.mark.parametrize('obj, expected',
                         _EXCEPTIONAL_CASES.values(),
                         ids=list(_EXCEPTIONAL_CASES))
def test_unjsonify_camel_raises(obj: Any, expected: Any) -> None:
    with pytest.raises(expected):
        serialisation.unjsonify(obj, camel_case_keys=True)


@pytest.mark.parametrize('obj, expected',
                         _EXCEPTIONAL_CASES.values(),
                         ids=list(_EXCEPTIONAL_CASES))
def test_unjsonify_raises(obj: Any, expected: Any) -> None:
    with pytest.raises(expected):
        serialisation.unjsonify(obj)


@mock.patch('orjson.dumps', return_value=b'123')
@mock.patch('pygot.serialisation.jsonify', return_value=123)
def test_orjson_response(serialisation_jsonify: mock.MagicMock,
                         orjson_dumps: mock.MagicMock) -> None:
    serialisation.ORJSONResponse(321)

    assert serialisation_jsonify.call_count == 1
    assert serialisation_jsonify.call_args == ((321,), {})

    assert orjson_dumps.call_count == 1
    assert orjson_dumps.call_args == ((123,), {})
