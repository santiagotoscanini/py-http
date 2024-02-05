# Python HTTP Server

Basic implementation of HTTP server in Python from scratch.

I still have to implement radix tree for routing, right now it's hardcoded.

### Examples

Example of the server usage:
```python3
http_handler = HTTPHandler(ADDRESS, PORT)

# Register handlers
http_handler.get("/user-agent", handle_user_agent)
http_handler.post("/files", handle_post_file)

# Register default handler
http_handler.default(handle_not_found)

# Start the server
http_handler.listen()
```

Example of a handler that returns the User-Agent header from the request in the body of the response:
```python3
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
```

### Testing

You can start the server (with the `--directory` flag) and test it with curl:
```bash
curl -i -X GET http://localhost:4221/files/.gitignore
curl -v -X POST http://localhost:4221/files/vanilla_monkey_vanilla_monkey -d 'humpty monkey yikes monkey Coo Monkey humpty monkey'
```