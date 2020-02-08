"""Test common game model machinery."""

from __future__ import annotations

import itertools
from typing import Any, List, Optional, Union, Type

import pytest

from pygot import utils


@pytest.mark.parametrize('obj, expected', [
    (Optional, True),
    (Optional[str], True),
    (Optional[Optional[str]], True),
    (Union[str, None], True),
    (Union[None, str], True),
    (Union[str, None, None], True),
    (Union[None, None, str], True),
    (Union[Optional[str], None], True),
    (Union[Optional[str]], True),
    (Union[str, int], False),
    (Union[str, int], False),
    (Union[Optional[str], int], False),
    (Union[None], False),
    (Union, False),
    (str, False),
    (List[str], False),
    (type('A', tuple(), dict()), False),
    (type('Optional', tuple(), dict()), False),
], ids=repr)
def test_is_optional(obj: Any, expected: bool) -> None:
    assert utils.is_optional(obj) == expected


@pytest.mark.parametrize('obj, expected', [
    (Optional[str], str),
    (Optional[int], int),
    (Optional[List[int]], List[int]),
], ids=repr)
def test_optional_subtype(obj: Any, expected: Any) -> None:
    assert utils.optional_subtype(obj) == expected


@pytest.mark.parametrize('obj', [
    Optional,
    Union[int, str],
    int,
    str,
    None,
])
def test_optional_subtype_raises(obj: Any) -> None:
    with pytest.raises(ValueError):
        utils.optional_subtype(obj)


def _test() -> Type[Any]:
    """Test case function."""
    # pylint: disable=too-few-public-methods
    class Test:
        """Test case class."""
    return Test


@pytest.mark.parametrize('obj, expected', [
    (Optional[int], 'typing.Optional[int]'),
    (List[int], 'typing.List[int]'),
    (str, 'str'),
    (int, 'int'),
    ('123', 'str'),
    (123, 'int'),
    (type('Local', tuple(), {}), f'{__name__}.Local'),
    (_test, f'{__name__}._test'),
    (_test(), f'{__name__}._test.<locals>.Test'),
    (Optional, 'typing.Optional[Any]'),
], ids=repr)
def test_type_name(obj: Any, expected: str) -> None:
    assert utils.type_name(obj) == expected


@pytest.mark.parametrize('obj, expected', [
    (Optional[int], 'typing.Optional[int]'),
    (List[int], 'typing.List[int]'),
    (str, 'str'),
    (int, 'int'),
    ('123', 'str'),
    (123, 'int'),
    (type('Local', tuple(), {}), f'{__name__}.Local'),
    (_test, f'{__name__}._test'),
    (_test(), f'{__name__}.Test'),
    (Optional, 'typing.Optional[Any]'),
], ids=repr)
def test_type_name_qualname(obj: Any, expected: str) -> None:
    assert utils.type_name(obj, local_name=True) == expected


def test_random_ids() -> None:
    random_ids = set()
    for _ in range(1000):
        random_id, random_name = utils.random_id()
        assert utils.id_to_name(random_id) == random_name
        assert utils.name_to_id(random_name) == random_id
        random_ids.add(random_id)

    # Not a measure of uniquness, just to ensure we are not spitting
    # same ID out all the time
    assert len(random_ids) > 500


def test_good_ids() -> None:
    names = set()
    for n in range(1000):
        names.add(utils.id_to_name(n))
    assert len(names) == 1000


@pytest.mark.parametrize('name, expected_id', [
    ['good-red-lion', 0],
    ['shiny-white-manticore', 999],
    ['big-black-snake', 584],
])
def test_good_names(name: str, expected_id: int) -> None:
    assert utils.name_to_id(name) == expected_id


def test_bad_ids() -> None:
    for n in itertools.chain(range(-100, 0), range(1000, 1100)):
        with pytest.raises(ValueError):
            utils.id_to_name(n)


@pytest.mark.parametrize('name', [
    'bad-shiny-lion',
    'good-red-pink-bat',
    'fat-moose',
    'random-words-here',
])
def test_bad_name(name: str) -> None:
    with pytest.raises(ValueError):
        utils.name_to_id(name)
