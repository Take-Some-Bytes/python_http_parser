"""
``python_http_parser`` module.
"""
__all__ = [
    'decode',
    'parse'
]

from typing import Dict, List, Optional, Union
# For compatiblity with Python<3.8
from typing_extensions import TypedDict

import python_http_parser.constants as constants

class ParsedHTTPMessage(TypedDict):
    status_code: Optional[int]
    status_msg: Optional[str]
    req_method: Optional[str]
    req_uri: Optional[str]
    http_ver: float
    headers: Dict[str, Union[str, list]]
    raw_headers: List[str]
    body: Optional[str]


def parse(
    msg: Union[bytes, bytearray, str],
    strictness_level: int = constants.PARSER_NORMAL,
    is_response: bool = False
) -> ParsedHTTPMessage: ...


decode = parse
