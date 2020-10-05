==================================================
 ``python_http_parser`` v0.1.0 Documentation
==================================================

.. contents:: Table of Contents
    :depth: 3
    :local:

----------------------------
``python_http_parser``
----------------------------
The ``python_http_parser`` package provides a simple API in which you could use
to parse and stringify HTTP messages. It can be accessed using:

.. code:: python

  import python_http_parser

``python_http_parser.parse(msg, opts)``
=======================================
* msg |str|_ | |bytes|_ The HTTP message to parse
* opts |dict|_

  - ``received_from`` |str|_ Either ``"client request"`` or ``"server response"``

* Returns: |dict|_, with the following structure:

  .. code:: python

    {
      "version": str,
      "method": str,
      "uri": str,
      "headers": dict,
      "raw_headers": list,
      "body": str
    } or {
      "version": str,
      "status_code": str,
      "status_message": str,
      "headers": dict,
      "raw_headers": list,
      "body": str
    }

The ``python_http_parser.parse()`` method parses a HTTP message, whether it is |bytes|_ or a |str|_.

For example, a HTTP message like this:

.. code:: http

  GET /index.html HTTP/1.1
  accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
  accept-encoding: gzip, deflate, br
  accept-language: en-US,en;q=0.9
  cache-control: no-cache
  pragma: no-cache
  sec-fetch-dest: document
  sec-fetch-mode: navigate
  sec-fetch-site: none
  sec-fetch-user: ?1
  upgrade-insecure-requests: 1
  user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36

Would be parsed into a |dict|_ like this:

.. code:: python

  {
    'version': 'HTTP/1.1',
    'method': 'GET',
    'uri': '/index.html',
    'headers': {
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      'accept-encoding': 'gzip, deflate, br',
      'accept-language': 'en-US,en;q=0.9',
      'cache-control': 'no-cache',
      'pragma': 'no-cache',
      'sec-fetch-dest': 'document',
      'sec-fetch-mode': 'navigate',
      'sec-fetch-site': 'none',
      'sec-fetch-user': '?1',
      'upgrade-insecure-requests': '1'
    },
    'raw_headers': [
      'accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      'accept-encoding', 'gzip, deflate, br', 'accept-language', 'en-US,en;q=0.9', 'cache-control', 'no-cache',
      'pragma', 'no-cache', 'sec-fetch-dest', 'document', 'sec-fetch-mode', 'navigate', 'sec-fetch-site', 'none',
      'sec-fetch-user', '?1', 'upgrade-insecure-requests', '1',
      'user-agent',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
      ],
    'body': ''
  }


.. |str| replace:: ``<str>``
.. _str: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
.. |bytes| replace:: ``<bytes>``
.. _bytes: https://docs.python.org/3/library/stdtypes.html#binary-sequence-types-bytes-bytearray-memoryview
.. |dict| replace:: ``<dict>``
.. _dict: https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
