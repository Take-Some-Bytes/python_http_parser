"""
``utils`` module with utility parsing functions.
"""

from typing import List, NamedTuple, Union
# Compatibility reasons.
from typing_extensions import Literal, TypedDict

class ParsedHeaderLine(TypedDict):
    name: str
    value: str
    raw: List[str]


class SplitMessage(NamedTuple):
    head: str
    body: str


class RequestLine(NamedTuple):
    method: str
    uri: str
    version: float


class StatusLine(NamedTuple):
    version: float
    code: int
    msg: str


class ConsumedData(NamedTuple):
    data: str
    leftovers: str


class ParsedHeaders(NamedTuple):
    raw_headers: list[str]
    headers: dict[str, Union[str, list]]


def get_headers(
    head: str, newline_type: Literal[r'\r\n', r'\n'], strictness: int
) -> ParsedHeaders: ...


def get_start_line(
    msg: str, newline_type: Literal[r'\r\n', r'\n']
) -> ConsumedData: ...


def split_msg(
    msg: str, newline_type: Literal[r'\r\n', r'\n']
) -> SplitMessage: ...


def get_newline_type(msg: str) -> str: ...
def parse_status_line(string: str) -> StatusLine: ...
def parse_request_line(string: str) -> RequestLine: ...
def parse_header_line(hdr_line: str) -> ParsedHeaderLine: ...
