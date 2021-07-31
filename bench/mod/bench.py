"""
Benchmarks!
"""

import timeit
from typing import Tuple

from . import (REQ, REQ_LONG, REQ_SHORT, RES, RES_LONG, RES_SHORT,
               run_http_parser_req, run_http_parser_res)

reqs = [REQ, REQ_LONG, REQ_SHORT]
reses = [RES, RES_LONG, RES_SHORT]


def bench(fn_name: str) -> Tuple[float, float]:
    """Benchmark the supplied function."""
    result = timeit.timeit(
        fn_name, globals=globals(), number=100_000
    )
    return (result, result / 100_000)


def bench_req_parsing(num: int):
    """Benchmark request parsing."""
    run_http_parser_req(reqs[num])


def bench_res_parsing(num: int):
    """Benchmark request parsing."""
    run_http_parser_res(reses[num])


def run(
    req: bool = True, res: bool = True,
    req_num: int = 0, res_num: int = 0
):
    """Run the benchmarks."""
    if req:
        print('Parsing request num {} with HTTPParser 100_000 times.'.format(req_num))
        bench_req_result = bench('bench_req_parsing({})'.format(req_num))
        print('Parsing total time: {}s'.format(bench_req_result[0]))
        print('Parsing avg time: {}s'.format(bench_req_result[1]))

    if res:
        print('Parsing response num {} with HTTPParser 100_000 times'.format(res_num))
        bench_res_result = bench('bench_res_parsing({})'.format(res_num))
        print('Parsing total time: {}s'.format(bench_res_result[0]))
        print('Parsing avg time: {}s'.format(bench_res_result[1]))
