"""
Static models that represent game data.

Is it necessary? No. Is it fun? Yes.

The high-level goal is to create partially fixed data containers, where
some data is preset and immutable, while some data is required to be set
on instantiation and can be mutated.

For convenience the root `StaticData` is a registry of all partially
fixed data container types, while in turn those fixed data container
types are registries of the partially fixed data containers.

These partially fixed data containers can be instantiated as dataclasses
that span the mutable properties.
"""

from __future__ import annotations

__all__ = ('ExpectedStaticAttr', 'Flavour', 'House', 'Registry',
           'StaticData', 'StaticInstanceConflict',
           'StaticTypeConflict', 'Terrain', 'UnexpectedStaticAttr',
           'Unit', 'UnitState', 'Vanilla')

import dataclasses
import datetime
from enum import Enum
import functools
import logging
import textwrap
from typing import (Any, Dict, Iterable, Iterator, List, Optional,
                    Tuple, Type, TypeVar)

from pygot import serialisation, utils

logger = logging.getLogger(__name__)


# This place contains a lot of dataclasses and meta-magic...
# pylint: disable=too-few-public-methods


class StaticTypeConflict(TypeError):
    """Thrown when static names conflict."""

    def __init__(self, name: str, existing_class: Type[Any]) -> None:
        """
        Initialise error with debugging information.

        :param name: Clashing name
        :param existing_class:  Existing class
        """
        self.name = name
        self.existing_class = existing_class
        super().__init__(f'Could not create {name!r}, name in use')


class StaticInstanceConflict(TypeError):
    """Thrown when static instance names conflict."""

    def __init__(self, name: str, existing_class: Type[Any]) -> None:
        """
        Initialise error with debugging information.

        :param name: Clashing name
        :param existing_class:  Existing class
        """
        self.name = f'{type(existing_class).__name__}.{name}'
        self.existing_class = existing_class
        super().__init__(f'Could not create {name!r}, name in use')


class ExpectedStaticAttr(AttributeError):
    """Thrown when static definition is missing an expected attribute."""

    def __init__(self, name: str, attrs: Iterable[str]) -> None:
        """
        Initialise error with debugging information.

        :param name: Class name
        :param attrs:  Missing attributes
        """
        self.name = name
        self.attrs = attrs
        super().__init__(f'Could not create {name!r}, expected attr '
                         f'{", ".join(map(repr, attrs))}')


class UnexpectedStaticAttr(AttributeError):
    """Thrown when static definition has an unexpected attribute."""

    def __init__(self, name: str, attrs: Iterable[str]) -> None:
        """
        Initialise error with debugging information.

        :param name: Class name
        :param attrs:  Unexpected attributes
        """
        self.name = name
        self.attrs = attrs
        super().__init__(f'Could not create {name!r}, unexpected attr '
                         f'{", ".join(map(repr, attrs))}')


STATIC = type('STATIC', tuple(), {})

T = TypeVar('T')


class _Registry(type):
    """Mixin to provide information on data containers."""

    @property
    def name(cls) -> str:
        """
        Get data container name.

        :return: Data container name
        """
        return cls.__name__

    @property
    def info(cls) -> str:
        """
        Get data container info.

        :return: Data container info
        """
        # noinspection PyTypeChecker
        doc: str = cls.__doc__
        desc = doc.lstrip().split('\n', maxsplit=1)[-1]
        desc = textwrap.dedent(desc).strip()
        return desc

    def __getattr__(cls, name: str) -> Any:
        if name.lower() not in cls.__registry__:
            raise AttributeError(name)
        return cls.__registry__[name.lower()]

    def __len__(cls) -> int:
        return len(cls.__registry__)

    def __iter__(cls) -> Iterator[Any]:
        for x in cls.__registry__.values():
            yield x

    def __contains__(cls, x: object) -> bool:
        if isinstance(x, str):
            return x.lower() in cls.__registry__
        return x in cls.__registry__.values()


class Registry(_Registry):
    """Metaclass that does registry setup."""

    def __new__(mcs,
                name: str,
                bases: Tuple[Type[Any]],
                class_dict: Dict[str, Any]) -> Registry:
        """
        Attach a new registry to class during class creation.

        :param name: Class name
        :param bases: Class bases
        :param class_dict: Class dict
        """
        new = super().__new__(mcs, name, bases, class_dict)
        new.__registry__ = {}
        if not hasattr(new, '__annotations__'):
            new.__annotations__ = {}
        return new

    def register(cls, instance):
        """
        Register an instance with the registry.

        :param instance: Instance to register
        """
        cls.__registry__[instance.__name__.lower()] = instance

    def __dir__(cls) -> Iterable[str]:
        default_dir = list(super().__dir__())
        registry_dir = [c.__name__ for c in cls.__registry__.values()]
        return default_dir + registry_dir


class StaticData(_Registry, metaclass=Registry):
    """Metaclass keeping track of all static data classes and instances."""

    def __new__(mcs,
                name: str,
                bases: Tuple[Type[Any]] = tuple(),
                class_dict: Optional[Dict[str, Any]] = None,
                **kwargs) -> StaticData:
        """
        Create a new partially fixed static data container.

        :param name: Container name
        :param bases: Container bases
        :param class_dict: Container class dict
        :param kwargs: Kwargs for container class, if dynamically generated
        """
        if class_dict is None:
            class_dict = kwargs
            logger.info('Programmatically creating %r as instance of %s...',
                        name, utils.type_name(mcs))
        else:
            class_dict.update(kwargs)
            logger.info('Creating %r as instance of %s...',
                        name, utils.type_name(mcs))
        # Check for existing name
        if name in mcs:
            existing = getattr(mcs, name)
            existing_class_dict = {k: getattr(existing, k)
                                   for k in existing.__static_fields__}

            # This check will fail if we have any dunders available,
            # making this only work for programatically defined classes.
            if class_dict == existing_class_dict:
                return existing
            raise StaticInstanceConflict(name, existing)

        # Sort out attributes
        static_attrs = {}
        dynamic_attrs = {}
        for attr, hint in mcs.__annotations__.items():
            if attr.startswith('_'):
                continue
            if getattr(mcs, attr, None) is STATIC:
                static_attrs[attr] = hint
            else:
                dynamic_attrs[attr] = hint

        # Check for missing and unexpected attrs
        missing = static_attrs.keys() - class_dict.keys()
        if missing:
            raise ExpectedStaticAttr(name, missing)
        unexpected = class_dict.keys() & dynamic_attrs
        if unexpected:
            raise UnexpectedStaticAttr(name, unexpected)

        # Extend static attrs with additional class_dict values
        full_static = static_attrs.keys() | {k for k in class_dict.keys()
                                             if k not in dynamic_attrs
                                             and not k.startswith('_')}

        # Instantiate object
        new = super().__new__(mcs, name, bases, class_dict)

        # Create setattr to block frozen attrs from being overridden
        @functools.wraps(new.__setattr__)
        def _setattr(self_: StaticData, name_: str, value_: Any) -> None:
            if name_ in self_.__static_fields__:
                raise AttributeError(f'Frozen attribute: {name_!r}')
            # pylint: disable=bad-super-call
            super(new, self_).__setattr__(name_, value_)

        # Create half-frozen dataclass
        new.__annotations__ = dynamic_attrs
        new.__static_fields__ = full_static
        new.__setattr__ = _setattr
        new = dataclasses.dataclass(new)

        # Register instance
        mcs.register(new)
        logger.info('%s registered with %s',
                    utils.type_name(new), utils.type_name(mcs))

        return new

    def __init__(cls,
                 name: str,
                 bases: Tuple[Type[Any]] = tuple(),
                 class_dict: Optional[Dict[str, Any]] = None,
                 **kwargs) -> None:
        """
        Capture and correctly assemble class dict for programmatic instances.

        :param name: Class name
        :param bases: Class bases
        :param class_dict: Class dict
        :param kwargs: Class dict as kwargs
        """
        if class_dict is None:
            class_dict = kwargs
        else:
            class_dict.update(kwargs)
        super().__init__(name, bases, class_dict)

    def __init_subclass__(mcs, **kwargs: Any) -> None:
        # We are just going to hijack the children registry for
        # subclasses instead here...
        if mcs.__name__ in StaticData:
            existing = getattr(StaticData, mcs.__name__)
            raise StaticTypeConflict(mcs.__name__, existing)
        StaticData.register(mcs)
        logger.info('%s registered with %s',
                    utils.type_name(mcs), utils.type_name(StaticData))

    def __str__(cls) -> str:
        return f'{type(cls).__name__}.{cls.__name__}'

    def __repr__(cls) -> str:
        args = [repr(cls.__name__)]
        for f in cls.__static_fields__:
            args.append(f'{f}={getattr(cls, f)!r}')
        return f'{type(cls).__name__}({", ".join(args)})'


@serialisation.jsonify.register
def _jsonify_static_data(obj: StaticData,
                         camel_case_keys: bool = True,
                         arg_struct: bool = True) -> serialisation.JSONType:
    d = {f: getattr(obj, f) for f in obj.__static_fields__}
    d['name'] = obj.__name__
    d = serialisation.jsonify(d,
                              camel_case_keys=camel_case_keys,
                              arg_struct=arg_struct)
    if arg_struct:
        d[serialisation.MODULE_KEY] = type(obj).__module__
        d[serialisation.NAME_KEY] = type(obj).__name__
    return d


class _Enum(Enum):
    """Just a nicer enum, because we do not care about values."""

    def __repr__(self):
        return str(self)


class UnitState(_Enum):
    """Unit state."""

    READY = 'Ready'
    RETREATING = 'Retreating'
    OFF_BOARD = 'Off Board'


class Flavour(StaticData):
    """Game flavour."""

    shared_round_time: datetime.timedelta
    individual_round_time: datetime.timedelta
    rounds: int


class Vanilla(metaclass=Flavour):
    """Vanilla game flavour."""


class Unit(StaticData):
    """Unit information."""

    unit_damage: int = STATIC
    fort_damage: int = STATIC
    state: UnitState


class Footman(metaclass=Unit):
    """A noble footman. Fodder for the king's army."""

    unit_damage = 1
    fort_damage = 1


class Knight(metaclass=Unit):
    """A clown, second only to jesters."""

    unit_damage = 2
    fort_damage = 2


class Ship(metaclass=Unit):
    """The ancient version of a spaceship."""

    unit_damage = 1
    fort_damage = 1


class Siege(metaclass=Unit):
    """When you need to compensate."""

    unit_damage = 0
    fort_damage = 4


class Terrain(StaticData):
    """Terrain."""

    unit_constraint: List[Unit] = STATIC
    token_constraint: List[Any] = STATIC


class Land(metaclass=Terrain):
    """Earthy terrain."""

    unit_constraint = [Footman, Knight, Siege]
    token_constraint = []


class Sea(metaclass=Terrain):
    """Wet terrain."""

    unit_constraint = List[Ship]
    token_constraint = []


class House(StaticData):
    """A house in the wild west."""

    words: str = STATIC
    description: str = STATIC


class Stark(metaclass=House):
    """A house that wants the throne."""

    words = 'Winter is Coming'
    description = ''


class Greyjoy(metaclass=House):
    """A house that wants the throne."""

    words = 'We Do Not Sow'
    description = ''


class Lannister(metaclass=House):
    """A house that wants the throne."""

    words = 'Hear Me Roar'
    description = ''


class Martell(metaclass=House):
    """A house that wants the throne."""

    words = 'Unbowed, Unbent, Unbroken'
    description = ''


class Tyrell(metaclass=House):
    """A house that wants the throne."""

    words = 'Growing String'
    description = ''


class Baratheon(metaclass=House):
    """A house that wants the throne."""

    words = 'Ours is the Fury'
    description = ''
