"""Static models that represent game data."""

from __future__ import annotations

__all__ = ('Flavour', 'House', 'StaticEnum', 'StaticInformation',
           'Terrain', 'Unit', 'UnitState')

import dataclasses
from enum import Enum, EnumMeta
from typing import Any, Dict, Optional, Set, Tuple, Type


class StaticNameConflict(RuntimeError):
    """Thrown when static names conflict."""

    def __init__(self, name, existing_enum):
        self.name = name
        self.existing_enum = existing_enum
        super().__init__(f'Could not create {name!r}, name in use')


class StaticMeta(EnumMeta):
    """
    Metaclass for static data enums.

    Tries to ensure that there are uniquely named classes in existence,
    which can be easily accessed through case insensitive references.
    """

    __root__: Optional[StaticMeta] = None
    __registry__: Dict[str, StaticMeta] = {}

    def __new__(mcs,
                cls: str,
                bases: Tuple[Type[object]],
                class_dict: Dict[str, Any]) -> StaticMeta:
        # Walrus is sad :'=
        if cls.lower() in mcs.__registry__:
            raise StaticNameConflict(cls, mcs.__registry__[cls.lower()])

        if mcs.__root__ is not None and mcs.__root__ not in bases:
            raise TypeError(f'Must subclass {mcs.__root__.__name__}')

        new = super().__new__(mcs, cls, bases, class_dict)

        if mcs.__root__ is None:
            mcs.__root__ = new
        else:
            mcs.__registry__[cls.lower()] = new
        return new

    @classmethod
    def get(mcs, name: str) -> StaticMeta:
        """
        Find a `StaticEnum` that matches the given name.

        This will not find an instance of `StaticEnum`, but rather the
        `Enum` class itself.

        :param name: `StaticEnum` case-insensitive class name
        :return: `StaticEnum` class
        """
        if name.lower() not in mcs.__registry__:
            raise ValueError(f'Could not find {name!r}')
        return mcs.__registry__[name.lower()]

    @classmethod
    def all_enums(mcs) -> Set[StaticMeta]:
        """
        Find all registered subclasses of `StaticEnum`.

        :return: All registered subclasses of `StaticEnum`
        """
        return set(mcs.__registry__.values())


class StaticEnum(Enum, metaclass=StaticMeta):
    """
    Static data enum parent.

    Enum values should resolve to `StaticInformation` instances with
    names that match the enum names.
    """

    @property
    def info(self) -> StaticInformation:
        """
        Return static information about enum.

        :return: Static information about enum
        """
        return self.value


@dataclasses.dataclass(frozen=True)
class StaticInformation:
    """
    Static data parent.

    `StaticEnum` values should resolve to instances of this class with
    names that match the enum names.
    """

    name: str


@dataclasses.dataclass(frozen=True)
class _Terrain(StaticInformation):
    """Terrain."""


class Terrain(StaticEnum):
    """Terrain type."""

    LAND = _Terrain(name='Land')
    WATER = _Terrain(name='Water')


@dataclasses.dataclass(frozen=True)
class _Unit(StaticInformation):
    """Unit information."""

    name: str
    terrain: Terrain
    strength: int


class Unit(StaticEnum):
    """Unit information enum."""

    FOOTMAN = _Unit(name='Footman',
                    terrain=Terrain.LAND,
                    strength=1)

    KNIGHT = _Unit(name='Knight',
                   terrain=Terrain.LAND,
                   strength=2)

    SHIP = _Unit(name='Ship',
                 terrain=Terrain.WATER,
                 strength=1)

    SIEGE = _Unit(name='Siege',
                  terrain=Terrain.LAND,
                  strength=2)


@dataclasses.dataclass(frozen=True)
class _House(StaticInformation):
    """House information."""

    name: str
    words: str
    description: str = ''


class House(StaticEnum):
    """Houses of Westeros."""

    STARK = _House(name='Stark',
                   words='Winter is Coming')
    GREYJOY = _House(name='Greyjoy',
                     words='We Do Not Sow')
    LANNISTER = _House(name='Lannister',
                       words='Hear Me Roar')
    MARTELL = _House(name='Martell',
                     words='Unbowed, Unbent, Unbroken')
    TYRELL = _House(name='Tyrell',
                    words='Growing String')
    BARATHEON = _House(name='Baratheon',
                       words='Ours is the Fury')


@dataclasses.dataclass(frozen=True)
class _UnitState(StaticInformation):
    """Unit state."""


class UnitState(StaticEnum):
    """Unit state."""

    READY = _UnitState(name='Ready')
    RETREATING = _UnitState(name='Retreating')
    UNAVAILABLE = _UnitState(name='Unavailable')


@dataclasses.dataclass(frozen=True)
class _Flavour(StaticInformation):
    """Game flavour."""


class Flavour(StaticEnum):
    """Game flavour."""

    VANILLA = _Flavour('Vanilla')
