#!/usr/bin/env python

from setuptools import setup

import backtracepython

setup(
    name='BacktracePython',
    version=backtracepython.version_string,
    description='Backtrace error reporting tool for Python',
    author='Andrew Kelley',
    author_email='akelley@backtrace.io',
    packages=['backtracepython'],
    test_suite="tests",
    url='https://github.com/backtrace-labs/backtrace-python',
)
