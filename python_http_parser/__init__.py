"""
``python_http_parser`` module.
"""

# List the public API of this package.
__all__ = [
  "decode",
  "parse"
]
# The version...
__version__ = "0.2.1"

# Imports.
from python_http_parser.__private import (
  linebreak_map,
  normalize_linebreaks,
  trim_and_lower,
  ParsingError
)


def parse(msg, opts):
  """
    Parses a HTTP message.

    The `msg` parameter should be the actual HTTP message, either a
    `str` or some `bytes`.
    The `opts` parameter should be a `dict`, with the following form:
    ```
    {
      "received_from": "client request" or "server response",
      "body_required": bool,
      "normalize_linebreaks": bool
    }
    ```

    This function returns a `dict`, with the following format:
    ```
    {
      "version": str,
      "method": str,
      "uri": str,
      "headers": dict,
      "raw_headers": list,
      "body": str or None
    } or {
      "version": str,
      "status_code": str,
      "status_message": str,
      "headers": dict,
      "raw_headers": list,
      "body": str or None
    }
    ```
  """
  # Decode the message, if needed. Also determine options.
  msg = msg.decode("utf-8") if type(msg) is bytes else msg
  received_from = opts["received_from"] if "received_from" in opts else None
  body_required = opts["body_required"] if "body_required" in opts else True
  convert_to_CRLF = opts["normalize_linebreaks"] if "normalize_linbreaks" in opts else False
  if received_from is None:
    raise TypeError("`received_from` property of the `opts` object is required!")
  # Determine the type of linebreaks that we need to use.
  # Also store the split message, just in case.
  linebreak_type = None
  split_message = None
  tmp_split_msg = None
  # If we are to normalize linebreaks, do it NOW.
  if convert_to_CRLF:
    msg = normalize_linebreaks(msg)
  for string in linebreak_map.values():
    split_message = msg.split(string + string)
    if len(split_message) == 2:
      linebreak_type = string
      break
    else:
      split_message = None

  if (type(split_message) is not list) and (body_required is True):
    raise ParsingError("Failed to split message into body and headers!")
  elif (type(split_message) is not list) and (body_required is False):
    for string in linebreak_map.values():
      tmp_split_msg = msg.split(string)
      if len(tmp_split_msg) > 0:
        linebreak_type = string
        break
    split_message = [msg, None]

  # Now, actually parse the message.
  try:
    # Body is optional.
    head, body = split_message
  except ValueError:
    raise ParsingError(
      "Failed to separate message into headers and body!"
    )

  head = head.split(linebreak_type)
  headline = head[0].strip()
  if not headline:
    raise ParsingError("Failed to get HTTP message headline!")
  # Get headers. We do this because there could be duplicate headers, and even
  # those are important.
  headers = {}
  raw_headers = []
  for hdr in head[1:]:
    # TODO: Check if the following line is sufficient for splitting valid headers.
    split_header = hdr.split(":", 1)
    if len(split_header) != 2:
      # Malformed header, move on.
      continue
    split_header[0] = trim_and_lower(split_header[0])
    split_header[1] = split_header[1].strip()
    # For raw headers, we need to put the headers in the same way
    # we received them. Duplicates are not merged.
    raw_headers.append(split_header[0])
    raw_headers.append(split_header[1])
    if split_header[0].lower() in headers:
      # Header key already exists, append to that one.
      header_val = headers[split_header[0]]
      if type(header_val) is list:
        headers[split_header[0].lower()].append(split_header[1])
      else:
        old_val = header_val
        headers[split_header[0].lower()] = [old_val, split_header[1]]
    else:
      headers[split_header[0].lower()] = split_header[1]

  split_headline = headline.split(" ")
  if received_from == "client request":
    try:
      req_method, req_uri, req_version = split_headline
    except ValueError:
      raise ParsingError(
        "Failed to parse request headline!"
      )

    return {
      "version": req_version,
      "method": req_method,
      "uri": req_uri,
      "headers": headers,
      "raw_headers": raw_headers,
      "body": body
    }
  elif received_from == "server response":
    try:
      req_version, req_status, req_message = split_headline
    except ValueError:
      raise ParsingError("Failed to parse response headline!")

    return {
      "version": req_version,
      "status_code": req_status,
      "status_message": req_message,
      "headers": headers,
      "raw_headers": raw_headers,
      "body": body
    }

# Aliases for the above functions.
decode = parse
