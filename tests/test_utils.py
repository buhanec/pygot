"""Test common game model machinery."""

from __future__ import annotations

from typing import List, Optional, Union, Any

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
], ids=lambda a: repr(a))
def test_is_optional(obj: Any, expected: bool) -> None:
    assert utils.is_optional(obj) == expected


@pytest.mark.parametrize('obj, expected', [
    (Optional[str], str),
    (Optional[int], int),
    (Optional[List[int]], List[int]),
], ids=lambda a: repr(a))
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


def _test():
    class Test:
        pass
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
], ids=lambda a: repr(a))
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
], ids=lambda a: repr(a))
def test_type_name_qualname(obj: Any, expected: str) -> None:
    assert utils.type_name(obj, local_name=True) == expected
