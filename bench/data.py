"""
Data to benchmark with
"""

REQUEST = {
    'short': b''.join([
        b'GET / HTTP/1.1\r\n',
        b'Host: short.example.com\r\n',
        b'Accept: text/html,text/plain,*/*\r\n'
    ]),
    'regular': b''.join([
        b'GET /index.html HTTP/1.1\r\n',
        b'Host: example.org:8080\r\n',
        b'Accept: text/html,application/xhtml+xml,application/xml;q=0.9\r\n',
        b'Accept-Encoding: gzip, br\r\n',
        b'Connection: keep-alive\r\n',
        b'User-Agent: Jeremy-Blunts-Agent/1.13.2\r\n\r\n'
    ]),
    'long': b''.join([
        b'GET /app.php?user=Bob&auth=headers HTTP/1.1\r\n',
        b'Host: shop.example.com:443\r\n',
        b'Accept: text/html,application/xhtml+xml,application/xml;q=0.9\r\n',
        b'Accept-Encoding: gzip, br\r\n',
        b'Accept-Language: en\r\n',
        b'Accept-Charset: utf-8\r\n',
        b'Connection: keep-alive\r\n',
        b'Keep-Alive: 8\r\n',
        # Clearly not an auth token.
        b'Cookie: auth-token=f0a99e0938c8d90af0s9d8ff4817209da8d9s39487daf294e\r\n',
        b'User-Agent: McDonalds New HTTP Client/0.9-alpha2\r\n\r\n'
    ])
}

RESPONSE = {
    'short': b''.join([
        b'HTTP/1.1 200 OK\r\n',
        b'Date: Wed, 30 Jun 2021 01:16:36 GMT\r\n',
        b'Server: Not Python\r\n\r\n'
    ]),
    'regular':b''.join([
        b'HTTP/1.1 200 OK\r\n',
        b'Date: Tue 29 Jun 2021 18:13:06 GMT\r\n',
        b'Transfer-Encoding: chunked,gzip\r\n',
        b'Cache-Control: max-age=9000\r\n',
        b"Content-Security-Policy: default-src 'self'\r\n",
        b'X-XSS-Protection: 1\r\n\r\n'
    ]),
    'long': b''.join([
        b'HTTP/1.1 404 Not Found\r\n',
        # Not a real date.
        b'Date: Thu 12 Jul 2023 01:32:11 GMT\r\n',
        b'ETag: dfdfjdifjdijfdijfdifjdifjdfjdifjdifjdifj\r\n',
        b'Referrer-Policy: no-referrer\r\n',
        b"Content-Security-Policy: default-src 'self'\r\n",
        b'Report-To: {"group":"endpoint","max_age":900,"endpoints":[{"url":"https://no.com/no"}]}\r\n',
        b'Server: HTTPParser/1.1\r\n',
        b'Cache-Control: must-revalidate\r\n',
        b'Set-Cookie: sess=no\r\n',
        b'Strict-Transport-Security: max-age=300000\r\n\r\n'
    ])
}
