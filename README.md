# backtrace-python

[Backtrace](http://backtrace.io/) error reporting tool for Python.

## Usage

```python
import backtracepython as bt
bt.initialize(
    endpoint="https://console.backtrace.io",
    token="51cc8e69c5b62fa8c72dc963e730f1e8eacbd243aeafc35d08d05ded9a024121",
)
```

## Installation

### Requirements

 * Python >= 2.7.12 or Python >= 3.5.2

```
python -m pip install BacktracePython
```

## Contributing

To run the test suite:

```
python setup.py test
```

Be sure to run the test suite with both Python 2 and Python 3 since both are
supported simultaneously.
