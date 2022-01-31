"""
Profile the code.
"""

import cProfile

from . import (REQ, REQ_LONG, REQ_SHORT, RES, RES_LONG, RES_SHORT,
               run_http_parser_req, run_http_parser_res)

reqs = [REQ, REQ_LONG, REQ_SHORT]
reses = [RES, RES_LONG, RES_SHORT]


def run(
    req: bool = True, res: bool = True,
    req_num: int = 0, res_num: int = 0
):
    """Run the profiler."""
    profile_type = 'request' if req else 'response'
    profile_num = req_num if req else res_num
    msg = f'Profiling HTTPParser class while parsing {profile_type} number {profile_num}'
    print(msg)

    if req:
        cProfile.runctx(
            f'for _ in range(100_000): run_http_parser_req(reqs[{req_num}])',
            globals(), {}
        )
    if res:
        cProfile.runctx(
            f'for _ in range(100_000): run_http_parser_res(reses[{res_num}])',
            globals(), {}
        )
