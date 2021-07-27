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
    msg = 'Profiling HTTPParser class while parsing {} number {}'.format(
        'request' if req else 'response',
        req_num if req else res_num
    )
    print(msg)

    if req:
        cProfile.runctx(
            'for _ in range(100_000): run_http_parser_req(reqs[{}])'
                .format(req_num),
            globals(), {}
        )
    if res:
        cProfile.runctx(
            'for _ in range(100_000): run_http_parser_res(reses[{}])'
                .format(res_num),
            globals(), {}
        )
