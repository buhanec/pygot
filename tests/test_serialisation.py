"""Serialisation tests."""

from __future__ import annotations

import dataclasses
from typing import Optional

import pytest

from pygot.models import serialisation


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


def test_json_mixin_serialisation():
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


def test_json_mixin_deserialisation():
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


def test_replace_mixin():
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
