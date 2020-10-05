"""Basic tests."""

from .context import python_http_parser

def test_parser_static():
  # Test parser parsing client message.
  client_msg = \
    """\
    GET /index.html HTTP/1.1
    User-Agent: Bot/v100.0.96
    USER-AGENT: APOIJDSPIOFJKSAPODISJAPDOIJSADPIOJSAPO/111.ca
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

    """
  bad_client_msg = \
    b"""\
      SPDOIFJDPa/asd;okjf/HTPP dsafk sadfffdsf HTTP/0.1
      sdaoipjpoidasfpoi:
      dasfopidajspoi
      dasofjdsp:iaf
      dsafdasjfomd fsda
      fasdkf: esafopisd

      sdapofjpio asfasd dasfoihudaf 

    """
  err1 = None
  err2 = None
  try:
    print(python_http_parser.parse(client_msg, { "received_from": "client request" }))
  except Exception as e:
    err1 = e
  try:
    print(python_http_parser.parse(bad_client_msg, { "received_from": "client request" }))
  except Exception as e:
    err2 = e

  assert (err1 is None) and isinstance(err2, Exception)

test_parser_static()
