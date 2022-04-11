========================================
 ``events`` - Synchronous events helper
========================================

.. py:module:: python_http_parser.helpers.events

Version v0.4.2.

The internal ``events`` module provides a custom EventEmitter implementation.
This module is not public, and the only reason this is documented is because users
*will* need to know the API of the |EventEmitter|_ class in order to use the
|HTTPParser|_ class properly.

------------------
 Concrete Classes
------------------

~~~~~~~~~~~~~~~~~~~~~~~~
 Class ``EventEmitter``
~~~~~~~~~~~~~~~~~~~~~~~~
The ``EventEmitter`` class is a simple implementation of an event emitter, with its
API based the `Node.JS EventEmitter class`_.

Users could not construct this class directly.

``emitter.on(event, callback)``
=================================
- ``event`` |str|_ The name of the event to listen for.
- ``callback`` |Callable|_ The function to call when ``event`` is emitted.

Register a new listener for ``event``. ``callback`` can have any signature--just make
sure you call ``emitter.emit`` with the right arguments.

``emitter.once(event, callback)``
===================================
- ``event`` |str|_ The name of the event to listen for.
- ``callback`` |Callable|_ The function to call when ``event`` is emitted.

Register a new once listener for ``event``. ``callback`` can have any signature--just make
sure you call ``emitter.emit`` with the right arguments.

The listener will be removed after the first time it is called.

``emitter.off(event, callback)``
==================================
- ``event`` |str|_ The name of the event to remove ``callback`` from.
- ``callback`` |Callable|_ The function to remove.

Remove a listener from ``event``. ``callback`` is compared using hashes_.

``emitter.emit(event, *args, **kwargs)``
==========================================
- ``event`` |str|_ The name of the event to emit.
- ``*args`` |Any|_ Any positional arguments to call listeners with.
- ``**kwargs`` |Any|_ Any keyword arguments to call listeners with.

Call all listeners listening for ``event`` with the specified arguments. Do not call
this in your own code unless you know what you're doing. Calling this functions interferes
with normal events (especially in |HTTPParser|_), and may mess a lot of things up.

``emitter.listeners(event)``
==============================
- ``event`` |str|_ The name of the event to get the listeners from.
- Returns: |List|_ of |Callable|_ s.

Return all listeners listening for ``event``.

.. |str| replace:: ``<str>``
.. |Any| replace:: ``<Any>``
.. |List| replace:: ``<List>``
.. |Callable| replace:: ``<Callable>``
.. |HTTPParser| replace:: ``HTTPParser``
.. |EventEmitter| replace:: ``EventEmitter``

.. _EventEmitter: #class-eventemitter
.. _HTTPParser: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.2/docs/modules/stream.rst#class-httpparser

.. _str: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
.. _Callable: https://docs.python.org/3/library/typing.html#callable
.. _List: https://docs.python.org/3/library/stdtypes.html#list
.. _Any: https://docs.python.org/3/library/typing.html#the-any-type
.. _hashes: https://docs.python.org/3/library/functions.html#hash
.. _`Node.JS EventEmitter class`: https://nodejs.org/dist/latest-v14.x/docs/api/events.html#events_class_eventemitter
