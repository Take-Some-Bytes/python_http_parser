"""
Profile the specified API.
"""

import argparse
import cProfile
import sys

from context import python_http_parser
from data import CHUNKED, REQUEST, RESPONSE

HTTPParser = python_http_parser.stream.HTTPParser
ChunkedProcessor = python_http_parser.body.ChunkedProcessor

PARSER_PROCESS = """\
while i < iters:
    parser.reset()
    parser.process(data)
    i += 1
"""

def main() -> int:
    """Program entrypoint."""
    argparser = argparse.ArgumentParser(
        prog='pyhttp-parse-profile',
        description='Profile the python_http_parser APIs'
    )
    argparser.add_argument(
        '-a', '--api',
        action='store', default='stream_parser_req',
        choices=(
            'stream_parser_req',
            'stream_parser_res',
            'chunkedbody'
        ),
        help="""\
    Which API to profile.
    """
    )
    argparser.add_argument(
        '-i', '--iters', '--iterations',
        action='store', type=int, default=100000,
        help="""\
    How many times to call the specified API
    """
    )

    args = argparser.parse_args()

    print(f'[INFO] Profiling API "{args.api}" with {args.iters} consecutive calls')

    if args.api == 'stream_parser_req':
        parser = HTTPParser(is_response=False)

        i = 0
        data = REQUEST['long']
        iters = args.iters

        cProfile.runctx(PARSER_PROCESS, globals(), locals())
    elif args.api == 'stream_parser_res':
        parser = HTTPParser(is_response=True)

        i = 0
        data = RESPONSE['long']
        iters = args.iters

        cProfile.runctx(PARSER_PROCESS, globals(), locals())
    elif args.api == 'chunkedbody':
        i = 0
        data = CHUNKED['long']
        iters = args.iters

        cProfile.run("""\
while i < iters:
    p = ChunkedProcessor()
    p.process(data, True)
    i += 1
""", globals(), locals())

    print('[INFO] Profile finished')
    return 0

if __name__ == '__main__':
    sys.exit(main())
