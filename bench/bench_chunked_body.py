"""
Benchmarks for the ChunkedProcessor, which processes chunked bodies.
"""

from .context import python_http_parser
from .data import CHUNKED

def run_processor(data: bytes):
    return python_http_parser \
        .body \
        .ChunkedProcessor() \
        .process(data, True)


def bench_chunked_short(benchmark):
    ret = benchmark.pedantic(
        run_processor,
        args=(CHUNKED['short'],),
        iterations=10000,
        rounds=10,
        warmup_rounds=1
    )

    assert ret == len(CHUNKED['short'])


def bench_chunked_regular(benchmark):
    ret = benchmark.pedantic(
        run_processor,
        args=(CHUNKED['regular'],),
        iterations=10000,
        rounds=10,
        warmup_rounds=1
    )

    assert ret == len(CHUNKED['regular'])


def bench_chunked_long(benchmark):
    ret = benchmark.pedantic(
        run_processor,
        args=(CHUNKED['long'],),
        iterations=10000,
        rounds=10,
        warmup_rounds=1
    )

    assert ret == len(CHUNKED['long'])
