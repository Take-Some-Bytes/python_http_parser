"""Shim file with `setuptools.setup()`, just in case."""

import setuptools

setuptools.setup(
    # These are here for github's dependency graph.
    extras_require={
        'test': ['pytest>=6.2.2'],
        'linting': ['pylint>=2.7.2', 'rstcheck>=3.3.1'],
        'documentation': ['docutils>=0.16']
    }
)
