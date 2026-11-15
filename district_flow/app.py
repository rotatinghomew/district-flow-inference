import argparse
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .client import SourceClient
from .overview import summarize
from .store import ReportStore
from .wire import reply


def make_server(address, source_url, database):
    client = SourceClient(source_url)
    store = ReportStore(database)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            if self.path == '/health':
                return reply(self, 200, {'status': 'ok'})
            if self.path == '/v1/summary':
                try:
                    release = client.read_release()
                    report = {'kind': 'summary', 'revision': release['revision'], 'cutoff': release['cutoff'], 'result': summarize(release)}
                    identifier = store.save(report)
                    return reply(self, 200, {'report_id': identifier, **report})
                except (ValueError, OSError, RuntimeError) as error:
                    return reply(self, 502, {'error': str(error)})
            if self.path.startswith('/v1/reports/'):
                report = store.load(self.path.rsplit('/', 1)[-1])
                return reply(self, 200 if report else 404, report or {'error': '未找到报告'})
            return reply(self, 404, {'error': '接口不存在'})

    return ThreadingHTTPServer(address, Handler)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8090)
    parser.add_argument('--source', default=os.getenv('SOURCE_URL', 'http://127.0.0.1:8091'))
    parser.add_argument('--database', default='/tmp/analysis-reports.sqlite3')
    args = parser.parse_args()
    make_server(('0.0.0.0', args.port), args.source, args.database).serve_forever()


if __name__ == '__main__':
    main()
