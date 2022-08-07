"""
Benchmark the stream parser when parsing requests.
"""

from .context import python_http_parser
from .data import REQUEST

def run_parser_req(parser: python_http_parser.stream.HTTPParser, data: bytes):
    parser.reset()
    return parser.process(data)

def bench_req_short(benchmark):
    parser = python_http_parser.stream.HTTPParser()
    ret = benchmark.pedantic(
        run_parser_req,
        args=(parser, REQUEST['short']),
        iterations=10000,
        rounds=10,
        warmup_rounds=1
    )

    assert ret == len(REQUEST['short'])

def bench_req_regular(benchmark):
    parser = python_http_parser.stream.HTTPParser()
    ret = benchmark.pedantic(
        run_parser_req,
        args=(parser, REQUEST['regular']),
        iterations=10000,
        rounds=10,
        warmup_rounds=1
    )

    assert ret == len(REQUEST['regular'])

def bench_req_long(benchmark):
    parser = python_http_parser.stream.HTTPParser()
    ret = benchmark.pedantic(
        run_parser_req,
        args=(parser, REQUEST['long']),
        iterations=10000,
        rounds=10,
        warmup_rounds=1
    )

    assert ret == len(REQUEST['long'])
