"""
``utils`` module with utility parsing functions.
"""

from typing import Dict, List, Literal, TypedDict, Union


class ParseHeaderLine(TypedDict):
    name: str
    value: str
    raw: List[str]


def parse_http_version(string: str) -> float: ...
def parse_http_status(string: str) -> int: ...


def get_newline_type(msg: str) -> str: ...


def get_headers(
    head: str, newline_type: Literal[r'\r\n', r'\n'], strictness: int
) -> List[Union[List[str], Dict[str, Union[str, List[str]]]]]: ...


def parse_status_line(string: str) -> List[str]: ...
def parse_request_line(string: str) -> List[str]: ...
def parse_header_line(hdr_line: str) -> ParseHeaderLine: ...
