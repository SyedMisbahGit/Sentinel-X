import sqlite3
import json
import os
import logging

log = logging.getLogger("rich")

class DBList:
    def __init__(self, conn, table):
        self.conn = conn
        self.table = table

    def append(self, item):
        try:
            val = json.dumps(item) if isinstance(item, (dict, list)) else str(item)
            c = self.conn.cursor()
            c.execute(f"INSERT OR IGNORE INTO {self.table} (data) VALUES (?)", (val,))
            self.conn.commit()
        except Exception as e:
            log.error(f"DB Append Error in {self.table}: {e}")

    def extend(self, items):
        if not items: return
        try:
            # Safely stringify everything before binding
            vals = [(json.dumps(i) if isinstance(i, (dict, list)) else str(i),) for i in items]
            c = self.conn.cursor()
            c.executemany(f"INSERT OR IGNORE INTO {self.table} (data) VALUES (?)", vals)
            self.conn.commit()
        except Exception as e:
            log.error(f"DB Extend Error in {self.table}: {e}")

    def __iter__(self):
        c = self.conn.cursor()
        c.execute(f"SELECT data FROM {self.table}")
        for row in c.fetchall():
            try:
                yield json.loads(row[0])
            except json.JSONDecodeError:
                yield row[0]

    def __len__(self):
        c = self.conn.cursor()
        c.execute(f"SELECT COUNT(*) FROM {self.table}")
        return c.fetchone()[0]

    def __bool__(self):
        return len(self) > 0

    def clear(self):
        c = self.conn.cursor()
        c.execute(f"DELETE FROM {self.table}")
        self.conn.commit()

class TargetSession:
    def __init__(self, domain, mode="standard"):
        self.domain = domain
        self.mode = mode
        os.makedirs("data/sessions", exist_ok=True)
        self.db_path = f"data/sessions/{domain.replace('.', '_')}.db"
        
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        
        # THE ACCELERATOR: SQLite PRAGMA Optimizations
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.conn.execute("PRAGMA temp_store=MEMORY;")
        
        self._init_db()

        self.subdomains = DBList(self.conn, "subdomains")
        self.live_hosts = DBList(self.conn, "live_hosts")
        self.vulnerabilities = DBList(self.conn, "vulnerabilities")
        self.cidrs = DBList(self.conn, "cidrs")
        self.crawled_urls = DBList(self.conn, "crawled_urls")

    def _init_db(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS subdomains (data TEXT UNIQUE)")
        c.execute("CREATE TABLE IF NOT EXISTS live_hosts (data TEXT UNIQUE)")
        c.execute("CREATE TABLE IF NOT EXISTS vulnerabilities (data TEXT UNIQUE)")
        c.execute("CREATE TABLE IF NOT EXISTS cidrs (data TEXT UNIQUE)")
        c.execute("CREATE TABLE IF NOT EXISTS crawled_urls (data TEXT UNIQUE)")
        self.conn.commit()

    def save(self):
        # Auto-committed by SQLite. Maintained to prevent legacy crashes.
        pass

    def purge(self):
        self.conn.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
