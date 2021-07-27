====================================
 Module ``python_http_parser.body``
====================================
Version v0.4.0.

The ``python_http_parser.body`` module provides classes for processing HTTP
bodies. It includes an Abstract Base Class called ``BodyProcessor``, which represents
a generic class that processes HTTP bodies, and two concrete classes, ``FixedLenProcessor``
(to process bodies with fixed length) and ``ChunkedProcessor`` (to process chunked bodies).

-----------------------
 Abstract Base Classes
-----------------------

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 Base Class ``BodyProcessor``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``BodyProcessor`` ABC represents a generic class that processes HTTP bodies.
All concrete classes in this module implement this class.

Required Methods
==================

Abstract ``processor.process(chunk, allow_lf)``
-------------------------------------------------
- ``chunk`` |bytes|_ The next chunk of data to process.
- ``allow_lf`` |bool|_ Whether to allow LF instead of CRLF.
- Returns: |int|_ The number of bytes processed.

This method is called whenever more data is available to be processed as part of the HTTP
body. Implementors may ignore the ``allow_lf`` parameter if it does not apply to their
implementation.

It is recommended that buffering of data should not be performed. Instead, implementors
should leave buffering up to the caller, and return the number of bytes processed so that
the caller could calculate how many bytes to buffer.

When more data is available, implementors should call the function stored in
``processor.callbacks['data']``, with the processed data as its sole argument.

When an error occurs, implementors should call the function stored in
``processor.callbacks['error']``, with the error that occurred as its sole argument.

When the HTTP body is finished, implementors should call the function stored in
``processor.callbacks['finished']``, with no arguments.

Provided Methods
==================

``processor.on_data(callback)``
---------------------------------
- ``callback`` |Callable|_ Callback signature:

  - ``chunk`` |bytes|_ The processed data.
  - Returns: ``<None>``

Set the callback that will be called when more processed data is available. The callback is
stored in ``processor.callbacks['data']``.

Implementors should not override this method.

``processor.on_error(callback)``
----------------------------------
- ``callback`` |Callable|_ Callback signature:

  - ``err`` |Exception|_ The error that occurred.
  - Returns: ``<None>``

Set the callback that will be called when an error occurs. The callback is stored at
``processor.callbacks['error']``.

Implementors should not override this method.

``processor.on_finished(callback)``
-------------------------------------
- ``callback`` |Callable|_ Callback signature:

  - Returns: ``<None>``

Set the callback that will be called when the HTTP body is finished. The callback is stored
at ``processor.callbacks['finished']``.

Implementors should not override this method.

------------------
 Concrete Classes
------------------

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 Class ``FixedLenProcessor``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``FixedLenProcessor`` class represents a body processor which receives HTTP bodies of
a fixed length.

This class does nothing but count received bytes and compare it to the expected length of
the HTTP body.

``FixedLenProcessor.__init__(body_len)``
==========================================
- ``body_len`` |int|_ The expected length of the body.

Create a new ``FixedLenProcessor``. ``body_len`` must be an integer representing
the length of the HTTP body, as specified in (for example) the Content-Length header.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 Class ``ChunkedProcessor``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``ChunkedProcessor`` class represents a body processor which receives chunked HTTP bodies.
Use this class when you receive a Transfer-Encoding: chunked header.

This class does not place limits on the number of chunks it will accept. It does, however,
place a limit on the maximum size of a chunk: 16MiB. If any chunk is received that is larger
than that, the processor will immediately error out.

This class allows chunk extensions, but does not parse them. Chunk extensions are limited to
4KiB per chunk.

``ChunkedProcessor.__init__()``
==========================================
Create a new ``ChunkedProcessor``.

This function accepts no arguments.

.. |int| replace:: ``<int>``
.. |bool| replace:: ``<bool>``
.. |bytes| replace:: ``<bytes>``
.. |Callable| replace:: ``<Callable>``
.. |Exception| replace:: ``<Exception>``

.. _int: https://docs.python.org/3/library/functions.html#int
.. _bytes: https://docs.python.org/3/library/stdtypes.html#bytes
.. _bool: https://docs.python.org/3/library/stdtypes.html#bltin-boolean-values
.. _Callable: https://docs.python.org/3/library/typing.html#callable
.. _Exception: https://docs.python.org/3/library/exceptions.html#Exception
