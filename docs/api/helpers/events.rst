========================================
 ``events`` - Synchronous events helper
========================================

.. py:module:: python_http_parser.helpers.events

Version |version|.

The internal ``events`` module provides a custom EventEmitter implementation.
This module is not public, and the only reason this is documented is because users
*will* need to know the API of the :py:class:`EventEmitter` class in order to use the
|HTTPParser| class properly.

------------------
 Concrete Classes
------------------

.. py:class:: EventEmitter

   The ``EventEmitter`` class is a simple implementation of an event emitter, with its
   API based the `Node.JS EventEmitter class`_.

   Users *cannot* construct this class directly.

   .. py:method:: on(event: str, callback: Callable)

      :param event: The name of the event to listen for.
      :param callback: The function to call when ``event`` is emitted.
      :type event: |str|_
      :type callback: |Callable|_

      Register a new listener for ``event``. ``callback`` can have any signature--just
      make sure you call ``emitter.emit`` with the right arguments.

   .. py:method:: once(event: str, callback: Callable)

      :param event: The name of the event to listen for.
      :param callback: The function to call when ``event`` is emitted.
      :type event: |str|_
      :type callback: |Callable|_

      Register a new once listener for ``event``. ``callback`` can have any signature--just
      make sure you call ``emitter.emit`` with the right arguments.

      The listener will be removed after the first time it is called.


   .. py:method:: off(event: str, callback: Callable)

      :param event: The name of the event to remove ``callback`` from.
      :param callback: The function to remove.
      :type event: |str|_
      :type callback: |Callable|_

      Remove a listener from ``event``. ``callback`` is compared using hashes_

   .. py:method:: emit(event: str, *args, **kwargs)

      :param event: The name of the event to emit.
      :param \*args: Any positional arguments to call listeners with.
      :param \**kwargs: Any keyword arguments to call listeners with.

      Call all listeners listening for ``event`` with the specified arguments. Do not call
      this in your own code unless you know what you're doing. Calling this function interferes
      with normal events (especially in |HTTPParser|), and may mess a lot of things up.

   .. py:method:: listeners(event: str)

      :param event: The name of the event to get the listeners from.
      :returns: |List|_ of |Callable|_ s
      :type event: |str|_

      Return all listeners listening for ``event``.

.. |str| replace:: ``<str>``
.. |Any| replace:: ``<Any>``
.. |List| replace:: ``<List>``
.. |Callable| replace:: ``<Callable>``
.. |HTTPParser| replace:: :py:class:`HTTPParser <python_http_parser.stream.HTTPParser>`

.. _str: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
.. _Callable: https://docs.python.org/3/library/typing.html#callable
.. _List: https://docs.python.org/3/library/stdtypes.html#list
.. _Any: https://docs.python.org/3/library/typing.html#the-any-type
.. _hashes: https://docs.python.org/3/library/functions.html#hash
.. _`Node.JS EventEmitter class`: https://nodejs.org/dist/latest-v14.x/docs/api/events.html#events_class_eventemitter
