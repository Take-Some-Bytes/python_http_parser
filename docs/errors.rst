===========================================================
 Errors Documentation for ``python_http_parser`` v0.3.0
===========================================================

.. contents:: Table of Contents
  :depth: 3
  :local:

-------------------------------
 ``python_http_parser.errors``
-------------------------------
``python_http_parser`` raises a few custom exceptions while parsing a message.
They could be accessed using:

.. code:: python

  import python_http_parser.errors

``.code`` property
====================
All exceptions raised by this package have a ``.code`` property, which is guaranteed to
not change (or not change as often) throughout different ``python_http_parser`` versions.
Here's a table of error codes and the exception class they match with.

================ =======================
Error code       Exception class
================ =======================
    ELENGTH           LengthError
   EPARSEFAIL         ParsingError
  EPARSEFATAL      FatalParsingError
 EINVALIDSTRUCT   InvalidStructureError
================ =======================

``LengthError``
=================
``python_http_parser.errors.LengthError`` is raised when something length-related fails,
e.g. a header line is too short.

``ParsingError``
==================
``python_http_parser.errors.ParsingError`` is the generic "catch-all" exception that is
raised when there is no other appropriate exception to raise.

**NOTE**: ``ParsingError`` *may* be slowly replaced by other more specific exception
classes in the long term.

``FatalParsingError``
=======================
``python_http_parser.errors.FatalParsingError`` is a fatal variation of ``ParsingError``;
all ``FatalParsingError`` s raised cannot be ignored.

``InvalidStructureError``
===========================
``python_http_parser.errors.InvalidStructureError`` is raised when something doesn't match
an expected structure, e.g. when the request line is not in the correct format.
