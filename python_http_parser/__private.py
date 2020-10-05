"""
Common variables and functions that will be used regardless
of the python version.
"""

# Some variables we need.
line_break_map = {
  "CRLF": "\r\n",
  "LF": "\n",
  "CR": "\r"
}

# Some functions we need.
def normalize_linebreaks(string):
  r"""Normalizes linebreaks into uniform \r\n."""
  return "".join((line + "\r\n") for line in string.splitlines())
def trim_and_lower(string):
  """Trims and lowers a string."""
  return string.strip().lower()

# Some classes we need.
class ParsingError(Exception):
  """ParsingError class."""
  pass
