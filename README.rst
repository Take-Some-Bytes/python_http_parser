========================
 ``python_http_parser``
========================
Simple HTTP parser written in pure python.

``python_http_parser`` currently offers a simple API for parsing HTTP messages
that comply to `RFC 7230`_.

--------------
 Basic Usage
--------------

.. code:: python

  import python_http_parser

  msg = """\
  GET / HTTP/1.1
  Host: example.com
  Accept: */*

  """

  result = python_http_parser.parse(msg)

  # ``result`` will be a ``dict`` with request method, uri, http version,
  # headers, raw headers, and the body, if any.
  print(result)

Find the full documentation here_.

------------
 Installing
------------
You could easily install this package with pip:

.. code:: bash

  $ pip install --upgrade python_http_parser

--------------
 Contributing
--------------
Please see `CONTRIBUTING.rst`_

.. _`CONTRIBUTING.rst`: https://github.com/Take-Some-Bytes/python_http_parser/blob/main/CONTRIBUTING.rst
.. _`RFC 7230`: https://tools.ietf.org/html/rfc7230
.. _here: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.3.0/docs/README.rst
