"""Shim file with `setuptools.setup()`, just in case."""

import setuptools

setuptools.setup(
  # These are here for github's dependency graph
  install_requires=[
    "docutils>=0.16"
  ],
  tests_require=[
    "pytest>=6.0.1"
  ]
)
