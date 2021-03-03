"""
``python_http_parser`` module.
"""
# Imports
from typing import (
  Union,
  Dict,
  Mapping
)

def parse(msg: Union[bytes, str], opts: Mapping[str, Union[str, bool]]) -> Dict[str, Union[str, list, dict]]: ...
