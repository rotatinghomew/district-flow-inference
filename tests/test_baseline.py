import json
import tempfile
import threading
import unittest
from pathlib import Path
from district_flow.app import make_server as app_server
from district_flow.provider import make_server as source_server
from district_flow.client import SourceClient
from district_flow.overview import summarize
from district_flow.store import ReportStore
from district_flow.wire import call, RemoteFailure


class BaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(Path('data/release.json').read_text())
        cls.source=source_server(('127.0.0.1',0),cls.data)
        cls.thread=threading.Thread(target=cls.source.serve_forever,daemon=True)
        cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.source.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.source.shutdown()
        cls.source.server_close()
        cls.thread.join()

    def test_pagination_preserves_every_row(self):
        release=SourceClient(self.base).read_release()
        self.assertEqual(release,self.data)

    def test_revision_cannot_be_mixed(self):
        name=next(iter(self.data['tables']))
        with self.assertRaises(RemoteFailure):
            call(self.base,'/v1/tables/'+name+'?revision=obsolete')

    def test_page_size_is_bounded(self):
        name=next(iter(self.data['tables']))
        with self.assertRaises(RemoteFailure):
            call(self.base,'/v1/tables/'+name+'?revision=release-1&limit=1001')

    def test_overview_is_order_independent(self):
        other=json.loads(json.dumps(self.data))
        for rows in other['tables'].values():
            rows.reverse()
        self.assertEqual(summarize(self.data),summarize(other))

    def test_report_is_content_addressed_and_persistent(self):
        with tempfile.TemporaryDirectory() as directory:
            path=str(Path(directory)/'reports.sqlite3')
            store=ReportStore(path)
            identifier=store.save({'result':{'count':3},'revision':'release-1'})
            self.assertEqual(identifier,store.save({'revision':'release-1','result':{'count':3}}))
            self.assertEqual(ReportStore(path).load(identifier)['result']['count'],3)
            self.assertNotEqual(identifier,store.save({'revision':'release-2','result':{'count':3}}))

    def test_http_application_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            app=app_server(('127.0.0.1',0),self.base,str(Path(directory)/'reports.sqlite3'))
            thread=threading.Thread(target=app.serve_forever,daemon=True)
            thread.start()
            try:
                base=f'http://127.0.0.1:{app.server_port}'
                first=call(base,'/v1/summary')
                self.assertEqual(first['result'],summarize(self.data))
                self.assertEqual(call(base,'/v1/reports/'+first['report_id'])['result'],first['result'])
                self.assertEqual(call(base,'/v1/summary')['report_id'],first['report_id'])
            finally:
                app.shutdown()
                app.server_close()
                thread.join()


if __name__=='__main__':
    unittest.main()
