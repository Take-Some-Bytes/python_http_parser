========================
 ``python_http_parser``
========================
HTTP parser written in pure python.

This package is currently *not stable*. Before upgrading on releases, please check the
CHANGELOG_ for what changed and what you need to change. Using this package for production
is highly discouraged.

----------
 Features
----------

- Simple, functional API for parsing complete messages.
- Event-based, stream-friendly API for parsing messages that may or may not be complete.
- Event-based, stream-friendly APIs for processing fixed length and chunked HTTP bodies.

------------------------
 Basic Functional Usage
------------------------
For simple parsing of complete messages.

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

--------------------
 Stream-based Usage
--------------------
For more complex parsing of messages that may or may not arrive at once.

.. code:: python

  import python_http_parser
  import python_http_parser.stream

  msg = b"""\
  GET / HTTP/1.1
  Host: example.com
  Accept: */*

  """

  parser = python_http_parser.stream.HTTPParser(is_response=False)

  # Message parts are pushed via synchronous events.
  # Decorators are not supported yet.
  def on_error(err):
      raise err
  def on_method(method):
      print(f'Method: {method}')
  # Etc, etc

  parser.on('error', on_error)
  parser.on('method', on_method)
  # Etc, etc

  # ret can be negative if an error occurred.
  # Otherwise, ret represents the number of bytes processed.
  ret = parser.process(msg)

  print(f'Parser finished: {parser.finished()}')

Find the full documentation here_.

------------
 Installing
------------
This package is available on PyPI:

.. code:: shell

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

Python >=3.7 is required to use this package.

.. |typing_extensions| replace:: ``typing_extensions``

.. _`CONTRIBUTING.rst`: https://github.com/Take-Some-Bytes/python_http_parser/blob/main/CONTRIBUTING.rst
.. _`CHANGELOG`: https://github.com/Take-Some-Bytes/python_http_parser/blob/main/CHANGELOG.rst
.. _here: https://python-http-parser.readthedocs.io/en/latest/

.. _typing_extensions: https://pypi.org/project/typing_extensions/
