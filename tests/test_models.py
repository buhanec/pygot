"""Test models."""

from __future__ import annotations

import pytest

from pygot import models


@pytest.mark.parametrize('house', [
    'baratheon',
    'greyjoy',
    'lannister',
    'martell',
    'stark',
    'tyrell',
])
def test_houses_set_up(house: str) -> None:
    if not hasattr(models.House, house.upper()):
        raise AssertionError(f'Missing house {house!r}')
    house_enum: models.House = getattr(models.House, house.upper())
    if not house_enum.info.name:
        raise AssertionError(f'House {house!r} missing name')
    if not house_enum.info.words:
        raise AssertionError(f'Houes {house!r} missing words')
