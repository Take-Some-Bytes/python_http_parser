"""
python_http_parser module.
"""
# Imports
import typing

str_or_bytes = typing.TypeVar("str_or_bytes", str, bytes)
str_or_bool = typing.TypeVar("str_or_bool", str, bool)

parse_could_return = typing.TypeVar(
  "parse_could_return", str, list, dict
)

def parse(msg: str_or_bytes, opts: typing.Mapping[str, str_or_bool]) -> typing.Dict[str, parse_could_return]: ...
