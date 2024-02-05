import threading
from ftplib import CRLF
from http import HTTPStatus

# This module provides access to the BSD socket interface.
# BSD sockets are the standard API for network programming on POSIX-conformant operating systems.
# BSD stands for Berkeley Software Distribution.
from socket import create_server, AF_INET

HTTP_VERSION = "HTTP/1.1"


def extract_data_from_request(request):
    headers = {}
    header_line = 1
    for line in request[1:]:
        header_line += 1
        if line == '':
            break
        key, value = line.split(": ")
        headers[key] = value

    body = ""
    for line in request[header_line:]:
        body += line
        if line == '':
            break

    return headers, body


def build_status_line(http_status: HTTPStatus):
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages#status_line
    # The first CRLF signifies the end of the status line.
    # The second one signifies the end of the response headers section.
    return f'{HTTP_VERSION} {http_status.value} {http_status.phrase}{CRLF}'


def build_headers(headers_dict):
    headers = ""
    for key, value in headers_dict.items():
        headers += f"{key}: {value}{CRLF}"

    return headers


def build_body(data):
    # before the body we place an extra CRLF to separate the headers from the body
    body = CRLF
    body += f"{data}{CRLF}"

    return body


def build_response(status_line, headers, body):
    body = f"{status_line}{headers}{body}{CRLF}"
    return body.encode()


def handler(http_handler):
    def inner(request):
        response = http_handler(request)

        status_line = build_status_line(response["status"])

        headers = ""
        if "headers" in response:
            headers = build_headers(response["headers"])

        body = ""
        if "body" in response:
            body = build_body(response["body"])

        return build_response(status_line, headers, body)

    return inner


class HTTPHandler:
    def __init__(self, address, port):
        # Utility function to create a TCP socket
        self.socket = create_server(
            (address, port),
            # AF_INET is for IPv4 https://man7.org/linux/man-pages/man2/socket.2.html
            family=AF_INET,
            reuse_port=True
        )
        self.get_routes = {}
        self.post_routes = {}
        self.default_handler = None

    def get(self, route, handler):
        self.get_routes[route] = handler

    def post(self, route, handler):
        self.post_routes[route] = handler

    def default(self, handler):
        self.default_handler = handler

    def handle_connection(self, client_connection):
        # maximum amount of data to be received at once
        request = client_connection.recv(1024).decode().split(CRLF)
        req_status_line = request[0]
        method, path, version = req_status_line.split(" ")

        headers, body = extract_data_from_request(request)
        request_item = {
            "method": method,
            "path": path,
            "headers": headers,
            "body": body
        }

        # TODO: create radix tree for route matching
        if method == "GET":
            if path == "/":
                response = self.get_routes["/"](request_item)
            elif path.startswith("/echo"):
                response = self.get_routes["/echo"](request_item)
            elif path.startswith("/user-agent"):
                response = self.get_routes["/user-agent"](request_item)
            elif path.startswith("/files"):
                response = self.get_routes["/files"](request_item)
            else:
                response = self.default_handler(request_item)
        elif method == "POST":
            if path.startswith("/files"):
                response = self.post_routes["/files"](request_item)
            else:
                response = self.default_handler(request_item)

        client_connection.sendall(response)
        client_connection.close()

    def listen(self):
        while True:
            client_connection, client_address = self.socket.accept()
            client_thread = threading.Thread(target=self.handle_connection, args=(client_connection,))
            client_thread.start()
