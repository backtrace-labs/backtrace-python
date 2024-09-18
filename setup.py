#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="backtracepython",
    version="0.4.0",
    description="Backtrace.io error reporting tool for Python",
    author="Backtrace.io",
    author_email="team@backtrace.io",
    packages=find_packages(),
    test_suite="tests",
    url="https://github.com/backtrace-labs/backtrace-python",
    install_requires=["six", "simplejson", "requests"],
    extras_require={
        "test": ["pytest"],
    },
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4",
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
