import argparse
import copy
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from .partner import operate
from .wire import reply


def make_server(address, data):
    release = copy.deepcopy(data)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            parsed = urlsplit(self.path)
            if parsed.path == '/v1/catalog':
                return reply(self, 200, {key: value for key, value in release.items() if key != 'tables'} | {'tables': list(release['tables'])})
            if not parsed.path.startswith('/v1/tables/'):
                return reply(self, 404, {'error': '接口不存在'})
            query = parse_qs(parsed.query)
            if query.get('revision', [''])[0] != release['revision']:
                return reply(self, 409, {'error': '资料版本不一致'})
            name = parsed.path.rsplit('/', 1)[-1]
            if name not in release['tables']:
                return reply(self, 404, {'error': '资料表不存在'})
            try:
                offset = int(query.get('offset', ['0'])[0])
                limit = int(query.get('limit', ['31'])[0])
                if offset < 0 or not 1 <= limit <= 100:
                    raise ValueError('分页参数超界')
            except ValueError:
                return reply(self, 400, {'error': '分页参数无效'})
            rows = release['tables'][name]
            end = min(len(rows), offset+limit)
            return reply(self, 200, {'revision': release['revision'], 'rows': rows[offset:end], 'next': end if end < len(rows) else None})

        def do_POST(self):
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 1000000:
                    raise ValueError('请求大小无效')
                payload = json.loads(self.rfile.read(length))
                if payload.get('revision') != release['revision']:
                    return reply(self, 409, {'error': '资料版本不一致'})
                result = operate(self.path, payload, release)
                return reply(self, 200, result)
            except LookupError as error:
                return reply(self, 404, {'error': str(error)})
            except (ValueError, KeyError, TypeError) as error:
                return reply(self, 422, {'error': str(error)})

    return ThreadingHTTPServer(address, Handler)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8091)
    parser.add_argument('--data', type=Path, default=Path('data/release.json'))
    args = parser.parse_args()
    make_server(('0.0.0.0', args.port), json.loads(args.data.read_text())).serve_forever()


if __name__ == '__main__':
    main()
