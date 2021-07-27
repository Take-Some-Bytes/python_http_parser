"""
Context file so that the tests could import our package.
"""

# pylint: disable=W0611,C0413

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import python_http_parser
import python_http_parser.body
import python_http_parser.constants
import python_http_parser.errors
import python_http_parser.stream
