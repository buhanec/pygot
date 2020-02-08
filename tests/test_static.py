"""Test static models."""

from __future__ import annotations

__all__ = tuple()

from typing import cast

from _pytest.fixtures import FixtureRequest
import pytest

from pygot import static

# Fixtures. Need to make a PR for this.
# pylint: disable=unused-argument,redefined-outer-name

# Dummy classes
# pylint: disable=function-redefined,too-few-public-methods,unused-variable


@pytest.fixture(scope='function')
def reset_metaclass(request: FixtureRequest):
    """Ensure StaticMeta has clean registry and correct root."""
    __root__ = static.StaticMeta.__root__
    __registry__ = static.StaticMeta.__registry__.copy()

    def _fin():
        static.StaticMeta.__root__ = __root__
        static.StaticMeta.__registry__ = __registry__

    request.addfinalizer(_fin)


def test_name_conflict(reset_metaclass):
    class Name123(static.StaticEnum):
        """Test enum."""

    original = Name123

    with pytest.raises(static.StaticNameConflict):
        class Name123(static.StaticEnum):
            """Test enum."""

    assert static.StaticMeta.get('name123') is original


def test_single_root(reset_metaclass):
    with pytest.raises(TypeError):
        class Name123(metaclass=static.StaticMeta):
            """Test enum."""


def test_get_name(reset_metaclass):
    class Name123(static.StaticEnum):
        """Test enum."""

    class SomeOtherName(static.StaticEnum):
        """Test enum."""

    with pytest.raises(ValueError):
        static.StaticMeta.get('staticenum')
    with pytest.raises(ValueError):
        static.StaticMeta.get('StaticEnum')

    assert static.StaticMeta.get('name123') is Name123
    assert static.StaticMeta.get('NAME123') is Name123
    assert static.StaticMeta.get('Name123') is Name123
    assert static.StaticMeta.get('someOtherName') is SomeOtherName
    assert static.StaticMeta.get('sOmEOthErNAmE') is SomeOtherName


def test_correct_enum_value(reset_metaclass):
    for enum in static.StaticMeta.all_enums():
        assert issubclass(enum, static.StaticEnum)
        for value in enum:
            value = cast(static.StaticEnum, value)
            assert isinstance(value.info, static.StaticInformation)
