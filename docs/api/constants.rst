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

.. py:data:: HTTP_STATUS_LINE_REGEX: str

   A regex for testing if a line conforms to the structure of a `HTTP status line`_.

.. py:data:: HTTP_REQUEST_LINE_REGEX: str

   Similar to the regex above, this one tests if a line conforms to the structure
   of a `HTTP request line`_.

These regexes are only used in the |parse()| function.

.. _parser-strictness-section:

-----------------------------
 Parser Strictness Constants
-----------------------------
There are 3 possible parser strictness modes: strict, normal, and lenient.

In STRICT mode, the |parse()| function will:

- Reject messages which do not use CRLF.
- Reject messages which have empty header lines.
- Reject messages which have invalid header lines.

In NORMAL mode, the |parse()| function will:

- Accept messages which do not use CRLF.
- Accept messages which have empty header lines.
- Reject messages which have invalid header lines.

In LENIENT mode, the |parse()| function will:

- Accept messages which do not use CRLF.
- Accept messages which have empty header lines.
- Accept messages which have invalid header lines.

The behaviour of the |HTTPParser| class currently does not change much when passed different
strictness modes, with the exception that messages which use LF will be rejected in
strict mode.

Parser strictness could be specified with the following constants:

.. py:data:: PARSER_STRICT: Final[3]

   The ``PARSER_STRICT`` constant tells the parser to be strict while parsing a message. This is
   equivalent to the |int|_ 3.

.. py:data:: PARSER_NORMAL: Final[2]

The ``PARSER_NORMAL`` constant tells the parser to be use normal strictness while parsing a
message. This is equivalent to the |int|_ 2.

.. py:data:: PARSER_LENIENT: Final[1]

The ``PARSER_LENIENT`` constant tells the parser to be lenient while parsing a message. This
is equivalent to the |int|_ 1.

Parser strictness can also be specified using the following |IntEnum|_

.. py:class:: ParserStrictness

   Bases: |IntEnum|_

   .. py:attribute:: LENIENT: Final[1]

      Same as :py:const:`PARSER_LENIENT`.

   .. py:attribute:: NORMAL: Final[2]

      Same as :py:const:`PARSER_NORMAL`.

   .. py:attribute:: STRICT: Final[3]

      Same as :py:const:`PARSER_STRICT`.

   Values of this enum's fields are equivalent to those above.

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

Here is a table of all validation-related constants.

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
The new |HTTPParser| and |BodyProcessor| classes introduced *limits* for various
elements of a HTTP message. The limits are listed below.

.. py:data:: MAX_URI_LENGTH: Final[65535]

   The longest URI the |HTTPParser| will accept (65535 characters).

.. py:data:: MAX_REQ_METHOD_LEN: Final[64]

   The maximum length of a parsed HTTP request method. |HTTPParser| does not try to
   match the received HTTP method to a standard definition.

.. py:data:: MAX_REASON_LEN: Final[1024]

   The longest reason phrase the |HTTPParser| will accept. I mean, who needs more than
   1024 characters?

.. py:data:: MAX_CHUNK_SIZE: Final[16777216]

   The largest chunk a |ChunkedProcessor| will accept. In human-readable format, the
   above integer is equivalent to 16MiB (16 * 1024 * 1024).

.. py:data:: MAX_CHUNK_SIZE_DIGITS: Final[7]

   The largest amount of digits a chunk size could have. Since 16MiB could be represented in
   exactly 7 hexadecimal digits (0x1000000), the |ChunkedProcessor| will reject any chunk
   size with more than 7 digits

.. py:data:: MAX_CHUNK_EXTENSION_SIZE: Final[4096]

   The maximum of chunk extensions per chunk (4KiB). Parsing is not performed, so
   |ChunkedProcessor| limits the size of chunk extensions instead of the number
   of chunk extensions.

.. py:data:: MAX_HEADER_NAME_LEN: Final[128]

   The longest header name the |HTTPParser| class will accept.

.. py:data:: MAX_HEADER_VAL_SIZE: Final[16384]

   The maximum size of a header value while parsing with |HTTPParser|. In human-readable
   format, the above integer is equivalent to 16KiB

.. |int| replace:: ``<int>``
.. |str| replace:: ``<str>``
.. |parse()| replace:: :py:func:`parse() <python_http_parser.parse>`
.. |IntEnum| replace:: ``<IntEnum>``
.. |HTTPParser| replace:: :py:class:`HTTPParser <python_http_parser.stream.HTTPParser>`
.. |BodyProcessor| replace:: :py:class:`BodyProcessor <python_http_parser.body.BodyProcessor>`
.. |ChunkedProcessor| replace:: :py:class:`ChunkedProcessor <python_http_parser.body.ChunkedProcessor>`

.. _int: https://docs.python.org/3/library/functions.html#int
.. _str: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
.. _IntEnum: https://docs.python.org/3/library/enum.html#enum.IntEnum

.. _`HTTP status line`: https://tools.ietf.org/html/rfc7230#section-3.1.2
.. _`HTTP request line`: https://tools.ietf.org/html/rfc7230#section-3.1.1
