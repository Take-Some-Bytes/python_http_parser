=====
 API
=====

.. py:module:: python_http_parser

---------
 Modules
---------

.. toctree::
   :maxdepth: 1

   body
   constants
   errors
   stream
   helpers/events

----------------------
 Standalone functions
----------------------

.. py:function:: parse(msg: Union[str, bytes, bytearray], [strictness_level: int = 2], [is_response: bool = False]) -> dict

   Parse a HTTP message.

   :param msg: The message to parse.
   :param strictness_level: How strict to be when parsing.
   :param is_response: Specify whether the message is a HTTP response.
   :type msg: |str|_, |bytes|_, or |bytearray|_
   :type strictness_level: |int|_
   :type is_response: |bool|_
   :return: The parsed HTTP message.
   :rtype: |dict|_

   This function expects that the entire message is present in ``msg``--incomplete
   messages will not be accepted.

   For more information on parser strictness, look :ref:`here <parser-strictness-section>`.

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

.. py:function:: decode(msg: Union[str, bytes, bytearray], [strictness_level: int = 2], [is_response: bool = False]) -> dict

   Alias for :py:func:`python_http_parser.parse`.

.. |int| replace:: ``<int>``
.. |dict| replace:: ``<dict>``
.. |str| replace:: ``<str>``
.. |bytes| replace:: ``<bytes>``
.. |bytearray| replace:: ``<bytearray>``
.. |bool| replace:: ``<bool>``

.. _int: https://docs.python.org/3/library/functions.html#int
.. _str: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
.. _bytes: https://docs.python.org/3/library/stdtypes.html#bytes-objects
.. _bytearray: https://docs.python.org/3/library/stdtypes.html#bytearray-objects
.. _dict: https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
.. _bool: https://docs.python.org/3/library/stdtypes.html#bltin-boolean-values
