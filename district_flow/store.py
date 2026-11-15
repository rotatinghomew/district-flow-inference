import hashlib
import json
import sqlite3


class ReportStore:
    def __init__(self, path):
        self.path = path
        with self.connect() as connection:
            connection.execute('CREATE TABLE IF NOT EXISTS reports (id TEXT PRIMARY KEY, payload TEXT NOT NULL)')

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def save(self, report):
        payload = json.dumps(report, sort_keys=True, ensure_ascii=False, allow_nan=False)
        identifier = hashlib.sha256(payload.encode()).hexdigest()
        with self.connect() as connection:
            connection.execute('INSERT OR IGNORE INTO reports VALUES (?, ?)', (identifier, payload))
        return identifier

    def load(self, identifier):
        with self.connect() as connection:
            row = connection.execute('SELECT payload FROM reports WHERE id=?', (identifier,)).fetchone()
        return None if row is None else json.loads(row[0])
