"""Models used to abstract various game entities."""

from __future__ import annotations

__all__ = ('House', 'HouseInfo',)

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class HouseInfo:
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
