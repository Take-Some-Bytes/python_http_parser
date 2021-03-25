"""Shim file with `setuptools.setup()`, just in case."""

import setuptools

setuptools.setup(
    # These are here for github's dependency graph.
    extras_require=[
        'pytest>=6.2.2',
        'docutils>=0.16',
        'pep517>=0.10.0',
        'pylint>=2.7.2',
        'pytest>=6.2.2',
        'rstcheck>=3.3.1'
    ]
)
