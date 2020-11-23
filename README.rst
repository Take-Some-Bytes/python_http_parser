========================
 ``python_http_parser``
========================
Simple HTTP parser written in pure python.

``python_http_parser`` has only been tested with `CPython 3.8`_–it is *not* guaranteed to
work with any other versions and/or implementations of Python. You are welcome to
test this package with other implementations and/or versions of Python, and you may also
open an issue if you think a compatibility issue between this project and a implementation
and/or version of Python could be fixed.

**This project is not complete**! Do not, I repeat, **DO NOT** use it for production.

----------------
Documentation
----------------
Read the documentation here_.

-----------------------
Running the tests
-----------------------
To run the tests, either:

- Download the files of this Git repository, make sure you have ``pytest``, and run
  ``make test`` in the project root.
- Download (or somehow grab) the source distribution of this package, either from
  PyPI or from GitHub. And again, make sure you have ``pytest``, and run ``make test``
  in the project root.

.. _here: https://github.com/Take-Some-Bytes/python_http_parser/blob/master/docs/README.rst
.. _CPython 3.8: https://github.com/python/cpython/tree/v3.8.6
