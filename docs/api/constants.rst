======================================================
 ``python_http_parser.constants`` - Library constants
======================================================

.. py:module:: python_http_parser.constants

Version |version|.

The ``python_http_parser.constants`` module houses various constants used in ``python_http_parser``.

----------------------
 HTTP Parsing Regexes
----------------------
``python_http_parser`` internally uses a set of regexes to determine whether a |str|_
conforms to a specific structure; if it doesn't, an exception is raised. Here's a list
of public and stable parsing regexes.

- ``HTTP_STATUS_LINE_REGEX``: A regex for testing if a line conforms to the
  structure of a `HTTP status line`_.
- ``HTTP_REQUEST_LINE_REGEX``: Similarily to the regex above, this one tests
  if a line conforms to the structure of a `HTTP request line`_.

These regexes are only used in the |parse()|_ function.

.. _parser-strictness-section:

-----------------------------
 Parser Strictness Constants
-----------------------------
There are 3 possible parser strictness modes: strict, normal, and lenient.

In STRICT mode, the |parse()|_ function will:

- Reject messages which do not use CRLF.
- Reject messages which have empty header lines.
- Reject messages which have invalid header lines.

In NORMAL mode, the |parse()|_ function will:

- Accept messages which do not use CRLF.
- Accept messages which have empty header lines.
- Reject messages which have invalid header lines.

In LENIENT mode, the |parse()|_ function will:

- Accept messages which do not use CRLF.
- Accept messages which have empty header lines.
- Accept messages which have invalid header lines.

The behaviour of the |HTTPParser|_ class currently does not change much when passed different
strictness modes, with the exception that messages which use LF will be rejected in
strict mode.

Parser strictness could be specified with the following constants:

~~~~~~~~~~~~~~~~~~~
 ``PARSER_STRICT``
~~~~~~~~~~~~~~~~~~~
.. code:: python

    PARSER_STRICT: Literal[3]

The ``PARSER_STRICT`` constant tells the parser to be strict while parsing a message. This is
equivalent to the |int|_ 3.

~~~~~~~~~~~~~~~~~~~
 ``PARSER_NORMAL``
~~~~~~~~~~~~~~~~~~~
.. code:: python

    PARSER_NORMAL: Literal[2]

The ``PARSER_STRICT`` constant tells the parser to be use normal strictness while parsing a
message. This is equivalent to the |int|_ 2.

~~~~~~~~~~~~~~~~~~~~
 ``PARSER_LENIENT``
~~~~~~~~~~~~~~~~~~~~
.. code:: python

    PARSER_LENIENT: Literal[1]

The ``PARSER_LENIENT`` constant tells the parser to be lenient while parsing a message. This
is equivalent to the |int|_ 1.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 |IntEnum|_ ``ParserStrictness``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code:: python

    class ParserStrictness(IntEnum):
        LENIENT = 1
        NORMAL = 2
        STRICT = 3

It is also possible to specify parser strictness using the ``ParserStrictness`` |IntEnum|_.
Its variants are integers, with values equivalent to the above constants.

----------------------
 Validation Constants
----------------------
There are a handful of constants in this module that *may* be useful for validation purposes.
Usage:

.. code:: python

    from python_http_parser import constants

    to_test = b'GET'

    if len(to_test.translate(None, constants.TOKENS)) == 0:
        # It's a valid HTTP token.
        print('Valid!')
    else:
        # It's not valid.
        print('Invalid.')

The main idea here is to remove characters that are valid. If there are any characters left,
that means the entire string (or bytes sequence) is invalid.

Here is a list of all validation-related constants.

+------------------+----------------------------------------------------------------+
|    ``TOKENS``    | A byte sequence containing all the characters in a HTTP token. |
+------------------+----------------------------------------------------------------+
|  ``URI_CHARS``   | A byte sequence containing all the characters in a HTTP URI.   |
+------------------+----------------------------------------------------------------+
| ``VCHAR_OR_WSP`` | A byte sequence containing all visible printing characters,    |
|                  | HTAB (horizontal tab), and space.                              |
+------------------+----------------------------------------------------------------+
|   ``OBS_TXT``    | A byte sequence containing characters classified as obsolete   |
|                  | text.                                                          |
+------------------+----------------------------------------------------------------+
|    ``DIGITS``    | A byte sequence containing all the normal digits (0-9).        |
+------------------+----------------------------------------------------------------+
|  ``HEX_DIGITS``  | A byte sequence containing all hexadecimal digits.             |
+------------------+----------------------------------------------------------------+

----------------
 Parsing Limits
----------------
The new |HTTPParser|_ and |BodyProcessor|_ classes introduced *limits* for various elements
of a HTTP message. The limits are listed below.

~~~~~~~~~~~~~~~~~~~~
 ``MAX_URI_LENGTH``
~~~~~~~~~~~~~~~~~~~~
.. code:: python

    MAX_URI_LENGTH: Literal[65535]

The longest URI the ``HTTPParser`` will accept (65535 characters).

~~~~~~~~~~~~~~~~~~~~~~~~
 ``MAX_REQ_METHOD_LEN``
~~~~~~~~~~~~~~~~~~~~~~~~
.. code:: python

    MAX_REQ_METHOD_LEN: Literal[64]

The maximum length of a parsed HTTP request method. ``HTTPParser`` does not try to
match the received HTTP method to a standard definition.

~~~~~~~~~~~~~~~~~~~~
 ``MAX_REASON_LEN``
~~~~~~~~~~~~~~~~~~~~
.. code:: python

    MAX_REASON_LEN: Literal[1024]

The longest reason phrase the ``HTTPParser`` will accept. I mean, who needs more than
1024 characters?

~~~~~~~~~~~~~~~~~~~~
 ``MAX_CHUNK_SIZE``
~~~~~~~~~~~~~~~~~~~~
.. code:: python

    MAX_CHUNK_SIZE: Literal[16777216]

The largest chunk a |ChunkedProcessor|_ will accept. In human-readable format, the
above integer is equivalent to 16MiB (16 * 1024 * 1024).

~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ``MAX_CHUNK_SIZE_DIGITS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code:: python

    MAX_CHUNK_SIZE: Literal[7]

The largest amount of digits a chunk size could have. Since 16MiB could be represented in exactly
7 hexadecimal digits (0x1000000), the |ChunkedProcessor|_ will reject any chunk size with more
than 7 digits

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ``MAX_CHUNK_EXTENSION_SIZE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code:: python

    MAX_CHUNK_EXTENSION_SIZE: Literal[4096]

The maximum of chunk extensions per chunk (4KiB). Parsing is not performed, so |ChunkedProcessor|_
limits the size of chunk extensions instead of the number of chunk extensions.

~~~~~~~~~~~~~~~~~~~~~~~~~
 ``MAX_HEADER_NAME_LEN``
~~~~~~~~~~~~~~~~~~~~~~~~~
.. code:: python

    MAX_HEADER_NAME_LEN: Literal[128]

The longest header name the |HTTPParser|_ class will accept.

~~~~~~~~~~~~~~~~~~~~~~~~~
 ``MAX_HEADER_VAL_SIZE``
~~~~~~~~~~~~~~~~~~~~~~~~~
.. code:: python

    MAX_HEADER_VAL_SIZE: Literal[16384]

The maximum size of a header value while parsing with |HTTPParser|_. In human-readable format, the
above integer is equivalent to 16KiB

.. |int| replace:: ``<int>``
.. |str| replace:: ``<str>``
.. |parse()| replace:: ``parse()``
.. |IntEnum| replace:: ``<IntEnum>``
.. |HTTPParser| replace:: ``HTTPParser``
.. |BodyProcessor| replace:: ``BodyProcessor``
.. |ChunkedProcessor| replace:: ``ChunkedProcessor``

.. _int: https://docs.python.org/3/library/functions.html#int
.. _str: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
.. _parse(): https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.2/docs/index.rst#parsemsg-strictness_level-is_response
.. _IntEnum: https://docs.python.org/3/library/enum.html#enum.IntEnum
.. _HTTPParser: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.2/docs/modules/stream.rst#class-httpparser
.. _BodyProcessor: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.2/docs/modules/body.rst#base-class-bodyprocessor
.. _ChunkedProcessor: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.2/docs/modules/body.rst#class-chunkedprocessor

.. _`HTTP status line`: https://tools.ietf.org/html/rfc7230#section-3.1.2
.. _`HTTP request line`: https://tools.ietf.org/html/rfc7230#section-3.1.1
