import http.server
import io

__author__ = 'jwilner'


REQUEST_LINE_TEMPLATE = "{method} {request_uri} {http_version}"
HEADER_LINE = "{field_name}: {field_value}"


def get_request(method, request_uri, http_version, host, headers=None):
    """
    :type method: str
    :type request_uri: str
    :type http_version: str
    :type headers: dict[str, str]
    :rtype: HTTPRequest
    """
    if headers is None:
        headers = {}

    headers['host'] = host

    request_line = REQUEST_LINE_TEMPLATE.format(method=method,
                                                request_uri=request_uri,
                                                http_version=http_version)

    header_lines = "\n".join(HEADER_LINE.format(field_name=k, field_value=v)
                             for k, v in headers.items())

    # must end in blank line
    return HTTPRequest("\n".join((request_line, header_lines, "")))


class HTTPRequest(http.server.BaseHTTPRequestHandler):
    """
    Inspired by http://stackoverflow.com/a/5955949/1567452
    """
    def __init__(self, request_text):
        """
        :type request_text: str
        """
        self.rfile = io.BytesIO(request_text.encode("utf-8"))
        self.raw_requestline = self.rfile.readline()
        self.parse_request()

    def send_error(self, code, message=None):
        """
        :type code: int
        :type message: str
        """
        raise ValueError("Invalid message: "
                         "parsing yielded {} {}".format(code,  message))
