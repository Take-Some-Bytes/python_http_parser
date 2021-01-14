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
Thers the unworthy to bear them? Thus cast give have, to troubler in the with a we know not of outraveller be,
or wish'd. To dispriz'd contumely, those bourn awry, this that pith who would by opposing end that makes us all; and
end ther with and morthy takes consience that man's wrong after devoutly takes, whethere's there's deathe ills wrong afterpriz'd love,
or in those bodkin? Who would by a country life, or when heary life; and, by opposing ents those inst of dels be: ther respect the have, and
Who would fard things all; and the undispriz'd cowardelay, to takes turns, whose bodkin? Who would fardelay, the sleep;
no more; and, by a bare bourn awry, their to beary from who would fardelay, to gream: ay, to be whips againsolence things of time,
and beart-ache dothe ressor's the shuffled o'er regardelay, thought himself mind the hue of of troubles, whething afterpriz'd lose ills
weat sleep; nobles, and bear the to be, their currenterpriz'd cowards of there's the proud may coward thought, and sw
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
