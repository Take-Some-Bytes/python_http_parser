"""
Test this package's body processors, namely ``FixedLenProcessor``, for use
when ``Content-Length`` is encountered, and ``ChunkedProcessor``, for use
when ``Transfer-Encoding: chunked`` is encountered.
"""

from . import chunk, parser_process_chunks
from .context import python_http_parser

FixedLenProcessor = python_http_parser.body.FixedLenProcessor
ChunkedProcessor = python_http_parser.body.ChunkedProcessor


class mock_processor:
    """Mock class to make body processor to work like the HTTPParser class."""
    # pylint: disable=too-few-public-methods,invalid-name

    def __init__(self, processor):
        """Mock class to make body processor to work like the HTTPParser class."""
        self.processor = processor

    def process(self, chk):
        """Process the next chunk."""
        return self.processor.process(chk, True)


def test_fixed_body():
    """Make sure the FixedLenProcessor works."""
    body = b"""
Nope, NOpe, NOpity nope. (nope nope)
Why not?\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<- That's 16 tabs.
"""
    body_len = len(body)
    results = [
        {
            'chunks': [],
            'finished': False,
            'body': None
        },
        {
            'chunks': [],
            'finished': False,
            'body': None
        }
    ]
    errors = []

    def on_error(err):
        errors.append(err)

    def create_on_data(result_id):
        """Create a data listener."""
        def on_data(chk):
            results[result_id]['chunks'].append(chk)
        return on_data

    def create_on_finished(result_id):
        """Create a finished listener."""
        def on_finished():
            results[result_id]['finished'] = True
        return on_finished

    # First, let's try all at once.
    processor = FixedLenProcessor(body_len)
    processor.on_data(create_on_data(0))
    processor.on_finished(create_on_finished(0))
    processor.on_error(on_error)
    processor.process(body, True)

    results[0]['body'] = b''.join(results[0]['chunks'])

    assert len(errors) == 0
    assert results[0]['body'] == body
    assert results[0]['finished']

    # Now, see what happens when we chunk it.
    processor = FixedLenProcessor(body_len)
    processor.on_data(create_on_data(1))
    processor.on_finished(create_on_finished(1))
    processor.on_error(on_error)
    parser_process_chunks(mock_processor(processor), chunk(body, 5))

    results[1]['body'] = b''.join(results[1]['chunks'])

    assert len(errors) == 0
    assert results[1]['body'] == body
    assert results[1]['finished']


def test_chunked_body():
    """Make sure the ChunkedProcessor works."""
    results = [
        {
            'chunks': [],
            'finished': False,
            'body': None
        },
        {
            'chunks': [],
            'finished': False,
            'body': None
        }
    ]
    body = b"""\
b
\nNope, NOpe
8
, NOpity
8
 nope. (
d
nope nope)\nWh
29
y not?\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<- That's 16 tabs.\n
0

"""
    actual_body = b"""
Nope, NOpe, NOpity nope. (nope nope)
Why not?\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<- That's 16 tabs.
"""
    errors = []

    def on_error(err):
        errors.append(err)
    def create_on_data(result_id):
        """Create a data listener."""
        def on_data(chk):
            results[result_id]['chunks'].append(chk)
        return on_data
    def create_on_finished(result_id):
        """Create a finished listener."""
        def on_finished():
            results[result_id]['finished'] = True
        return on_finished

    # First, let's try all at once.
    processor = ChunkedProcessor()
    processor.on_data(create_on_data(0))
    processor.on_finished(create_on_finished(0))
    processor.on_error(on_error)
    processor.process(body, True)

    results[0]['body'] = b''.join(results[0]['chunks'])

    assert len(errors) == 0
    assert len(results[0]['chunks']) > 0
    assert results[0]['body'] == actual_body
    assert results[0]['finished']

    # Now, see what happens when we chunk it.
    processor = ChunkedProcessor()
    processor.on_data(create_on_data(1))
    processor.on_finished(create_on_finished(1))
    processor.on_error(on_error)
    parser_process_chunks(mock_processor(processor), chunk(body, 6))

    results[1]['body'] = b''.join(results[1]['chunks'])

    assert len(errors) == 0
    assert len(results[1]['chunks']) > 0
    assert results[1]['body'] == actual_body
    assert results[1]['finished']


def test_chunked_body_with_exts():
    """Make sure the ChunkedProcessor works with chunk extensions."""
    results = [
        {
            'chunks': [],
            'finished': False,
            'body': None
        },
        {
            'chunks': [],
            'finished': False,
            'body': None
        }
    ]
    body = b"""\
b;this_be_extension=1
\nNope, NOpe
8;fff=ddd;ccc=bbb;aaa=thisBeChunkExtension
, NOpity
8
 nope. (
d;nope=nope
nope nope)\nWh
29
y not?\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<- That's 16 tabs.\n
0;lastchunk=1

"""
    actual_body = b"""
Nope, NOpe, NOpity nope. (nope nope)
Why not?\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<- That's 16 tabs.
"""
    errors = []

    def on_error(err):
        errors.append(err)
    def create_on_data(result_id):
        """Create a data listener."""
        def on_data(chk):
            results[result_id]['chunks'].append(chk)
        return on_data
    def create_on_finished(result_id):
        """Create a finished listener."""
        def on_finished():
            results[result_id]['finished'] = True
        return on_finished

    # First, let's try all at once.
    processor = ChunkedProcessor()
    processor.on_data(create_on_data(0))
    processor.on_finished(create_on_finished(0))
    processor.on_error(on_error)
    processor.process(body, True)

    results[0]['body'] = b''.join(results[0]['chunks'])

    assert len(errors) == 0
    assert len(results[0]['chunks']) > 0
    assert len(processor.extensions) > 0
    assert results[0]['body'] == actual_body
    assert results[0]['finished']

    # Now, see what happens when we chunk it.
    processor = ChunkedProcessor()
    processor.on_data(create_on_data(1))
    processor.on_finished(create_on_finished(1))
    processor.on_error(on_error)
    parser_process_chunks(mock_processor(processor), chunk(body, 6))

    results[1]['body'] = b''.join(results[1]['chunks'])

    assert len(errors) == 0
    assert len(results[1]['chunks']) > 0
    assert len(processor.extensions) > 0
    assert results[1]['body'] == actual_body
    assert results[1]['finished']

def test_fixed_body_negative_len():
    """Make sure the FixedLenProcessor fails if ``body_len`` is negative."""
    body = b"""
Nope, NOpe, NOpity nope. (nope nope)
Why not?\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t<- That's 16 tabs.
"""
    body_len = -len(body)
    errors = []
    result = {
        'chunks': [],
        'finished': False,
        'body': None
    }
    processor = FixedLenProcessor(body_len)
    def on_error(ex):
        errors.append(ex)
    def on_data(chk):
        result['chunks'].append(chk)
    def on_finished():
        result['finished'] = True

    processor.on_data(on_data)
    processor.on_error(on_error)
    processor.on_finished(on_finished)
    processor.process(body)

    assert len(errors) == 1
    assert isinstance(errors[0], ValueError)
    assert len(result['chunks']) == 0
    assert result['body'] is None
    assert not result['finished']

def test_chunked_body_invalid_chunk_size():
    """Make sure the ChunkedProcessor fails if a chunk size is invalid."""
    body = b"""\
asfd
WJAJDOOC>D#MV)OC_W#J LDSfo
"""
    errors = []
    result = {
        'chunks': [],
        'finished': False,
        'body': None
    }
    processor = ChunkedProcessor()
    def on_error(ex):
        errors.append(ex)
    def on_data(chk):
        result['chunks'].append(chk)
    def on_finished():
        result['finished'] = True

    processor.on_data(on_data)
    processor.on_error(on_error)
    processor.on_finished(on_finished)
    processor.process(body, True)

    assert len(errors) == 1
    assert isinstance(errors[0], python_http_parser.errors.InvalidChunkSize)
    assert len(result['chunks']) == 0
    assert result['body'] is None
    assert not result['finished']

def test_chunked_body_chunk_too_large():
    """Make sure the ChunkedProcessor fails if a chunk is too large.."""
    body = b"""\
ffffffffffffffffff
The above hexadecimal number is equal to 4722366482869645213695,
or 4194304PiB (Pebibytes)
"""
    errors = []
    result = {
        'chunks': [],
        'finished': False,
        'body': None
    }
    processor = ChunkedProcessor()
    def on_error(ex):
        errors.append(ex)
    def on_data(chk):
        result['chunks'].append(chk)
    def on_finished():
        result['finished'] = True

    processor.on_data(on_data)
    processor.on_error(on_error)
    processor.on_finished(on_finished)
    processor.process(body, True)

    assert len(errors) == 1
    assert isinstance(errors[0], python_http_parser.errors.InvalidChunkSize)
    assert len(result['chunks']) == 0
    assert result['body'] is None
    assert not result['finished']
