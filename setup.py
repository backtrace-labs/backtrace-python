#!/usr/bin/env python

import os

from setuptools import find_packages, setup

current_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="backtracepython",
    version="0.4.2",
    description="Backtrace.io error reporting tool for Python",
    author="Backtrace.io",
    author_email="team@backtrace.io",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    license="MIT",
    test_suite="tests",
    url="https://github.com/backtrace-labs/backtrace-python",
    install_requires=["six", "simplejson", "requests"],
    extras_require={
        "test": ["pytest"],
    },
    project_urls={
        "Homepage": "https://backtrace.io",
        "Source": "https://github.com/backtrace-labs/backtrace-python",
        "Changelog": "https://github.com/backtrace-labs/backtrace-python/blob/master/CHANGELOG.md",
        "Documentation": "https://docs.saucelabs.com/error-reporting/language-integrations/python/",
    },
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: System :: Monitoring",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
