"""Test static models."""

from __future__ import annotations

__all__ = tuple()

from _pytest.fixtures import FixtureRequest
import pytest

from pygot import static


# Fixtures. Need to make a PR for this.
# pylint: disable=unused-argument,redefined-outer-name

# Dummy classes
# pylint: disable=function-redefined,too-few-public-methods,unused-variable


@pytest.fixture(scope='function')
def reset_registry(request: FixtureRequest):
    """Ensure everything has a clean registry."""
    reset = {}
    for name in dir(static):
        obj = getattr(static, name)
        if hasattr(obj, '__registry__'):
            reset[obj] = getattr(obj, '__registry__').copy()

    def _fin():
        for obj_, __registry__ in reset.items():
            obj_.__registry__ = __registry__

    request.addfinalizer(_fin)


def test_static_type_name_conflict(reset_registry):
    # noinspection PyUnusedLocal
    class Name123(static.StaticData):
        """Test class."""

    with pytest.raises(static.StaticTypeConflict):
        # noinspection PyUnusedLocal,PyRedeclaration
        class Name123(static.StaticData):
            """Test class."""

    with pytest.raises(static.StaticTypeConflict):
        # pylint: disable=invalid-name
        # noinspection PyUnusedLocal,PyRedeclaration,PyPep8Naming
        class name123(static.StaticData):
            """Test class."""

    with pytest.raises(static.StaticTypeConflict):
        # noinspection PyUnusedLocal,PyRedeclaration,PyPep8Naming
        class NAME123(static.StaticData):
            """Test class."""


def test_static_type_instance_conflict(reset_registry):
    class Name123(static.StaticData):
        """Test class."""

    # noinspection PyUnusedLocal
    class Instance123(metaclass=Name123):
        """Test instance."""

    with pytest.raises(static.StaticInstanceConflict):
        # noinspection PyUnusedLocal,PyRedeclaration
        class Instance123(metaclass=Name123):
            """Test class."""

    with pytest.raises(static.StaticInstanceConflict):
        # pylint: disable=invalid-name
        # noinspection PyUnusedLocal,PyRedeclaration,PyPep8Naming
        class instance123(metaclass=Name123):
            """Test class."""

    with pytest.raises(static.StaticInstanceConflict):
        # noinspection PyUnusedLocal,PyRedeclaration,PyPep8Naming
        class INSTANCE123(metaclass=Name123):
            """Test class."""


def test_attr_scopes(reset_registry):
    class Name123(static.StaticData):
        """Test class."""

        a: int = static.STATIC
        b: int = static.STATIC
        c: int
        d: int

    # noinspection PyUnusedLocal
    class OkInstance(metaclass=Name123):
        """Test instance."""

        a = 1
        b = 2

    with pytest.raises(static.ExpectedStaticAttr):
        # noinspection PyUnusedLocal
        class BadInstance(metaclass=Name123):
            """Test class."""

            a = 1

    with pytest.raises(static.UnexpectedStaticAttr):
        # noinspection PyUnusedLocal,PyRedeclaration
        class BadInstance(metaclass=Name123):
            """Test class."""

            a = 1
            b = 2
            c = 3


def test_bad_type_does_not_register(reset_registry):
    class Name123(static.StaticData):
        """Test class."""

        a: int = static.STATIC
        b: int = static.STATIC
        c: int
        d: int

    with pytest.raises(static.ExpectedStaticAttr):
        # noinspection PyUnusedLocal
        class BadInstance(metaclass=Name123):
            """Test class."""

            a = 1

    # noinspection PyTypeChecker
    assert len(Name123) == 0


def test_good_type_registers(reset_registry):
    class Name123(static.StaticData):
        """Test class."""

    class GoodBoy(metaclass=Name123):
        """Test class."""

    class GoodGirl(metaclass=Name123):
        """Test class."""

    assert GoodBoy in Name123
    assert GoodGirl in Name123
    # noinspection PyTypeChecker
    assert len(Name123) == 2


# noinspection SpellCheckingInspection
def test_type_registry(reset_registry):
    # noinspection PyTypeChecker
    initial_len = len(static.StaticData)

    class GoodBoy(static.StaticData):
        """Test class."""

    class GoodGirl(static.StaticData):
        """Test class."""

    assert static.StaticData.GoodBoy is GoodBoy
    assert static.StaticData.goodBoy is GoodBoy
    assert static.StaticData.GOODBOY is GoodBoy
    assert static.StaticData.goodboy is GoodBoy
    assert static.StaticData.GOoDBoy is GoodBoy
    assert static.StaticData.GoodGirl is GoodGirl
    assert static.StaticData.goodGirl is GoodGirl
    assert static.StaticData.GOODGIRL is GoodGirl
    assert static.StaticData.goodgirl is GoodGirl
    assert static.StaticData.goOdgIRl is GoodGirl

    # noinspection PyTypeChecker
    assert len(static.StaticData) - initial_len == 2

    assert any(x is GoodBoy for x in static.StaticData)
    assert any(x is GoodGirl for x in static.StaticData)

    assert GoodBoy in static.StaticData
    assert GoodBoy.__name__ in static.StaticData
    assert 'GoodBoy' in static.StaticData
    assert 'goodBoy' in static.StaticData
    assert 'GOODBOY' in static.StaticData
    assert 'goodboy' in static.StaticData
    assert 'GOoDBoy' in static.StaticData
    assert GoodGirl in static.StaticData
    assert GoodGirl.__name__ in static.StaticData
    assert 'GoodGirl' in static.StaticData
    assert 'goodGirl' in static.StaticData
    assert 'GOODGIRL' in static.StaticData
    assert 'goodgirl' in static.StaticData
    assert 'goOdgIRl' in static.StaticData

    assert GoodBoy.__name__ in dir(static.StaticData)
    assert GoodGirl.__name__ in dir(static.StaticData)


# noinspection SpellCheckingInspection
def test_instance_registry(reset_registry):
    class Name123(static.StaticData):
        """Test class."""

        a: int = static.STATIC
        b: int

    class GoodBoy(metaclass=Name123):
        """Test class."""

        a = 1

    class GoodGirl(metaclass=Name123):
        """Test class."""

        a = 2

    assert Name123.GoodBoy is GoodBoy
    assert Name123.goodBoy is GoodBoy
    assert Name123.GOODBOY is GoodBoy
    assert Name123.goodboy is GoodBoy
    assert Name123.GOoDBoy is GoodBoy
    assert Name123.GoodGirl is GoodGirl
    assert Name123.goodGirl is GoodGirl
    assert Name123.GOODGIRL is GoodGirl
    assert Name123.goodgirl is GoodGirl
    assert Name123.goOdgIRl is GoodGirl

    # noinspection PyTypeChecker
    assert len(Name123) == 2

    # noinspection PyTypeChecker
    for n, x in enumerate(Name123):
        assert x is GoodGirl or x in GoodBoy
        assert n in (0, 1)

    assert GoodBoy in Name123
    assert GoodBoy.__name__ in Name123
    assert 'GoodBoy' in Name123
    assert 'goodBoy' in Name123
    assert 'GOODBOY' in Name123
    assert 'goodboy' in Name123
    assert 'GOoDBoy' in Name123
    assert GoodGirl in Name123
    assert GoodGirl.__name__ in Name123
    assert 'GoodGirl' in Name123
    assert 'goodGirl' in Name123
    assert 'GOODGIRL' in Name123
    assert 'goodgirl' in Name123
    assert 'goOdgIRl' in Name123

    assert GoodBoy.__name__ in dir(Name123)
    assert GoodGirl.__name__ in dir(Name123)


def test_type_and_instance_metadata(reset_registry):
    class Name123(static.StaticData):
        """
        Test class.

        The actual description, very very long-winded and whatnot.
        It might even feature some breaks, an example:
            Example:
                x + 2 = 5
                    x = 5 - 2
                    x = 3

        ...and a paragraph.
        """

    name_info = """The actual description, very very long-winded and whatnot.
It might even feature some breaks, an example:
    Example:
        x + 2 = 5
            x = 5 - 2
            x = 3

...and a paragraph."""

    class GoodBoy(static.StaticData):
        """It may also follow slightly different docstring conventions.

        In which case, tough - right?

        Or maybe it can be handled."""

    good_boy_info = """In which case, tough - right?

Or maybe it can be handled."""

    class Boring(metaclass=Name123):
        """So boring it can barely get a summary."""

    # pylint: disable=missing-class-docstring
    class Indescribable(metaclass=GoodBoy):
        pass

    assert Name123.name == Name123.__name__
    assert Name123.info == name_info
    assert GoodBoy.name == GoodBoy.__name__
    assert GoodBoy.info == good_boy_info
    assert Boring.name == Boring.__name__
    assert Boring.info == 'So boring it can barely get a summary.'
    assert Indescribable.name == Indescribable.__name__
    assert Indescribable.info == 'Indescribable()'
