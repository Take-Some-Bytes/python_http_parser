======================================================
 ``python_http_parser.stream`` - Stream-based parsing
======================================================

.. py:module:: python_http_parser.stream

Version |version|.

The ``python_http_parser.stream`` module contains classes for incremental processing
of HTTP messages, namely, the :py:class:`HTTPParser` class.

-------
 Types
-------

.. py:class:: HTTPVersion(major: int, minor: int)

   Bases: |NamedTuple|_

   The ``HTTPVersion`` namedtuple_ represents a HTTP version. The version major is
   available as the first element, or at ``version.major``, and the version minor is
   available as the second element, or at ``version.minor``.

------------------
 Concrete Classes
------------------

.. py:class:: HTTPParser(strictness: ParserStrictness, is_response: bool)

   Bases: |EventEmitter|

   :param strictness: How strict to be while parsing.
   :param is_response: Whether the message is a HTTP response message.
   :type strictness: |ParserStrictness| or |int|_
   :type is_response: |bool|_

   The ``HTTPParser`` class is a event-based push parser that allows for incremental
   processing of HTTP messages. Parts of the message (e.g. request method, status code)
   are pushed to the caller via synchronous events.

   Buffering of incomplete messages is *not taken care of* by the ``HTTPParser`` class.
   Instead, the :py:meth:`.process` method of the ``HTTPParser`` class returns an integer
   representing the number of bytes parsed. The caller then *must* buffer the unprocessed
   bytes for the next call to ``parser.process()``.

   The ``HTTPParser`` class inherits from a custom |EventEmitter| implementation, making
   registering and removing event listeners easy and straightforward.

   The ``strictness`` parameter could either be a variant of the
   :py:class:`ParserStrictness <python_http_parser.constants.ParserStrictness>` IntEnum,
   or it could be an integer with an equivalent value (see link for more details).

   **Note**: As of right now, the ``strictness`` parameter doesn't do much to change the
   behaviour of the ``HTTPParser``. The only thing it does is tell the parser to reject LF
   if ``strictness`` is equivalent to ``ParserStrictness.STRICT``.

   **Event 'error'**

      Arguments passed:

      - ``err`` |Exception|_ The error that occurred.

      Emitted each time an error occurs.

      **Note**: If an error occurs, and there are zero listeners for the ``'error'`` event,
      the error is *raised* instead of emitted.

   **Event 'req_method'**

      Arguments passed:

      - ``method`` |str|_ The request method.

      Emitted when the request method is received.

      Only emitted for requests.

   **Event 'req_uri'**

      Arguments passed:

      - ``uri`` |str|_ The URI.
   
      Emitted when the request URI is received.
   
      Only emitted for requests.
   
   **Event 'reason'**

      Arguments passed:

      - ``reason`` |str|_ The reason phrase.
   
      Emitted when the reason phrase is received.
   
      Only emitted for responses.
   
   **Event 'status_code'**

      Arguments passed:

      - ``code`` |int|_ The status code.
   
      Emitted when the response status code is received.
   
      Only emitted for responses.
   
   **Event 'http_version'**

      Arguments passed:

      - ``version`` :py:class:`<HTTPVersion> <HTTPVersion>` The HTTP version.
   
      Emitted when the HTTP version is received.
   
   **Event 'header_name'**

      Arguments passed:

      - ``name`` |str|_ The HTTP header name.
   
      Emitted when a HTTP header name is received. The header name is not modified.
   
   **Event 'header_value'**

      Arguments passed:

      - ``value`` |str|_ The HTTP header value.
   
      Emitted when a HTTP header value is received. The header value will have
      whitespace stripped from the start and end.
   
   **Event 'data'**

      Arguments passed:

      - ``chunk`` |bytes|_ The chunk of the body that was received..

      Emitted when a chunk of the HTTP body has been received. This event will only be
      emitted if a body processor has been set.

   .. py:method:: parser.finished()

      :rtype: |bool|_

      Return ``True`` if this parser is finished.

   .. py:method:: reset()

      Reset this ``HTTPParser``.

      After a ``HTTPParser`` is reset, it may be used to parse another HTTP message.

   .. py:method:: has_body(has_body: bool = None) -> bool

      If ``has_body`` is not provided, return a boolean representing whether this
      parser is expecting a body. Otherwise, set whether this parser is expecting a
      body to ``has_body``.

   ..  py:method:: body_processor(body_processor: BodyProcessor = None) -> BodyProcessor

      :param body_processor: The body processor to use.
      :type body_processor: |BodyProcessor|

      If ``body_processor`` is not provided, return the |BodyProcessor| this parser is
      currently using. Otherwise, set this parser's |BodyProcessor| to ``body_processor``.

   .. py:method:: process(data: Union[bytes, bytearray, memoryview]) -> int

      :param data: The chunk of data to process.
      :type data: Union[|bytes|_, |bytearray|_, |memoryview|_]

      Process ``data`` as part of the current HTTP message. ``data`` will not be mutated
      when parsing.

      Return the number of bytes parsed. Any unparsed bytes *must* be buffered for the next
      call to ``parser.process()``.

      The integer ``-1`` means that an error was encountered, and thus parsing should stop.

      Example with basic buffering using |bytearray|_ and |memoryview|_.

      .. code:: python
      
          from python_http_parser.stream import HTTPParser

          # In a real program you would get a socket using socket.socket or something else.
          socket = get_socket_somehow()
          # Let's assume this is a request.
          parser = HTTPParser(is_response=False)

          # Set up the buffer.
          buf = bytearray(256)
          view = memoryview(buf)
          buf_len = 0

          # Add listeners...
          # Here, you would add your various event listeners to the parser.
          def on_error(err):
              # In a real application you would handle the error properly instead
              # of just raising it.
              raise err
          parser.on('error', on_error)
          # Other listeners... (e.g. 'http_version', 'header_name')

          # Keep parsing until parser is finished.
          while not parser.finished():
              # Receive another KiB from the socket.
              size = 1024
              chk = view[buf_len:buf_len+size]
              socket.recv_into(chk)
              buf_len += size

              # Give it to the parser.
              ret = parser.process(view[:buf_len])
              if ret >= 0:
                  # No error--if the parser still isn't done, keep processing.
                  # Keep the remaining bytes in the buffer.
                  view[:len(view)-ret] = view[ret:]
                  buf_len -= ret
              if ret < 0:
                  # Error!
                  break

          # Here, the parser could either be done, or it had an error.

.. |int| replace:: ``<int>``
.. |str| replace:: ``<str>``
.. |bool| replace:: ``<bool>``
.. |bytes| replace:: ``<bytes>``
.. |bytearray| replace:: ``<bytearray>``
.. |memoryview| replace:: ``<memoryview>``
.. |Exception| replace:: ``<Exception>``

.. |NamedTuple| replace:: ``<NamedTuple>``
.. |BodyProcessor| replace:: :py:class:`BodyProcessor <python_http_parser.body.BodyProcessor>`
.. |EventEmitter| replace:: :py:class:`EventEmitter <python_http_parser.helpers.events.EventEmitter>`
.. |ParserStrictness| replace:: :ref:`ParserStrictness <parser-strictness-section>`

.. _int: https://docs.python.org/3/library/functions.html#int
.. _str: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
.. _bool: https://docs.python.org/3/library/stdtypes.html#bltin-boolean-values
.. _bytes: https://docs.python.org/3/library/stdtypes.html#bytes
.. _bytearray: https://docs.python.org/3/library/stdtypes.html#bytearray-objects
.. _memoryview: https://docs.python.org/3/library/stdtypes.html#memoryview
.. _Exception: https://docs.python.org/3/library/exceptions.html#Exception
.. _namedtuple: https://docs.python.org/3.9/library/typing.html?highlight=namedtuple#typing.NamedTuple
