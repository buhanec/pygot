"""Common utility methods."""

from __future__ import annotations

__all__ = ('is_optional', 'optional_subtype', 'type_name')

from typing import Any, Callable, Union

NoneType = type(None)


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
