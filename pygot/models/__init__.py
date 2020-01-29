"""Models used to abstract various game entities."""

from __future__ import annotations

__all__ = ('House', 'HouseInfo',)

import dataclasses
from enum import Enum

from pygot.models.serialisation import JSONMixin, ReplaceMixin


@dataclasses.dataclass(frozen=True)
class HouseInfo(JSONMixin):
    """House information."""

    name: str
    words: str
    description: str = ''


_STARK = HouseInfo(name='Stark',
                   words='Winter is Coming')
_GREYJOY = HouseInfo(name='Greyjoy',
                     words='We Do Not Sow')
_LANNISTER = HouseInfo(name='Lannister',
                       words='Hear Me Roar')
_MARTELL = HouseInfo(name='Martell',
                     words='Unbowed, Unbent, Unbroken')
_TYRELL = HouseInfo(name='Tyrell',
                    words='Growing String')
_BARATHEON = HouseInfo(name='Baratheon',
                       words='Ours is the Fury')


class House(Enum):
    """Houses of Westeros."""

    STARK = _STARK
    GREYJOY = _GREYJOY
    LANNISTER = _LANNISTER
    MARTELL = _MARTELL
    TYRELL = _TYRELL
    BARATHEON = _BARATHEON

    @property
    def info(self) -> HouseInfo:
        """
        Get information about house.

        :return: Information about house
        """
        return self.value

    def __repr__(self) -> str:
        return f'<House.{self.name}>'


class Terrain(Enum):
    """Terrain type."""

    LAND = 'Land'
    WATER = 'Water'


@dataclasses.dataclass(frozen=True)
class UnitInfo(JSONMixin):
    """House information."""

    name: str
    terrain: Terrain
    value: int


_FOOTMAN = UnitInfo(name='Footman',
                    terrain=Terrain.LAND,
                    value=1)

_KNIGHT = UnitInfo(name='Knight',
                   terrain=Terrain.LAND,
                   value=2)

_SHIP = UnitInfo(name='Ship',
                 terrain=Terrain.WATER,
                 value=1)

_SIEGE = UnitInfo(name='Siege',
                  terrain=Terrain.LAND,
                  value=2)


class Unit(Enum):
    """Unit type."""

    FOOTMAN = _FOOTMAN
    KNIGHT = _KNIGHT
    SHIP = _SHIP
    SIEGE = _SIEGE


@dataclasses.dataclass(frozen=True)
class UnitInstance(ReplaceMixin, JSONMixin):
    """Unit instance."""

    type: Unit
    house: House
    retreating: bool
