"""
Benchmark the stream parser when parsing responses.
"""

from .context import python_http_parser
from .data import RESPONSE

def run_parser_res(parser: python_http_parser.stream.HTTPParser, data: bytes):
    parser.reset()
    return parser.process(data)

def bench_res_short(benchmark):
    parser = python_http_parser.stream.HTTPParser(is_response=True)
    ret = benchmark.pedantic(
        run_parser_res,
        args=(parser, RESPONSE['short']),
        iterations=10000,
        rounds=10,
        warmup_rounds=1
    )

    assert ret == len(RESPONSE['short'])

def bench_res_regular(benchmark):
    parser = python_http_parser.stream.HTTPParser(is_response=True)
    ret = benchmark.pedantic(
        run_parser_res,
        args=(parser, RESPONSE['regular']),
        iterations=10000,
        rounds=10,
        warmup_rounds=1
    )

    assert ret == len(RESPONSE['regular'])

def bench_res_long(benchmark):
    parser = python_http_parser.stream.HTTPParser(is_response=True)
    ret = benchmark.pedantic(
        run_parser_res,
        args=(parser, RESPONSE['long']),
        iterations=10000,
        rounds=10,
        warmup_rounds=1
    )

    assert ret == len(RESPONSE['long'])
