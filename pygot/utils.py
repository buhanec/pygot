"""Common utility methods."""

from __future__ import annotations

__all__ = ('id_to_name', 'is_optional', 'name_to_id',
           'optional_subtype', 'random_id', 'type_name')

import random
from typing import Any, Callable, Tuple, Union

NoneType = type(None)

_MIN_ID = 0
_MAX_ID = 999
_NAME_GEN_PARTS = [
    ['good', 'fat', 'great', 'little', 'old',
     'big', 'small', 'large', 'bad', 'shiny'],
    ['red', 'yellow', 'green', 'blue', 'purple',
     'silver', 'gold', 'pink', 'black', 'white'],
    ['lion', 'shark', 'dog', 'cat', 'snake',
     'wolf', 'dragon', 'bat', 'moose', 'manticore']
]


def random_id() -> Tuple[int, str]:
    """
    Random game id and name generator.

    :return: Game id, Game name
    """
    id_ = random.randint(_MIN_ID, _MAX_ID)
    name = id_to_name(id_)
    return id_, name


def id_to_name(game_id: int) -> str:
    """
    Convert game id to game name.

    :param game_id: Game id
    :return: Game name
    """
    if game_id > 999 or game_id < 0:
        raise ValueError('Game Id must be in range [0, 999]')
    return '-'.join((_NAME_GEN_PARTS[0][game_id % 1000 // 100],
                     _NAME_GEN_PARTS[1][game_id % 100 // 10],
                     _NAME_GEN_PARTS[2][game_id % 10 // 1]))


def name_to_id(game_name: str) -> int:
    """
    Convert game name to game id.

    :param game_name: Game name
    :return: Game id
    """
    parts = game_name.split('-')
    if len(parts) != 3:
        raise ValueError('Game name must have three parts')
    try:
        d0 = _NAME_GEN_PARTS[0].index(parts[0])
        d1 = _NAME_GEN_PARTS[1].index(parts[1])
        d2 = _NAME_GEN_PARTS[2].index(parts[2])
    except ValueError as e:
        raise ValueError('Invalid parts in game name') from e
    return d0 * 100 + d1 * 10 + d2


def is_optional(obj: Any) -> bool:
    """
    Check if typing.Optional or equivalent.

    :param obj: Object to check
    :return: ``True`` if typing.Optional or equivalent, ``False`` otherwise
    """
    try:
        return (obj.__module__ == 'typing'
                and (str(obj) == 'typing.Optional'
                     or (obj.__origin__ is Union
                         and len(obj.__args__) == 2
                         and NoneType in obj.__args__)))
    except AttributeError:
        return False


def optional_subtype(obj: Any) -> Any:
    """
    Extract optional subtype from typing.Optional.

    :param obj: typing.Optional instance
    :return: Subtype
    """
    if not is_optional(obj):
        raise ValueError('Not a typed typing.Optional')
    try:
        return obj.__args__[0] or obj.__args__[1]
    except AttributeError as e:
        raise ValueError('Not a typed typing.Optional') from e


def type_name(obj: Any, local_name: bool = False) -> str:
    """
    Create nice type name.

    If passing an instance rather than a type, take the instance's type.

    :param obj: Instance or type
    :param local_name: Use __name__ over __qualname__
    :return: Nice type name
    """
    if is_optional(obj):
        try:
            sub_name = optional_subtype(obj)
        except ValueError:
            return 'typing.Optional[Any]'
        else:
            return f'typing.Optional[{type_name(sub_name)}]'
    if getattr(obj, '__module__', None) == 'typing':
        return repr(obj)
    if not isinstance(obj, Callable):
        obj = type(obj)
    if obj.__module__ == 'builtins':
        return obj.__name__
    if local_name:
        return f'{obj.__module__}.{obj.__name__}'
    return f'{obj.__module__}.{obj.__qualname__}'
