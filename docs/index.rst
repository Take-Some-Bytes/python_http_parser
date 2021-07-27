================================
 Package ``python_http_parser``
================================
Version v0.4.0.

The ``python_http_parser`` package provides classes and functions for parsing HTTP
messages. This package aims to provide a usable, performant (in terms of Python)
API, written purely in Python. As of right now, this package is *very* incomplete, and should not,
in any circumstances, be used in production.

This package could be accessed by:

.. code:: python

    import python_http_parser

Sub-modules must be imported individually

---------
 Modules
---------
`body`_
    Classes for processing HTTP bodies.
`constants`_
    Package constants.
`errors`_
    Errors that could be raised by this package.
`stream`_
    Classes for incremental processing of HTTP messages. Plays well with streams.

-----------
 Functions
-----------

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ``parse(msg, strictness_level, is_response)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- ``msg`` |str|_ | |bytes|_ | |bytearray|_ The message to parse.
- ``strictness_level`` |int|_ How strict to be while parsing the message.
- ``is_response`` |bool|_ Whether the message is a response message.
- Returns: |dict|_.

The ``python_http_parser.parse()`` function parses a HTTP message.

This function expects that the entire message is present in ``msg``--incomplete
messages will not be accepted.

For more information on parser strictness, look here_.

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
      'headers': Dict[str, Union[str, List[str]]],
      'raw_headers': List[str], # The headers just as was received.
      # If we encountered double newlines, the characters after those double
      # newlines, if any.
      'body': Optional[str]
    }

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ``decode(msg, strictness_level, is_response)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Alias for |parse(msg, strictness_level, is_response)|_.

.. _`body`: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.0/docs/modules/body.rst
.. _`constants`: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.0/docs/modules/constants.rst
.. _`errors`: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.0/docs/modules/errors.rst
.. _`stream`: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.0/docs/modules/stream.rst

.. _here: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.0/docs/modules/constants.rst#parser-strictness-constants

.. |int| replace:: ``<int>``
.. |str| replace:: ``<str>``
.. |bytes| replace:: ``<bytes>``
.. |bytearray| replace:: ``<bytearray>``
.. |dict| replace:: ``<dict>``
.. |bool| replace:: ``<bool>``
.. |parse(msg, strictness_level, is_response)| replace:: ``parse(msg, strictness_level, is_response)``

.. _int: https://docs.python.org/3/library/functions.html#int
.. _str: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
.. _bytes: https://docs.python.org/3/library/stdtypes.html#bytes-objects
.. _bytearray: https://docs.python.org/3/library/stdtypes.html#bytearray-objects
.. _dict: https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
.. _bool: https://docs.python.org/3/library/stdtypes.html#bltin-boolean-values
