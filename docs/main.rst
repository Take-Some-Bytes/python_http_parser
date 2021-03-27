==========================================================
 Main API Documentation for ``python_http_parser`` v0.3.1
==========================================================

.. contents:: Table of Contents
  :depth: 3
  :local:

------------------------
 ``python_http_parser``
------------------------
The ``python_http_parser`` main module provides a simple API in which you could use
to parse and stringify HTTP messages. It can be accessed using:

.. code:: python

  import python_http_parser

``python_http_parser.parse(msg, strictness_level, is_response)``
==================================================================
- ``msg`` |str|_ | |bytes|_ | |bytearray|_ The message to parse.
- ``strictness_level`` |int|_ How strict to be while parsing the message.
- ``is_response`` |bool|_ Whether the message is a response message.

The ``python_http_parser.parse()`` method parses a HTTP message.

The message **must** include a double newline. Any characters after the double newline
will be treated as the body, and any characters before the double newline will be treated
as part of the start line and headers.

The ``strictness_level`` parameter must equal:

- ``python_http_parser.constants.PARSER_LENIENT``, or ``1``.
- ``python_http_parser.constants.PARSER_NORMAL``, or ``2``.
- ``python_http_parser.constants.PARSER_STRICT``, or ``3``.

More information about the strictness levels can be found here_.

This function could raise:

- ``python_http_parser.errors.LengthError``.
- ``python_http_parser.errors.ParsingError``.
- ``python_http_parser.errors.FatalParsingError``.
- ``python_http_parser.errors.InvalidStructureError``.
- ``TypeError``, when the message's newline type is not CRLF (only happens in strict mode).

Refer to our `errors documentation`_ to find out what each of those errors mean.

Returns a |dict|_ with the following structure.

.. code:: python

  {
    # The following 4 fields are either None or their specified type depending
    # on whether the message was a response or request message.
    'status_code': Optional[int],
    'status_msg': Optional[str],
    'req_method': Optional[str],
    'req_uri': Optional[str],
    'http_ver': float, # The HTTP version (e.g. 1.1, 1.0...)
    # Dictionary of headers that were received.
    # Duplicates are concatenated into a list.
    'headers': Dict[str, Union[str, list]],
    'raw_headers': List[str], # The headers just as was received.
    # If we encountered double newlines, the characters after those double
    # newlines, if any.
    'body': Optional[str]
  }

``python_http_parser.decode(msg, strictness_level, is_response)``
===================================================================
Alias for |python_http_parser.parse(msg, strictness_level, is_response)|_.

.. |int| replace:: ``<int>``
.. |str| replace:: ``<str>``
.. |bytes| replace:: ``<bytes>``
.. |bytearray| replace:: ``<bytearray>``
.. |dict| replace:: ``<dict>``
.. |bool| replace:: ``<bool>``
.. |python_http_parser.parse(msg, strictness_level, is_response)| replace:: ``python_http_parser.parse(msg, strictness_level, is_response)``
.. _int: https://docs.python.org/3/library/functions.html#int
.. _str: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
.. _bytes: https://docs.python.org/3/library/stdtypes.html#bytes-objects
.. _bytearray: https://docs.python.org/3/library/stdtypes.html#bytearray-objects
.. _dict: https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
.. _bool: https://docs.python.org/3/library/stdtypes.html#bltin-boolean-values

.. _here: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.3.1/docs/constants.rst#parser-strictness-constants
.. _`errors documentation`: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.3.1/docs/errors.rst
