"""Basic tests."""

from .context import python_http_parser

def test_parser_proper():
  # Test with valid client message.
  err = None
  parsed_msg = None
  client_msg = \
    "GET /index.html HTTP/1.1\r\n" + \
    "User-Agent: Bot/v100.0.96\r\n" + \
    "USER-AGENT: APOIJDSPIOFJKSAPODISJAPDOIJSADPIOJSAPO/111.ca\r\n" + \
    "accept: text/html,application/xhtml+xml,application/xml;q=0.9\r\n" + \
    "accept-encoding: gzip, deflate, br\r\n" + \
    "accept-language: en-US,en;q=0.9\r\n" + \
    "cache-control: no-cache\r\n" + \
    "pragma: no-cache\r\n" + \
    "sec-fetch-dest: document\r\n" + \
    "sec-fetch-mode: navigate\r\n" + \
    "sec-fetch-site: none\r\n" + \
    "sec-fetch-user: ?1\r\n" + \
    "upgrade-insecure-requests: 1\r\n" + \
    "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36\r\n\r\n"

  try:
    parsed_msg = python_http_parser.parse(client_msg, { "received_from": "client request" })
  except Exception as e:
    err = e
  assert err is None
  print(parsed_msg)

def test_parser_invalid():
  # Test with invalid client message.
  err = None
  parsed_msg = None
  bad_client_msg = \
    b"SPDOIFJDPa/asd;okjf/HTPP dsafk sadfffdsf HTTP/0.1\r\n"  + \
    b"sdaoipjpoidasfpoi:\r" + \
    b"dasfopidajspoi\n" + \
    b"dasofjdsp:iaf\n\r" + \
    b"dsafdasjfomd fsda\r\r\r" + \
    b"fasdkf: esafopisd\r\n\r" + \
    b"sdapofjpio asfasd dasfoihudaf\r\n\n"
  try:
    parsed_msg = python_http_parser.parse(bad_client_msg, { "received_from": "client request" })
  except Exception as e:
    err = e
  assert isinstance(err, Exception)
  print(parsed_msg)
