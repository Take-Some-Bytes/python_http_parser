========================
 ``python_http_parser``
========================
Simple HTTP parser written in pure python.

``python_http_parser`` currently offers a simple API for parsing HTTP messages
that comply to `RFC 7230`_.

This package is currently *not stable*. Before upgrading on releases, please check our
CHANGELOG_ for what changed and what you need to change. Using this package for production
is highly discouraged.

------------------------
 Basic Functional Usage
------------------------

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

--------------
 Dependencies
--------------
This package has one production dependency: |typing_extensions|_. It is only used for type hinting
compatiblity with Python versions earlier than 3.8, so it shouldn't add too much overhead.
This project also requires some tools if you wish to develop or test the code--those requirements could
be found in the ``/requirements`` folder.

Python >=3.6 is required to use this package.

.. |typing_extensions| replace:: ``typing_extensions``

.. _`CONTRIBUTING.rst`: https://github.com/Take-Some-Bytes/python_http_parser/blob/main/CONTRIBUTING.rst
.. _`CHANGELOG`: https://github.com/Take-Some-Bytes/python_http_parser/blob/main/CHANGELOG.rst
.. _here: https://github.com/Take-Some-Bytes/python_http_parser/blob/v0.4.0/docs/README.rst

.. _`RFC 7230`: https://tools.ietf.org/html/rfc7230
.. _typing_extensions: https://pypi.org/project/typing_extensions/
