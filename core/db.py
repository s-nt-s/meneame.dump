import os
import re
import sqlite3
import textwrap

import unidecode
import yaml
from bunch import Bunch

re_sp = re.compile(r"\s+")

sqlite3.register_converter("BOOLEAN", lambda x: int(x) > 0)
#sqlite3.register_converter("DATE", lambda x: datetime.strptime(str(x), "%Y-%m-%d").date())
sqlite3.enable_callback_tracebacks(True)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def bunch_factory(cursor, row):
    d = dict_factory(cursor, row)
    return Bunch(**d)


def one_factory(cursor, row):
    return row[0]


def plain_parse_col(c):
    c = re_sp.sub(" ", c).strip()
    c = c.lower()
    c = unidecode.unidecode(c)
    c = c.replace(" ", "_")
    return c


def ResultIter(cursor, size=1000):
    while True:
        results = cursor.fetchmany(size)
        if not results:
            break
        for result in results:
            yield result


def save(file, content):
    if file and content:
        content = textwrap.dedent(content).strip()
        with open(file, "w") as f:
            f.write(content)


class CaseInsensitiveDict(dict):
    def __setitem__(self, key, value):
        dict.__setitem__(self, key.lower(), value)

    def __getitem__(self, key):
        return dict.__getitem__(self, key.lower())


class DBLite:
    def __init__(self, file, parse_col=None, readonly=False, debug_dir=None):
        self.file = file
        self.readonly = readonly
        if self.readonly:
            file = "file:"+file+"?mode=ro"
            self.con = sqlite3.connect(
                file, detect_types=sqlite3.PARSE_DECLTYPES, uri=True)
        else:
            self.con = sqlite3.connect(
                file, detect_types=sqlite3.PARSE_DECLTYPES)
        self.tables = None
        self.srid = None
        self.parse_col = parse_col if parse_col is not None else lambda x: x
        self.load_tables()
        self.inTransaction = False
        self.closed = False
        self.debug_dir = None
        if debug_dir and os.path.isdir(debug_dir):
            if not debug_dir.endswith("/"):
                debug_dir = debug_dir + "/"
            self.debug_dir = debug_dir

    def openTransaction(self):
        if self.inTransaction:
            self.con.execute("END TRANSACTION")
        self.con.execute("BEGIN TRANSACTION")
        self.inTransaction = True

    def closeTransaction(self):
        if self.inTransaction:
            self.con.execute("END TRANSACTION")
            self.inTransaction = False

    def execute(self, sql, to_file=None):
        if os.path.isfile(sql):
            with open(sql, 'r') as schema:
                sql = schema.read()
        if sql.strip():
            save(to_file, sql)
            self.con.executescript(sql)
            self.con.commit()
            self.load_tables()

    def get_cols(self, sql):
        cursor = self.con.cursor()
        cursor.execute(sql)
        cols = tuple(col[0] for col in cursor.description)
        cursor.close()
        return cols

    def load_tables(self):
        self.tables = CaseInsensitiveDict()
        for t, in list(self.select("SELECT name FROM sqlite_master WHERE type in ('table', 'view')")):
            try:
                self.tables[t] = self.get_cols("select * from "+t+" limit 0")
            except:
                pass

    def create_table(self, table, row_example):
        self.load_tables()
        if table.lower() in self.tables:
            return
            sql = 'create table %s (' % table
        for k, v in row_example.items():
            t = "TEXT"
            if isinstance(v, int):
                t = "NUMBER"
            sql = sql + '\n  "%s" %s,' % (k, t)
        if "id" in row_example.keys():
            sql = sql + "\n  PRIMARY KEY (id)"
        else:
            sql = sql[:-1]
        sql = sql+"\n);\n"
        to_file = self.debug_dir + table + ".sql" if self.debug_dir else None
        self.execute(sql, to_file=to_file)
        self.commit()

    def insert(self, table, *args, insert_or=None, **kargv):
        if not args and not kargv:
            return
        if args:
            sobra = set()
            for a in args:
                a = {**kargv, **a}
                s = self.insert(table, insert_or=insert_or, **a)
                sobra = sobra.union(s.keys())
            return sorted(sobra)
        sobra = {}
        ok_keys = [k.upper() for k in self.tables[table]]
        keys = []
        vals = []
        for k, v in kargv.items():
            if v is None or (isinstance(v, str) and len(v) == 0):
                continue
            if k.upper() not in ok_keys:
                k = self.parse_col(k)
                if k.upper() not in ok_keys:
                    sobra[k] = v
                    continue
            keys.append('"'+k+'"')
            vals.append(v)
        prm = ['?']*len(vals)
        sql = "insert or "+insert_or if insert_or else "insert"
        sql = sql+" into %s (%s) values (%s)" % (
            table, ', '.join(keys), ', '.join(prm))
        self.con.execute(sql, vals)
        return sobra

    def update(self, table, **kargv):
        sobra = {}
        ok_keys = [k.upper() for k in self.tables[table]]
        keys = []
        vals = []
        sql_set = []
        id = None
        for k, v in kargv.items():
            if v is None or (isinstance(v, str) and len(v) == 0):
                continue
            if k.upper() not in ok_keys:
                k = self.parse_col(k)
                if k.upper() not in ok_keys:
                    sobra[k] = v
                    continue
            if k == "id":
                id = v
                continue
            sql_set.append(k+' = ?')
            vals.append(v)
        vals.append(id)
        sql = "update %s set %s where id = ?" % (
            table, ', '.join(sql_set))
        self.con.execute(sql, vals)
        return sobra

    def _build_select(self, sql):
        sql = sql.strip()
        if not sql.lower().startswith("select"):
            field = "*"
            if "." in sql:
                sql, field = sql.rsplit(".", 1)
            sql = "select "+field+" from "+sql
        return sql

    def commit(self):
        self.con.commit()

    def close(self, vacuum=False):
        if self.closed:
            return
        if self.readonly:
            self.con.close()
            self.closed = True
            return
        self.closeTransaction()
        self.con.commit()
        if vacuum:
            self.con.execute("VACUUM")
        self.con.commit()
        self.con.close()
        self.closed = True

    def select(self, sql, *args, row_factory=None, **kargv):
        sql = self._build_select(sql)
        self.con.row_factory = row_factory
        cursor = self.con.cursor()
        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)
        for r in ResultIter(cursor):
            yield r
        cursor.close()
        self.con.row_factory = None

    def one(self, sql):
        sql = self._build_select(sql)
        cursor = self.con.cursor()
        cursor.execute(sql)
        r = cursor.fetchone()
        cursor.close()
        if not r:
            return None
        if len(r) == 1:
            return r[0]
        return r
