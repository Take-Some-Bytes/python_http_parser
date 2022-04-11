=============================================
 ``python_http_parser.errors`` - Error types
=============================================

.. py:module:: python_http_parser.errors

Version |version|.

The ``python_http_parser.errors`` module houses various errors this module could raise.

-------------------
``.code`` property
-------------------
All exceptions raised by this package have a ``.code`` property, which is guaranteed to
not change (or not change as often) throughout different ``python_http_parser`` versions.
Here's a table of error codes and the exception class they match with.

================ ========================
Error code       Exception class
================ ========================
ELENGTH           LengthError
EPARSEFAIL        ParsingError
ENEWLINE          NewlineError
EPARSEFATAL       FatalParsingError
EINVALIDSTRUCT    InvalidStructureError
EDONE             DoneError
EHTTPVER          InvalidVersion
ESTATUS           InvalidStatus
ECHAR             UnexpectedChar
ETOKEN            InvalidToken
EURICHAR          InvalidURI
EHEADERVAL        InvalidHeaderVal
ECHUNK            InvalidChunk
ECHUNKSIZE        InvalidChunkSize
ECHUNKEXTS        InvalidChunkExtensions
EBODYPROCESSOR    BodyProcessorRequired
================ ========================

~~~~~~~~~~~~~~~~~
 ``LengthError``
~~~~~~~~~~~~~~~~~
Raised when something length-related fails, e.g. a header line is too short.

~~~~~~~~~~~~~~~~~~
 ``ParsingError``
~~~~~~~~~~~~~~~~~~
The generic "catch-all" exception that is raised when there is no other appropriate
exception to raise.

**NOTE**: ``ParsingError`` *may* be slowly replaced by other more specific exception
classes in the long term.

~~~~~~~~~~~~~~~~~~
 ``NewlineError``
~~~~~~~~~~~~~~~~~~
Raised when something related to newlines fails.

~~~~~~~~~~~~~~~~~~~~~~
 ``FatalParsingError``
~~~~~~~~~~~~~~~~~~~~~~
A fatal variation of ``ParsingError``; ``FatalParsingError`` s raised cannot be ignored.

``FatalParsingError`` is currently not raised.

~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ``InvalidStructureError``
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Raised when something doesn't match an expected structure, e.g. when the request line
is not in the correct format.

~~~~~~~~~~~~~~~
 ``DoneError``
~~~~~~~~~~~~~~~
Raised when a parser/processor is already done parsing/processing, but calls were made
to process/parse more bytes.

~~~~~~~~~~~~~~~~~~~~
 ``InvalidVersion``
~~~~~~~~~~~~~~~~~~~~
Raised when the received HTTP version is invalid.

~~~~~~~~~~~~~~~~~~~
 ``InvalidStatus``
~~~~~~~~~~~~~~~~~~~
Raised when the received HTTP status code is invalid.

~~~~~~~~~~~~~~~~~~~~
 ``UnexpectedChar``
~~~~~~~~~~~~~~~~~~~~
Raised when an unexpected character is encountered.

~~~~~~~~~~~~~~~~~~
 ``InvalidToken``
~~~~~~~~~~~~~~~~~~
Raised when non-|HTTP token|_ characters are received where a token is required.

~~~~~~~~~~~~~~~~
 ``InvalidURI``
~~~~~~~~~~~~~~~~
Raised when non-URI characters are received where a URI is required.

As the |HTTPParser|_ does not *parse* URIs, this error is only raised when invalid
*characters* are received.

~~~~~~~~~~~~~~~~~~~~~~
 ``InvalidHeaderVal``
~~~~~~~~~~~~~~~~~~~~~~
Raised when invalid characters are encountered the value of a HTTP header.

~~~~~~~~~~~~~~~~~~
 ``InvalidChunk``
~~~~~~~~~~~~~~~~~~
Raised when a chunk that is being processed by the |ChunkedProcessor|_ has syntax
errors (e.g. missing a newline).

~~~~~~~~~~~~~~~~~~~~~~
 ``InvalidChunkSize``
~~~~~~~~~~~~~~~~~~~~~~
Raised a chunk size is invalid (e.g. has invalid characters or is too large).

~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ``InvalidChunkExtensions``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Raised when chunk extensions are too large.

As the |ChunkedProcessor|_ does not *parse* chunk extensions, this error is only raised the
size of chunk extensions exceed the maximum_.

~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ``BodyProcessorRequired``
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Raised when a |BodyProcessor|_ is required, but none was set.

.. Hack to make sure putting a hyphen before a hyperlink doesn't break anything.
.. |HTTP token| replace:: HTTP token
.. |HTTPParser| replace:: ``HTTPParser``
.. |BodyProcessor| replace:: ``BodyProcessor``
.. |ChunkedProcessor| replace:: ``ChunkedProcessor``

.. _HTTPParser: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.2/docs/modules/stream.rst
.. _BodyProcessor: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.2/docs/modules/body.rst
.. _ChunkedProcessor: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.2/docs/modules/body.rst#class-chunkedprocessor
.. _maximum: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.2/docs/modules/constants.rst#max_chunk_extension_size

.. _`HTTP token`: https://datatracker.ietf.org/doc/html/rfc7230#section-3.2.6
