# backtrace-python

[Backtrace](http://backtrace.io/) error reporting tool for Python.

## Documentation

https://documentation.backtrace.io/python/

## Installation

### Requirements

This module supports Python 2, Python 3, and PyPy.

```
python -m pip install backtracepython
```

## Contributing

To run the test suite:

```
python setup.py test
```

Since all of these implementations of Python are supported, be sure to run the
test suite with all of them:

 * Python 2
 * Python 3
 * PyPy

### Publishing to PyPI

1. Make sure all tests pass (see above).
2. Update version number in backtracepython module.
3. Tag the version in git.

```
python2 setup.py bdist_wheel --universal
twine upload dist/*
```
