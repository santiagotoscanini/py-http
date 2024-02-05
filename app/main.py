import sys
from http import HTTPStatus

from app.http_handler import HTTPHandler, handler

ADDRESS = "localhost"
PORT = 4221


@handler
def handle_root(_):
    return {
        "status": HTTPStatus.OK,
    }


@handler
def handle_echo(request):
    body = request["path"].replace('/echo/', '')

    headers = {
        "Content-Type": "text/plain",
        "Content-Length": len(body)
    }

    return {
        "status": HTTPStatus.OK,
        "headers": headers,
        "body": body
    }


@handler
def handle_user_agent(request):
    body = request["headers"]['User-Agent']

    headers = {
        "Content-Type": "text/plain",
        "Content-Length": len(body)
    }

    return {
        "status": HTTPStatus.OK,
        "headers": headers,
        "body": body
    }


@handler
def handle_get_file(request):
    directory = sys.argv[2]
    file_name = request["path"].replace('/files', '')
    file_path = f"{directory}{file_name}"
    try:
        with open(file_path, "r") as file:
            status = HTTPStatus.OK
            body = file.read()
            headers = {
                "Content-Type": "application/octet-stream",
                "Content-Length": len(body)
            }
            response = {
                "status": status,
                "headers": headers,
                "body": body
            }
    except FileNotFoundError:
        status = HTTPStatus.NOT_FOUND
        response = {
            "status": status,
        }

    return response


@handler
def handle_post_file(request):
    directory = sys.argv[2]
    file_name = request["path"].replace('/files', '')
    file_path = f"{directory}{file_name}"

    with open(file_path, "w") as file:
        file.write(request["body"])

    return {
        "status": HTTPStatus.CREATED,
    }


@handler
def handle_not_found(_):
    return {
        "status": HTTPStatus.NOT_FOUND,
    }


def main():
    http_handler = HTTPHandler(ADDRESS, PORT)

    # test returning a simple response
    http_handler.get("/", handle_root)

    # test handling a not found route
    http_handler.default(handle_not_found)

    # test extracting information from path
    http_handler.get("/echo", handle_echo)

    # test extracting information from headers
    http_handler.get("/user-agent", handle_user_agent)

    # test returning a file
    http_handler.get("/files", handle_get_file)

    # test posting a file
    http_handler.post("/files", handle_post_file)

    http_handler.listen()


if __name__ == "__main__":
    main()
