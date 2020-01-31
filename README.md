# PyGoT
[![Travis CI](https://img.shields.io/travis/buhanec/pygot/master.svg?label=Travis+CI&style=flat-square)](https://travis-ci.org/buhanec/pygot)
[![Azure DevOps build](https://img.shields.io/azure-devops/build/buhanec/pygot/1?label=Azure%20DevOps%20build&style=flat-square)](https://dev.azure.com/buhanec/pygot/_build)
[![Code Coverage](https://img.shields.io/codecov/c/github/buhanec/pygot?style=flat-square)](https://codecov.io/gh/buhanec/pygot)
[![Code Quality](https://img.shields.io/codacy/grade/5c4e5d014fb74167b1283ba0b6b57198?style=flat-square)](https://www.codacy.com/manual/buhanec/pygot)
[![Requirements Status](https://img.shields.io/requires/github/buhanec/pygot?style=flat-square)](https://requires.io/github/buhanec/pygot/requirements/)
[![License](https://img.shields.io/github/license/buhanec/pygot?style=flat-square)](https://github.com/buhanec/pygot/blob/master/LICENSE)
<!--
[![Supported Python Version](https://img.shields.io/pypi/pyversions/pygot.svg?style=flat-square)](https://pypi.org/project/pygot/)
[![License](https://img.shields.io/pypi/l/pygot.svg?style=flat-square)](https://pypi.org/project/pygot/)
-->

Python Game of Thrones board game server.


## Linting and Testing

Simple four step pipeline, eventually feeding coverage to [Codecov.io](https://codecov.io/gh/buhanec/pygot) and [Codacy](https://www.codacy.com/manual/buhanec/pygot).

```shell script
pytest tests
pycodestyle pygot tests
pydocstyle pygot tests
pylint --rcfile=setup.cfg pygot tests
```

## Testing and Coverage

Fancy stuff.

![Historical](https://codecov.io/gh/buhanec/pygot/branch/master/graphs/commits.svg)
