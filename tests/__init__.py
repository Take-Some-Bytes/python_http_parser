"""Common stuff for tests."""

def chunk(stuff, chunk_size):
    """Chunk some stuff."""
    i = 0
    cap = len(stuff)

    while (i+chunk_size) < cap:
        yield stuff[i:i+chunk_size]
        i += chunk_size

    if i < cap:
        yield stuff[i:]

def parser_process_chunks(parser, chunks):
    """Helper function to parse a bunch of chunks using the specified parser."""
    buf = bytearray(256)
    view = memoryview(buf)
    buf_len = 0
    for chk in chunks:
        view[buf_len:buf_len+len(chk)] = chk
        buf_len += len(chk)

        ret = parser.process(bytes(view[:buf_len]))
        if ret >= 0:
            view[:len(view)-ret] = view[ret:]
            buf_len -= ret
        if ret < 0:
            break

def attach_common_event_handlers(
    parser, result, errors, is_response
):
    """Attach common event handlers to a HTTPParser.

    The ``result`` parameter must be ``dict`` that contains the
    results of parsing.

    The ``errors`` parameter must be a ``list`` of exceptions that happened.
    """
    def on_error(ex):
        errors.append(ex)
    def on_method(method):
        result['req_method'] = method
    def on_uri(uri):
        result['req_uri'] = uri
    def on_version(ver):
        result['http_version'] = ver
    def on_reason(msg):
        result['reason'] = msg
    def on_status_code(code):
        result['status_code'] = code
    def on_header_name(field):
        result['raw_headers'].append(field)
    def on_header_value(value):
        result['raw_headers'].append(value)
    def on_data(chk):
        result['body'].append(chk)

    parser.on('header_name', on_header_name)
    parser.on('header_value', on_header_value)
    parser.on('data', on_data)
    parser.on('error', on_error)
    if is_response:
        # It's a response.
        parser.on('reason', on_reason)
        parser.on('status_code', on_status_code)
        parser.on('version', on_version)
    else:
        parser.on('req_method', on_method)
        parser.on('req_uri', on_uri)
        parser.on('version', on_version)
