import json
import tempfile
import threading
from pathlib import Path
from .app import make_server as app_server
from .provider import make_server as source_server
from .wire import call


def main():
    data = json.loads(Path('data/release.json').read_text())
    source = source_server(('127.0.0.1', 0), data)
    source_thread = threading.Thread(target=source.serve_forever, daemon=True)
    source_thread.start()
    with tempfile.TemporaryDirectory() as directory:
        app = app_server(('127.0.0.1', 0), f'http://127.0.0.1:{source.server_port}', str(Path(directory)/'reports.sqlite3'))
        app_thread = threading.Thread(target=app.serve_forever, daemon=True)
        app_thread.start()
        try:
            base = f'http://127.0.0.1:{app.server_port}'
            health = call(base, '/health')
            report = call(base, '/v1/summary')
            saved = call(base, '/v1/reports/' + report['report_id'])
            print(json.dumps({'服务状态': health, '当前概览': report, '存档一致': saved['result'] == report['result']}, ensure_ascii=False, indent=2))
        finally:
            app.shutdown()
            app.server_close()
            app_thread.join()
            source.shutdown()
            source.server_close()
            source_thread.join()


if __name__ == '__main__':
    main()
