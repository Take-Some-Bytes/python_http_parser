=============================================
 ``python_http_parser.errors`` - Error types
=============================================

.. py:module:: python_http_parser.errors

Version |version|.

The ``python_http_parser.errors`` module houses various exceptions this module could raise.

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

.. py:exception:: LengthError

   Raised when something length-related fails.

   For example, if a header line is too short.

   This is only raised by the |parse()| function.

.. py:exception:: ParsingError

   The generic "catch-all" exception that is raised when there is no other appropriate
   exception to raise.

   **NOTE**: ``ParsingError`` *may* be slowly replaced by other more specific exception
   classes in the long term.

   This is only raised by the |parse()| function.

.. py:exception:: NewlineError

   Raised when something related to newlines fails.

   For example, if a bare CR is received, or if LF is received in strict mode.

.. py:exception:: FatalParsingError

   A fatal variation of ``ParsingError``; ``FatalParsingError`` s raised cannot be ignored.

   ``FatalParsingError`` is currently not raised.

.. py:exception:: InvalidStructureError

   Raised when something doesn't match an expected structure.

   For example if the request line is not in the correct format.

   This is only raised by the |parse()| function.

.. py:exception:: DoneError

   Raised when a parser/processor is already done parsing/processing, but calls were made
   to process/parse more bytes.

.. py:exception:: InvalidVersion

   Raised when the received HTTP version is invalid.

.. py:exception:: InvalidStatus

   Raised when the received HTTP status code is invalid.

.. py:exception:: UnexpectedChar

   Raised when an unexpected character is encountered.

.. py:exception:: InvalidToken

   Raised when non-|HTTP token|_ characters are received where a token is required.

.. py:exception:: InvalidURI

   Raised when non-URI characters are received where a URI is required.

   As the :py:class:`HTTPParser <python_http_parser.stream.HTTPParser>` does not
   *parse* URIs, this error is only raised when invalid *characters* are received.

.. py:exception:: InvalidHeaderVal

   Raised when invalid characters are encountered in the value of a HTTP header.

.. py:exception:: InvalidChunk

   Raised when a chunk that is being processed by the |ChunkedProcessor| has syntax
   errors (e.g. missing a newline).

.. py:exception:: InvalidChunkSize

   Raised when a chunk size is invalid (e.g. has invalid characters or is too large).

.. py:exception:: InvalidChunkExtensions

   Raised when chunk extensions are too large.

   As the |ChunkedProcessor| does not *parse* chunk extensions, this error is only raised
   if the size of chunk extensions exceed the :ref:`maximum <chunk-extension-max>`.

.. py:exception:: BodyProcessorRequired
   
   Raised when a :py:class:`BodyProcessor <python_http_parser.body.BodyProcessor>` is required,
   but none was set.

.. Hack to make sure putting a hyphen before a hyperlink doesn't break anything.
.. |HTTP token| replace:: HTTP token
.. |BodyProcessor| replace:: ``BodyProcessor``
.. |ChunkedProcessor| replace:: :py:class:`ChunkedProcessor <python_http_parser.body.ChunkedProcessor>`
.. |parse()| replace:: :py:func:`parse() <python_http_parser.parse>`

.. _`HTTP token`: https://datatracker.ietf.org/doc/html/rfc7230#section-3.2.6
