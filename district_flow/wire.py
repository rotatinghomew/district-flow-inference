import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class RemoteFailure(RuntimeError):
    pass


def call(base, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(base.rstrip('/') + path, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urlopen(request, timeout=5) as response:
            return json.load(response)
    except HTTPError as error:
        try:
            detail = error.read().decode()
        finally:
            error.close()
        raise RemoteFailure(f'{error.code}: {detail}') from error


def reply(handler, status, value):
    data = json.dumps(value, ensure_ascii=False, allow_nan=False).encode()
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)
