from urllib.parse import urlencode
from .wire import call, RemoteFailure


class SourceClient:
    def __init__(self, base):
        self.base = base

    def read_release(self):
        catalog = call(self.base, '/v1/catalog')
        tables = {}
        for name in catalog['tables']:
            rows = []
            offset = 0
            while True:
                query = urlencode({'revision': catalog['revision'], 'offset': offset, 'limit': 31})
                page = call(self.base, '/v1/tables/' + name + '?' + query)
                if page['revision'] != catalog['revision']:
                    raise RemoteFailure('资料版本不一致')
                rows.extend(page['rows'])
                if page['next'] is None:
                    break
                if page['next'] <= offset:
                    raise RemoteFailure('分页游标未前进')
                offset = page['next']
            tables[name] = rows
        return {'revision': catalog['revision'], 'cutoff': catalog['cutoff'], 'settings': catalog['settings'], 'tables': tables}
