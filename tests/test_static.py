"""Test static models."""

from __future__ import annotations

__all__ = tuple()

import dataclasses
from typing import Dict

from _pytest.fixtures import FixtureRequest
import pytest

from pygot import serialisation, static


# Fixtures. Need to make a PR for this.
# pylint: disable=unused-argument,redefined-outer-name

# Dummy classes
# pylint: disable=function-redefined,too-few-public-methods,unused-variable


@pytest.fixture(scope='function')
def reset_registry(request: FixtureRequest) -> None:
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


def test_static_type_name_conflict(reset_registry) -> None:
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


def test_static_type_instance_conflict(reset_registry) -> None:
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


def test_attr_scopes(reset_registry) -> None:
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


def test_bad_type_does_not_register(reset_registry) -> None:
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


def test_good_type_registers(reset_registry) -> None:
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
def test_type_registry(reset_registry) -> None:
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
def test_instance_registry(reset_registry) -> None:
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


def test_type_and_instance_metadata(reset_registry) -> None:
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


def test_dynamic_instance_creation(reset_registry) -> None:
    class Name123(static.StaticData):
        """Test class."""

        a: int = static.STATIC
        b: int

    new_instance = Name123('NewType', a=1)

    assert new_instance.__name__ == 'NewType'
    assert new_instance.__module__ == static.__name__
    assert new_instance.a == 1
    assert isinstance(new_instance, Name123)
    assert new_instance in Name123
    assert new_instance is Name123.NewType


def test_dynamic_instance_fetching(reset_registry) -> None:
    class Name123(static.StaticData):
        """Test class."""

        a: int = static.STATIC
        b: int

    class NewType(metaclass=Name123):
        """Test class."""

        a = 1

    new_instance = Name123('NewType', a=1)

    assert new_instance is NewType


def test_dynamic_instance_mismatch_raises(reset_registry) -> None:
    class Name123(static.StaticData):
        """Test class."""

        a: int = static.STATIC
        b: int

    Name123('NewType', a=1)

    with pytest.raises(static.StaticInstanceConflict):
        Name123('NewType', a=2)


def test_dynamic_instance_doc(reset_registry) -> None:
    class Name123(static.StaticData):
        """Test class."""

        a: int = static.STATIC
        b: int

    doc = """A summary.

    And some more details."""

    Name123('NewType', a=1, __doc__=doc)

    assert Name123.NewType.__doc__ == doc


def test_instance_instantiation_as_dataclass(reset_registry) -> None:
    class Name123(static.StaticData):
        """Test class."""

        a: int = static.STATIC
        b: int
        c: str

    class GoodBoy(metaclass=Name123):
        """Test class."""

        a = 1
        b: int
        c: str

    # noinspection PyArgumentList
    doggo = GoodBoy(b=2, c='doggo')
    # noinspection PyArgumentList
    wolfo = GoodBoy(b=3, c='wolfo')

    assert dataclasses.is_dataclass(GoodBoy)
    assert dataclasses.is_dataclass(doggo)
    assert dataclasses.is_dataclass(wolfo)


def test_superfluous_dataclass_annotation(reset_registry) -> None:
    class Name123(static.StaticData):
        """Test class."""

        a: int = static.STATIC
        b: int
        c: str

    @dataclasses.dataclass
    class GoodBoy(metaclass=Name123):
        """Test class."""

        a = 1
        b: int
        c: str

    doggo = GoodBoy(b=2, c='doggo')
    wolfo = GoodBoy(b=3, c='wolfo')

    assert dataclasses.is_dataclass(GoodBoy)
    assert dataclasses.is_dataclass(doggo)
    assert dataclasses.is_dataclass(wolfo)


def test_frozen_type_attributes(reset_registry) -> None:
    class Name123(static.StaticData):
        """Test class."""

        a: int = static.STATIC
        b: int
        c: str

    @dataclasses.dataclass
    class GoodBoy(metaclass=Name123):
        """Test class."""

        a = 1
        b: int
        c: str

    doggo = GoodBoy(b=2, c='doggo')

    assert doggo.a == 1
    assert doggo.b == 2
    assert doggo.c == 'doggo'

    with pytest.raises(AttributeError):
        doggo.a = 10
    doggo.b = 20
    doggo.c = 'DOGGO'

    assert doggo.a == 1
    assert doggo.b == 20
    assert doggo.c == 'DOGGO'


def test_private_properties_remain_private(reset_registry) -> None:
    class Name123(static.StaticData):
        """Test class."""

        __actual_species__: str
        _super_secret: str = 'never let anyone know'

        a: int = static.STATIC
        b: int
        c: str

    class GoodBoy(metaclass=Name123):
        """Test class."""

        __species__ = 'WolfoInDogClothes'
        __annotation_test__: int

        _private_key: str = 'hello world'

        a = 1
        b: int
        c: str

    # noinspection PyArgumentList
    doggo = GoodBoy(b=2, c='doggo')

    assert doggo.a == 1
    assert doggo.b == 2
    assert doggo.c == 'doggo'

    assert doggo.__species__ is GoodBoy.__species__
    assert not hasattr(doggo, '__annotation_test__')
    assert not hasattr(doggo, '__actual_species__')
    assert not hasattr(doggo, '_super_secret')
    # pylint: disable=protected-access
    assert doggo._private_key is GoodBoy._private_key


def test_private_dataclass_properties_remain_private(reset_registry) -> None:
    class Name123(static.StaticData):
        """Test class."""

        a: int = static.STATIC
        b: int
        c: str

    @dataclasses.dataclass
    class GoodBoy(metaclass=Name123):
        """Test class."""

        __species__ = 'WolfoInDogClothes'
        __annotation_test__: int

        a = 1
        b: int
        c: str

        _private_key: str = 'hello world'

    # noinspection PyArgumentList
    doggo = GoodBoy(b=2, c='doggo')

    assert doggo.a == 1
    assert doggo.b == 2
    assert doggo.c == 'doggo'

    assert doggo.__species__ is GoodBoy.__species__
    assert not hasattr(doggo, '__annotation_test__')
    # pylint: disable=protected-access
    assert doggo._private_key is GoodBoy._private_key


def test_dynamic_instance_private_properties(reset_registry) -> None:
    class Name123(static.StaticData):
        """Test class."""

        a: int = static.STATIC
        b: int
        c: str

    Name123('GoodBoy',
            a=1,
            __species__='WolfoInDogClothes',
            _private_key='hello world',
            __annotations__={'__annotation_test__': 'int',
                             '_private_key': 'str',
                             'b': 'int',
                             'c': 'str'})

    # noinspection PyArgumentList
    doggo = Name123.GoodBoy(b=2, c='doggo')

    assert doggo.a == 1
    assert doggo.b == 2
    assert doggo.c == 'doggo'

    assert doggo.__species__ is Name123.GoodBoy.__species__
    assert not hasattr(doggo, '__annotation_test__')
    # pylint: disable=protected-access
    assert doggo._private_key is Name123.GoodBoy._private_key


def test_instance_instance_serialisation(reset_registry) -> None:
    class Name123(static.StaticData):
        """Test class."""

        a: int = static.STATIC
        b: int
        c: Dict[str, int]

    @dataclasses.dataclass
    class GoodBoy(metaclass=Name123):
        """Test class."""

        __species__ = 'WolfoInDogClothes'

        a = 1
        b: int
        c: Dict[str, int]

    doggo = GoodBoy(b=2, c={
        'age_in_dog_years': 100,
    })

    assert serialisation.jsonify(doggo) == {'$module': GoodBoy.__module__,
                                            '$type': GoodBoy.__name__,
                                            'b': 2,
                                            'c': {'ageInDogYears': 100}}
    assert serialisation.jsonify(
        doggo,
        camel_case_keys=True,
        arg_struct=True) == {'$module': GoodBoy.__module__,
                             '$type': GoodBoy.__name__,
                             'b': 2,
                             'c': {'ageInDogYears': 100}}
    assert serialisation.jsonify(
        doggo,
        camel_case_keys=False,
        arg_struct=True) == {'$module': GoodBoy.__module__,
                             '$type': GoodBoy.__name__,
                             'b': 2,
                             'c': {'age_in_dog_years': 100}
                             }
    assert serialisation.jsonify(
        doggo,
        camel_case_keys=True,
        arg_struct=False) == {'b': 2,
                              'c': {'ageInDogYears': 100}}

    assert serialisation.jsonify(
        doggo,
        camel_case_keys=False,
        arg_struct=False) == {'b': 2,
                              'c': {'age_in_dog_years': 100}}


def test_instance_instance_deserialisation(reset_registry) -> None:
    class Name123(static.StaticData):
        """Test class."""

        a: int = static.STATIC
        b: int
        c: Dict[str, int]

    @dataclasses.dataclass
    class GoodBoy(metaclass=Name123):
        """Test class."""

        __species__ = 'WolfoInDogClothes'

        a = 1
        b: int
        c: Dict[str, int]

    doggo = GoodBoy(b=2, c={
        'age_in_dog_years': 100,
    })

    assert 'GoodBoy' not in globals()

    globals()['GoodBoy'] = GoodBoy

    try:
        one = serialisation.unjsonify({'$module': GoodBoy.__module__,
                                       '$type': GoodBoy.__name__,
                                       'b': 2,
                                       'c': {'ageInDogYears': 100}})
        assert one == doggo
        assert one is not doggo

        two = serialisation.unjsonify({'$module': GoodBoy.__module__,
                                       '$type': GoodBoy.__name__,
                                       'b': 2,
                                       'c': {'ageInDogYears': 100}},
                                      camel_case_keys=True)
        assert two == doggo
        assert two is not doggo

        three = serialisation.unjsonify({'$module': GoodBoy.__module__,
                                         '$type': GoodBoy.__name__,
                                         'b': 2,
                                         'c': {'age_in_dog_years': 100}},
                                        camel_case_keys=False)
        assert three == doggo
        assert three is not doggo
    finally:
        del globals()['GoodBoy']


def test_instance_serialisation(reset_registry) -> None:
    class Name123(static.StaticData):
        """Test class."""

        b: int = static.STATIC

    class GoodBoy(metaclass=Name123):
        """Test class."""

        __species__ = 'WolfoInDogClothes'

        b = 2
        c: Dict[str, int] = {'age_in_dog_years': 100}

    class BadBoy(metaclass=Name123):
        """He's a bad boy."""

        surname = 'Eilish'
        b = 2
        c: int
        d: str

    # GoodBoy
    assert serialisation.jsonify(GoodBoy) == {
        '$module': Name123.__module__,
        '$type': Name123.__name__,
        'name': 'GoodBoy',
        'b': 2,
        'c': {'ageInDogYears': 100}
    }
    assert serialisation.jsonify(
        GoodBoy,
        camel_case_keys=True,
        arg_struct=True) == {'$module': Name123.__module__,
                             '$type': Name123.__name__,
                             'name': 'GoodBoy',
                             'b': 2,
                             'c': {'ageInDogYears': 100}}
    assert serialisation.jsonify(
        GoodBoy,
        camel_case_keys=False,
        arg_struct=True) == {'$module': Name123.__module__,
                             '$type': Name123.__name__,
                             'name': 'GoodBoy',
                             'b': 2,
                             'c': {'age_in_dog_years': 100}}
    assert serialisation.jsonify(
        GoodBoy,
        camel_case_keys=True,
        arg_struct=False) == {'name': 'GoodBoy',
                              'b': 2,
                              'c': {'ageInDogYears': 100}}

    assert serialisation.jsonify(
        GoodBoy,
        camel_case_keys=False,
        arg_struct=False) == {'name': 'GoodBoy',
                              'b': 2,
                              'c': {'age_in_dog_years': 100}}

    # BadBoy
    assert serialisation.jsonify(BadBoy) == {'$module': Name123.__module__,
                                             '$type': Name123.__name__,
                                             'name': 'BadBoy',
                                             'b': 2,
                                             'surname': 'Eilish'}
    assert serialisation.jsonify(
        BadBoy,
        camel_case_keys=True,
        arg_struct=True) == {'$module': Name123.__module__,
                             '$type': Name123.__name__,
                             'name': 'BadBoy',
                             'b': 2,
                             'surname': 'Eilish'}
    assert serialisation.jsonify(
        BadBoy,
        camel_case_keys=False,
        arg_struct=True) == {'$module': Name123.__module__,
                             '$type': Name123.__name__,
                             'name': 'BadBoy',
                             'b': 2,
                             'surname': 'Eilish'}
    assert serialisation.jsonify(
        BadBoy,
        camel_case_keys=True,
        arg_struct=False) == {'name': 'BadBoy',
                              'b': 2,
                              'surname': 'Eilish'}

    assert serialisation.jsonify(
        BadBoy,
        camel_case_keys=False,
        arg_struct=False) == {'name': 'BadBoy',
                              'b': 2,
                              'surname': 'Eilish'}


def test_instance_deserialisation(reset_registry) -> None:
    class Name123(static.StaticData):
        """Test class."""

        b: int = static.STATIC
        c: Dict[str, int] = static.STATIC

    assert 'Name123' not in globals()

    globals()['Name123'] = Name123

    try:
        class GoodBoy(metaclass=Name123):
            """He's a good boy."""

            b = 2
            c = {'age_in_dog_years': 100}

        one = serialisation.unjsonify({
            '$module': Name123.__module__,
            '$type': Name123.__name__,
            'name': 'GoodBoy',
            'b': 2,
            'c': {'ageInDogYears': 100}
        })
        two = serialisation.unjsonify({
            '$module': Name123.__module__,
            '$type': Name123.__name__,
            'name': 'GoodBoy',
            'b': 2,
            'c': {'ageInDogYears': 100}
        }, camel_case_keys=True)
        three = serialisation.unjsonify({
            '$module': Name123.__module__,
            '$type': Name123.__name__,
            'name': 'GoodBoy',
            'b': 2,
            'c': {'age_in_dog_years': 100}
        }, camel_case_keys=False)

        fresh = serialisation.unjsonify({
            '$module': Name123.__module__,
            '$type': Name123.__name__,
            'name': 'FreshBoy',
            'b': 3,
            'c': {'ageInDogYears': 10}
        })

        assert one in GoodBoy
        assert two is GoodBoy
        assert three is GoodBoy

        assert fresh.__name__ == 'FreshBoy'
        assert fresh.__module__ == static.__name__
        assert isinstance(fresh, Name123)
        assert fresh in Name123
        assert fresh is not GoodBoy
        assert fresh is Name123.FreshBoy
        assert fresh.b == 3
        assert fresh.c == {'age_in_dog_years': 10}
    finally:
        del globals()['Name123']
