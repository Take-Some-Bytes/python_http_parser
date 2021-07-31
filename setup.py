"""Shim file with `setuptools.setup()`, just in case."""

import setuptools

if __name__ == '__main__':
    setuptools.setup(
        install_requires=[
            "typing-extensions"
        ]
    )
