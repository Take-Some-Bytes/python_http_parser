"""
Common(and private) variables and functions that will be used in this package.
"""

linebreak_map = {
  "CRLF": "\r\n",
  "LF": "\n",
  "CR": "\r"
}

def normalize_linebreaks(string):
  r"""Normalizes linebreaks into uniform \r\n."""
  return "".join((line + "\r\n") for line in string.splitlines())
def trim_and_lower(string):
  """Trims and lowers a string."""
  return string.strip().lower()

class ParsingError(Exception):
  """ParsingError class."""
  pass
