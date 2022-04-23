======================================================
 ``python_http_parser.body`` - Processing HTTP bodies
======================================================

.. py:module:: python_http_parser.body

Version |version|.

The ``python_http_parser.body`` module provides classes for processing HTTP
bodies. It includes an Abstract Base Class called ``BodyProcessor``, which represents
a generic class that processes HTTP bodies, and two concrete classes, ``FixedLenProcessor``
(to process bodies with fixed length) and ``ChunkedProcessor`` (to process chunked bodies).

-----------------------
 Abstract Base Classes
-----------------------

.. py:class:: BodyProcessor

   The ``BodyProcessor`` ABC represents a generic class that processes HTTP bodies.
   All concrete classes in this module implement this class.

    .. py:method:: process(chunk: bytes, allow_lf: bool) -> int

      Process the next chunk as part of the HTTP body.

      :abstractmethod:
      :param chunk: The next chunk of data to process.
      :param allow_lf: Whether to allow LF-style line endings.
      :type chunk: |bytes|_
      :type allow_lf: |bool|_
      :returns: The number of bytes processed.
      :rtype: |int|_

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
   
   .. py:method:: on_data(callback: Callable[bytes]) -> None

      Register a callback to be called when more processed data is available.

      :param callback: The function to invoke.
      :rtype: ``<None>``

      Set the callback that will be called when more processed data is available. The callback is
      stored in ``processor.callbacks['data']``.

      Implementors should not override this method.

   .. py:method:: on_error(callback: Callable[Exception]) -> None

      Register a callback to be called when an exception occurs.

      :param callback: The function to invoke.
      :rtype: ``<None>``

      Set the callback that will be called when an error occurs. The callback is stored at
      ``processor.callbacks['error']``.

      Implementors should not override this method.

   .. py:method:: on_finished(callback: Callable[Exception]) -> None

      Register a callback to be called when the body processing completes.

      :param callback: The function to invoke.
      :rtype: ``<None>``

      Set the callback that will be called when the HTTP body is finished. The callback is stored
      at ``processor.callbacks['finished']``.

      Implementors should not override this method.

------------------
 Concrete Classes
------------------

.. py:class:: FixedLenProcessor(body_len: int)
   
   The ``FixedLenProcessor`` class represents a body processor which receives HTTP bodies of
   a fixed length.

   This class does nothing but count received bytes and compare it to the expected length of
   the HTTP body.

   Implements :py:class:`BodyProcessor`.

   :param body_len: The expected length of the body.
   :type body_len: |int|_

   To construct a ``FixedLenProcessor``, one must call the constructor with the expected length
   of the HTTP body as an |int|_.

.. py:class:: ChunkedProcessor

  The ``ChunkedProcessor`` class represents a body processor which receives chunked HTTP bodies.
  Use this class when a Transfer-Encoding: chunked header is received.

  This class does not place limits on the number of chunks it will accept. It does, however,
  place a limit on the maximum size of a chunk: 16MiB. If any chunk is received that is larger
  than that, the processor will immediately error out.

  This class allows chunk extensions, but does not parse them. Chunk extensions are limited to
  4KiB per chunk. Chunk extensions currently cannot be accessed; this is a known limitation. A
  fix is expected sometime in the future.

  Implements :py:class:`BodyProcessor`.

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
