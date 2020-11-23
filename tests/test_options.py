"""Tests the parser when passed different parsing options."""

from .context import python_http_parser

def test_parser_optional_body():
  # Test with body, but with the `body_required` option set to False.
  err = None
  parsed_msg = None
  msg_with_body = \
    "POST /index.html HTTP/1.1\r\n" + \
    "Accept-Encoding: gzip, deflate\r\n" + \
    "ACCEPT-LANGUAGE: en-US,en;q=0.9\r\n" + \
    "Cache-Control: no-cache\r\n" + \
    "Content-Length: 3282" + \
    "Content-Type: text/plain " + \
    "cONNECTION: keep-alive\r\n" + \
    "Pragma: no-cache\r\n" + \
    "Upgrade-Insecure-Requests: 1\r\n" + \
    "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36\r\n" + \
    """
hortoncheng@Charless-iMac colonialwars-current % make dev
clear&&DEBUG=colonialwars node --inspect server.js
Debugger listening on ws://127.0.0.1:9229/c8845c1b-dfd7-412a-96d2-63b937975029
For help, see: https://nodejs.org/en/docs/inspector
  colonialwars Initializing Colonial Wars web application. +0ms
  colonialwars Exported and made loggers. +160ms
  colonialwars Exported and made Game manager. +1ms
  colonialwars Exported and made JWT and cookie secrets. +0ms
  colonialwars Exported server cache. +0ms
  colonialwars Exported and made Socket.IO session storage. +0ms
  colonialwars Exported and initialized helmet module functions. +1ms
  colonialwars Registered HTML route handlers. +2ms
  colonialwars Registered CSP report route, XHR route, and fallback handler. +0ms
  colonialwars Exported middleware handlers. +1ms
Sun, 08 Nov 2020 21:15:06 -08:00 [Server_log] info: All modules have been loaded; starting Express and Socket.IO servers.
  colonialwars Server instances created. +21ms
  colonialwars Express middleware and handlers have been mounted. +1ms
Sun, 08 Nov 2020 21:15:06 -08:00 [Server_log] info: Server running on http://localhost:8000.
^CSun, 08 Nov 2020 21:15:11 -08:00 [Server_log] info: Received signal SIGINT. Shutting down application...
Sun, 08 Nov 2020 21:15:11 -08:00 [Server_log] info: Server closed successfully. Exiting...

hortoncheng@Charless-iMac colonialwars-current % cd ../colonialwars

hortoncheng@Charless-iMac colonialwars % make dev
clear&&DEBUG=colonialwars node --inspect server.js
Debugger listening on ws://127.0.0.1:9229/b8ceabad-4908-4134-87ba-5e637539b42a
For help, see: https://nodejs.org/en/docs/inspector
  colonialwars Initializing Colonial Wars web application. +0ms
  colonialwars Exported utility methods. +218ms
  colonialwars Frozen and exported constants. +1ms
  colonialwars Returning console-only transports. +13ms
  colonialwars Returning 1 transports for logger Server-logger. +0ms
  colonialwars Returning 1 transports for logger Security-logger. +4ms
  colonialwars Exported and made winston loggers. +1ms
  colonialwars Exported and made Game manager. +0ms
  colonialwars Exported and made JWT and cookie secrets. +0ms
  colonialwars Exported server cache. +1ms
  colonialwars Exported and made Socket.IO session storage. +1ms
  colonialwars Exported and initialized helmet module functions. +0ms
  colonialwars Registered HTML route handlers. +2ms
  colonialwars Registered CSP report route, XHR route, and fallback handler. +1ms
  colonialwars Exported middleware handlers. +0ms
Colonialwars_server: 2020-11-09T05:15:19.699Z [Server_log] info: All modules have been loaded; starting Express and Socket.IO servers.
  colonialwars Server instances created. +26ms
  colonialwars Express middleware and handlers have been mounted. +1ms
  colonialwars Main Socket.IO namespace handlers have been mounted. +0ms
  colonialwars Play Socket.IO namespace handlers have been mounted. +0ms
Colonialwars_server: 2020-11-09T05:15:19.730Z [Server_log] info: Server running on http://localhost:8000.
^CColonialwars_server: 2020-11-09T05:15:30.887Z [Server_log] info: Received signal SIGINT. Shutting down application...
Colonialwars_server: 2020-11-09T05:15:30.888Z [Server_log] info: Server closed successfully. Exiting...
"""
  try:
    parsed_msg = python_http_parser.parse(msg_with_body, {
      "received_from": "client request",
      "body_required": False
    })
  except Exception as e:
    err = e

  assert err is None
  print(parsed_msg)

def test_parser_no_body():
  # Test with message that has no double `\r\n`s.
  err = None
  parsed_msg = None
  client_msg = \
    "GET /index.html HTTP/1.1\r\n" + \
    "Accept-Encoding: gzip, deflate\r\n" + \
    "ACCEPT-LANGUAGE: en-US,en;q=0.9\r\n" + \
    "Cache-Control: no-cache\r\n" + \
    "cONNECTION: keep-alive\r\n" + \
    "Pragma: no-cache\r\n" + \
    "Upgrade-Insecure-Requests: 1\r\n" + \
    "User-Agent: CURL/3.0\r\n"
  try:
    parsed_msg = python_http_parser.parse(client_msg, {
      "received_from": "client request",
      "body_required": False
    })
  except Exception as e:
    err = e
  assert err is None
  print(parsed_msg)

def test_parser_normalize_linebreaks():
  # Test the parser, while telling it to normalize linebreaks.
  err = None
  parsed_msg = None
  client_msg = \
    "GET /index.html HTTP/1.1\r" + \
    "Accept-Encoding: gzip, deflate\n" + \
    "ACCEPT-LANGUAGE: en-US,en;q=0.9\r\n" + \
    "Cache-Control: no-cache\n" + \
    "cONNECTION: keep-alive\t\r" + \
    "Pragma: no-cache\r\n" + \
    "Upgrade-Insecure-Requests: 1\n" + \
    "User-Agent: BOTS.ca/v9.9.300\r\r"
  try:
    parsed_msg = python_http_parser.parse(client_msg, {
      "received_from": "client request",
      "body_required": False,
      "normalize_linebreaks": True
    })
  except Exception as e:
    err = e
  assert err is None
  print(parsed_msg)
