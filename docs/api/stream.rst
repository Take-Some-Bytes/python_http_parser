======================================
 Module ``python_http_parser.stream``
======================================
Version v0.4.2.

The ``python_http_parser.stream`` module contains classes for incremental processing
of HTTP messages, namely, the |HTTPParser|_ class.

-------
 Types
-------

~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 Namedtuple ``HTTPVersion``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The ``HTTPVersion`` namedtuple_ represents a HTTP version. The version major is
available as the first element, or at ``version.major``, and the version minor is
available as the second element, or at ``version.minor``.

------------------
 Concrete Classes
------------------

~~~~~~~~~~~~~~~~~~~~~~
 Class ``HTTPParser``
~~~~~~~~~~~~~~~~~~~~~~
The ``HTTPParser`` class is a event-based push parser that allows for incremental
processing of HTTP messages. Parts of the message (e.g. request method, status code)
are pushed to the caller via synchronous events.

Buffering of incomplete messages is *not taken care of* by the ``HTTPParser`` class.
Instead, the |.process()|_ method of the ``HTTPParser`` class returns an integer
representing the number of bytes parsed. The caller then *must* buffer the unprocessed
bytes for the next call to ``parser.process()``.

The ``HTTPParser`` class inherits from a custom |EventEmitter|_ implementation, making
registering and removing event listeners easy and straightforward.

``HTTPParser.__init__(strictness, is_response)``
==================================================
- ``strictness`` |ParserStrictness|_ | |int|_ How strict to be while parsing the message.
- ``is_response`` |bool|_ Whether to expect responses or not.

Create a new ``HTTPParser``.

A HTTPParser object provides an incremental, event-based API for parsing HTTP messages.
Parsed parts of the message are pushed to the caller via synchronous events.

The ``strictness`` parameter could either be a variant of the |ParserStrictness|_ IntEnum,
or it could be an integer with an equivalent value (see link for more details).

**Note**: As of right now, the ``strictness`` parameter doesn't do much to change the
behaviour of the ``HTTPParser``. The only thing it does is tell the parser to reject LF
if ``strictness`` is equivalent to ``ParserStrictness.STRICT``.

Event ``'error'``
==================
- ``err`` |Exception|_ The error that occurred.

Emitted each time an error occurs.

**Note**: If an error occurs, and there are zero listeners for the ``'error'`` event, the
error is *raised* instead of emitted.

Event ``'req_method'``
=======================
- ``method`` |str|_ The request method.

Emitted when the request method is received.

Only emitted for requests.

Event ``'req_uri'``
=====================
- ``uri`` |str|_ The URI.

Emitted when the request URI is received.

Only emitted for requests.

Event ``'reason'``
====================
- ``reason`` |str|_ The reason phrase.

Emitted when the reason phrase is received.

Only emitted for responses.

Event ``'status_code'``
=========================
- ``code`` |int|_ The status code.

Emitted when the response status code is received.

Only emitted for responses.

Event ``'http_version'``
==========================
- ``version`` |HTTPVersion|_ The HTTP version.

Emitted when the HTTP version is received.

Event ``'header_name'``
==========================
- ``name`` |str|_ The HTTP header name.

Emitted when a HTTP header name is received. The header name is not modified.

Event ``'header_value'``
==========================
- ``value`` |str|_ The HTTP header value.

Emitted when a HTTP header value is received. The header value will have
whitespace stripped from the start and end.

Event ``'data'``
==========================
- ``chunk`` |bytes|_ The chunk of the body that was received..

Emitted when a chunk of the HTTP body has been received. This event will only be
emitted if a body processor has been set.

``parser.finished()``
=======================
- Returns: |bool|_

Return ``True`` if this parser is finished.

``parser.reset()``
=======================
Reset this ``HTTPParser``.

After you reset a ``HTTPParser``, you may use it to parse another HTTP message.

``parser.has_body([has_body])``
=================================
- ``has_body`` |bool|_

If ``has_body`` is not provided, return a boolean representing whether this parser
is expecting a body. Otherwise, set whether this parser is expecting a body to
``has_body``.

``parser.body_processor([body_processor])``
=============================================
- ``body_processor`` |BodyProcessor|_ The body processor to use.

If ``body_processor`` is not provided, return the |BodyProcessor|_ this parser is
currently using. Otherwise, set this parser's |BodyProcessor|_ to ``body_processor``.

``parser.process(data)``
=============================================
- ``data`` |bytes|_ | |bytearray|_ The chunk of data to process.

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
        # We have to create a new bytes object because the .process method
        # requires a bytes-like object to function properly, and the bytearray
        # we made has extra null bytes in it.
        ret = parser.process(bytes(view[:buf_len]))
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
.. |.process()| replace:: ``.process()``
.. |HTTPParser| replace:: ``HTTPParser``
.. |HTTPVersion| replace:: ``<HTTPVersion>``
.. |EventEmitter| replace:: ``EventEmitter``
.. |BodyProcessor| replace:: ``<BodyProcessor>``
.. |ParserStrictness| replace:: ``<ParserStrictness>``

.. _.process(): #no
.. _HTTPParser: #class-httpparser
.. _HTTPVersion: #namedtuple-httpversion

.. _int: https://docs.python.org/3/library/functions.html#int
.. _str: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
.. _bool: https://docs.python.org/3/library/stdtypes.html#bltin-boolean-values
.. _bytes: https://docs.python.org/3/library/stdtypes.html#bytes
.. _bytearray: https://docs.python.org/3/library/stdtypes.html#bytearray-objects
.. _memoryview: https://docs.python.org/3/library/stdtypes.html#memoryview
.. _BodyProcessor: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.2/docs/modules/body.rst#base-class-bodyprocessor
.. _namedtuple: https://docs.python.org/3/library/collections.html#collections.namedtuple
.. _Exception: https://docs.python.org/3/library/exceptions.html#Exception
.. _EventEmitter: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.2/docs/modules/helpers/events.rst#class-eventemitter
.. _ParserStrictness: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.2/docs/modules/constants.rst#parser-strictness-constants
