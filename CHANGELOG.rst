====================================
 ``python_http_parser`` CHANGELOG
====================================

This is the CHANGELOG for ``python_http_parser``. All notable changes will be
written here.

The format is based on `Keep a Changelog`_, and this project adheres to `Semantic Versioning`_.

--------------------------
`v0.3.1`_ - 2021-03-26
--------------------------
Changed:
============
- Minor changes to the documentation.
- Updated ``CONTRIBUTING.rst`` a bit

--------------------------
`v0.3.0`_ - 2021-03-24
--------------------------
Added:
============
- Added three new modules in the package:

  * ``constants``, with constants that are used throughout the package;
  * ``errors``, with errors and exceptions that this package raises; and
  * ``utils``, with lots of utility functions that are used to help parse HTTP messages;

- Added new options to replace the old ones:

  * ``strictness_level``: configure the parser strictness level. Details could be found here_.
  * ``is_response``: tell the parser whether the message is a HTTP response.

- Added more `errors and exceptions`_ that could be raised by this package.
- Added a draft of package contribution guidelines.
- Added new and improved tests.
- Added GitHub workflows to automatically lint and test code changes are pushed.

Changed:
============
- Completely restructured package documentation:

  * ``main.rst`` houses the main API documentation.
  * ``errors.rst`` houses the documentation for package error classes.
  * ``constants.rst`` houses the documentation for package constants.

Fixed
============
- Fixed dependency listing in ``setup.py`` and ``setup.cfg``.

Removed:
============
- Removed all old tests.
- Removed all parsing options that was added in previous versions.
- Removed ``__private.py`` package--the stuff inside was refactored into
  other modules.

--------------------------
`v0.2.1`_ - 2021-03-03
--------------------------
Changed:
============
- Stopped using ``TypeVar`` as ``Union`` types.

Fixed:
============
- Temporarily fixed the fact that the ``parse`` method dropped any header which
  had a colon in its value (|1|_).
- Fixed the fact that the ``parse`` function was aliased as ``encode``... Now it
  is aliased (correctly) as ``decode``.

--------------------------
`v0.2.0`_ - 2020-11-21
--------------------------
Added:
============
- Added aliases for the current package functions (``encode`` for ``parse``)
- Added more parsing options:

  * ``body_required``: This option really tells the parser whether to ignore
    the fact that the message may not end with double newlines.
  * ``normalize_newlines``: This option tells the parser whether to normalize the
    message's newlines.

Changed:
============
- Updated ``README.rst`` with a section on using this project with other versions
  and/or implementations of Python.
- Updated section on testing this package in ``README.rst``.
- Updated documentation to further emphasis which version they're documenting about.
- Updated the "name" in this project's MIT license.
- Moved tests that tested the various options for this parsing into ``test_options.py``.

Fixed:
============
- Fixed the broken CHANGELOG links that lead to a specific version.

--------------------------
`v0.1.0`_ - 2020-08-05
--------------------------
Added:
============
- Added the module itself! This is the first release.
- Added the documentation (Found in ``/docs``).
- Added all metadata files.

.. Replacements.

.. |1| replace:: #1

.. Third-party resources.

.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

.. Issue numbers links.

.. _1: https://github.com/Take-Some-Bytes/python_http_parser/issues/1

.. Release links.

.. _v0.1.0: https://github.com/Take-Some-Bytes/python_http_parser/tree/v0.1.0
.. _v0.2.0: https://github.com/Take-Some-Bytes/python_http_parser/tree/v0.2.0
.. _v0.2.1: https://github.com/Take-Some-Bytes/python_http_parser/tree/v0.2.1
.. _v0.3.0: https://github.com/Take-Some-Bytes/python_http_parser/tree/v0.3.0
.. _v0.3.1: https://github.com/Take-Some-Bytes/python_http_parser/tree/v0.3.1

.. Other links.

.. _here: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.3.1/docs/constants.rst#parser-strictness-constants
.. _`errors and exceptions`: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.3.1/docs/errors.rst