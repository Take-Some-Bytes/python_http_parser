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
        print(f'Parsing request num {req_num} with HTTPParser 100_000 times.')
        bench_req_result = bench(f'bench_req_parsing({req_num})')
        print(f'Parsing total time: {bench_req_result[0]}s')
        print(f'Parsing avg time: {bench_req_result[1]}s')

    if res:
        print(f'Parsing response num {res_num} with HTTPParser 100_000 times')
        bench_res_result = bench(f'bench_res_parsing({res_num})')
        print(f'Parsing total time: {bench_res_result[0]}s')
        print(f'Parsing avg time: {bench_res_result[1]}s')
