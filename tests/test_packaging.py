"""Test server packaging and style setup."""

from __future__ import annotations

from distutils.version import StrictVersion
import importlib
import itertools
import os
import pkgutil
import subprocess
from typing import MutableSequence, Sequence

import pytest

import pygot
import tests

# Find modules to play with
_ROOT = os.path.dirname(os.path.dirname(pygot.__file__))
_ROOT_MODULES = {m.name: m for m in pkgutil.iter_modules([_ROOT])}

_SRC_MODULES = {m.name: m for m in
                pkgutil.walk_packages(path=[os.path.dirname(pygot.__file__)],
                                      prefix=f'{pygot.__name__}.')}
_SRC_MODULES[pygot.__name__] = _ROOT_MODULES[pygot.__name__]

_TEST_MODULES = {m.name: m for m in
                 pkgutil.walk_packages(path=[os.path.dirname(tests.__file__)],
                                       prefix=f'{tests.__name__}.')}
_TEST_MODULES[tests.__name__] = _ROOT_MODULES[tests.__name__]

_ALL_MODULES = dict(itertools.chain(_SRC_MODULES.items(),
                                    _TEST_MODULES.items()))

# Find files to play with
_ALL_FILES = subprocess.run(('git', 'ls-files'),
                            capture_output=True,
                            check=True).stdout.decode().splitlines()
_ALL_FILES = [f for f in _ALL_FILES if not f.startswith('.idea')]


@pytest.mark.parametrize('attr', (
        '__title__',
        '__description__',
        '__url__',
        '__version__',
        '__author__',
        '__author_email__',
        '__license__',
        '__copyright__',
))
def test_package_meta(attr: str) -> None:
    if not hasattr(pygot, attr):
        raise AssertionError(f'{pygot.__name__} is missing {attr}')
    if getattr(pygot, attr) in {None, ''}:
        raise AssertionError(f'{pygot.__name__}.{attr} is not set')


def test_version_valid() -> None:
    try:
        StrictVersion(pygot.__version__)
    except ValueError as e:
        raise AssertionError(str(e)) from e


@pytest.mark.parametrize('module', _SRC_MODULES.values(),
                         ids=list(_SRC_MODULES.keys()))
def test_module_all(module: pkgutil.ModuleInfo) -> None:
    imported = importlib.import_module(module.name)
    if not hasattr(imported, '__all__'):
        raise AssertionError(f'{module.name} is missing __all__')
    if isinstance(imported.__all__, str):
        raise AssertionError(f'{module.name}.__all__ must not be a string')
    if (not isinstance(imported.__all__, Sequence)
            or isinstance(imported.__all__, MutableSequence)):
        raise AssertionError(f'{module.name}.__all__ must be immutable')


@pytest.mark.parametrize('module', _ALL_MODULES.values(),
                         ids=list(_ALL_MODULES.keys()))
def test_module_doc(module: pkgutil.ModuleInfo) -> None:
    imported = importlib.import_module(module.name)
    if imported.__doc__ is None or not imported.__doc__.strip():
        raise AssertionError(f'{module.name} is missing module docstring')


@pytest.mark.parametrize('module', _ALL_MODULES.values(),
                         ids=list(_ALL_MODULES.keys()))
def test_module_doc(module: pkgutil.ModuleInfo) -> None:
    imported = importlib.import_module(module.name)
    if (hasattr(imported, 'logger')
            and imported.logger.name != module.name):
        raise AssertionError(f'{module.name} has foreign logger '
                             f'{imported.logger.name}')


@pytest.mark.parametrize('module', _ALL_MODULES.values(),
                         ids=list(_ALL_MODULES.keys()))
def test_module_future_import(module: pkgutil.ModuleInfo) -> None:
    imported = importlib.import_module(module.name)
    if (not hasattr(imported, 'annotations')
            or imported.annotations is not annotations):
        raise AssertionError(f"{module.name} missing 'from __future__ "
                             f"import annotations' statement")


@pytest.mark.parametrize('filename', _ALL_FILES)
def test_newline_end_of_files(filename: str) -> None:
    try:
        with open(filename, 'rb') as f:
            content = f.read().decode()
    except (PermissionError, ValueError):
        return
    assert not content or content.endswith('\n')


@pytest.mark.parametrize('filename', _ALL_FILES)
def test_no_trailing_spaces(filename: str) -> None:
    try:
        with open(filename, 'rb') as f:
            content = f.read().decode()
    except (PermissionError, ValueError):
        return
    assert not any(l != l.rstrip() for l in content.splitlines())
