===========================================================
 Constants Documentation for ``python_http_parser`` v0.3.0
===========================================================

.. contents:: Table of Contents
  :depth: 3
  :local:

----------------------------------
 ``python_http_parser.constants``
----------------------------------
``python_http_parser`` exposes a set of constants used throughout
this package. It can be accessed using:

.. code:: python

  import python_http_parser.constants

HTTP Parsing Regexes
======================
``python_http_parser`` internally uses a set of regexes to determine whether a |str|_
conforms to a specific structure; if it doesn't, an exception is raised. Here's a list
of public and stable parsing regexes.

- ``HTTP_STATUS_LINE_REGEX``: A regex for testing if a line conforms to the
  structure of a `HTTP status line`_.
- ``HTTP_REQUEST_LINE_REGEX``: Similarily to the regex above, this one tests
  if a line conforms to the structure of a `HTTP request line`_.

Parser Strictness Constants
=============================
``python_http_parser`` has 3 parsing strictness modes: ``PARSER_LENIENT``,
``PARSER_NORMAL``, and ``PARSER_STRICT``. Here's what each of them mean:

- ``PARSER_LENIENT``: This constant will tell the parser to allow messages that:

  * Does not use CRLF;
  * Uses empty header lines;
  * Uses invalid header lines;
  * Uses bad whitespace in header lines;

  ``PARSER_LENIENT`` will skip any header lines which match the last two criteria.
  This constant is equivalent to the |int|_ 1.
- ``PARSER_NORMAL``: This constant will tell the parser to parse a message with
  strictness. ``PARSER_NORMAL`` will allow messages which:

  * Do not use CRLF;
  * Uses empty header lines;

  ``PARSER_NORMAL`` will reject messages which:

  * Uses invalid header lines;
  * Uses bad whitespace in header lines;

  This constants is equivalent to the |int|_ 2.
- ``PARSER_STRICT``: This constant will tell the parser to reject any messages that:

  * Does not use CRLF;
  * Uses empty header lines;
  * Uses invalid header lines;
  * Uses bad whitespace in header lines;

  ``PARSER_STRICT`` is equivalent to the |int|_ 3.

.. |int| replace:: ``<int>``
.. |str| replace:: ``<str>``
.. _str: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
.. _int: https://docs.python.org/3/library/functions.html#int

.. _`HTTP status line`: https://tools.ietf.org/html/rfc7230#section-3.1.2
.. _`HTTP request line`: https://tools.ietf.org/html/rfc7230#section-3.1.1
