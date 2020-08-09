import os
import re
import textwrap

import unidecode
import yaml
from bunch import Bunch
import MySQLdb
from .util import chunks, extract_tags, gW
from .api import Api, tm_search_user_data
from .threadme import ThreadMe
import sqlite3
import sys

import warnings
warnings.filterwarnings("ignore", category = MySQLdb.Warning)

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

class DB:
    def __init__(self, debug_dir=None):
        self.tables = None
        self.closed = False
        self.insert_count = 0
        self.debug_dir = None
        if debug_dir and os.path.isdir(debug_dir):
            if not debug_dir.endswith("/"):
                debug_dir = debug_dir + "/"
            self.debug_dir = debug_dir
        self.name = 'meneame'
        host = os.environ.get("MARIADB_HOSTS", "localhost")
        port = os.environ.get("MARIADB_PORT", "3306")
        self.con = MySQLdb.connect(host=host, port=int(port), user='meneame', password='meneame', database=self.name)
        self.con.set_character_set('utf8mb4')
        cursor = self.con.cursor()
        cursor.execute('SET NAMES utf8mb4;')
        cursor.execute('SET CHARACTER SET utf8mb4;')
        cursor.execute('SET character_set_connection=utf8mb4;')
        cursor.execute("SET time_zone='Europe/Madrid';")
        cursor.close()
        self.load_tables()

    def load_tables(self):
        self.tables = dict()
        for t in self.table_names:
            try:
                self.tables[t] = self.get_cols("select * from "+t+" limit 0")
            except:
                pass

    @property
    def table_names(self):
        return tuple(i[0] for i in self.select("SELECT table_name FROM information_schema.tables where table_type in ('VIEW', 'BASE TABLE')"))

    def commit(self):
        self.con.commit()

    def get_cols(self, sql, cursor=None):
        if cursor is None:
            cursor = self.con.cursor()
        cursor.execute(sql)
        cols = tuple(col[0] for col in cursor.description)
        cursor.close()
        return cols

    def _build_select(self, sql):
        sql = sql.strip()
        if not sql.lower().startswith("select"):
            field = "*"
            if "." in sql:
                sql, field = sql.rsplit(".", 1)
            sql = "select "+field+" from "+sql
        return sql

    def select(self, sql, *args, cursor=None, **kargv):
        sql = self._build_select(sql)
        cursor = self.con.cursor(cursor)
        cursor.execute(sql)
        for r in ResultIter(cursor):
            yield r
        cursor.close()

    def one(self, sql, *args, cursor=None):
        sql = self._build_select(sql)
        cursor = self.con.cursor(cursor)
        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)
        r = cursor.fetchone()
        cursor.close()
        if not isinstance(r, (list, tuple)):
            return r
        if not r:
            return None
        if len(r) == 1:
            return r[0]
        return r

    def parse_row(self, table, row, skipNull=False):
        if row and not isinstance(row, dict):
            row = row[0]
        if not row:
            return None
        _cols = self.tables[table]
        cols=[]
        for k, v in sorted(row.items()):
            if k not in _cols:
                continue
            if v is None and skipNull:
                continue
            cols.append(k)
        return tuple(cols)

    def insert(self, table, rows, insert="insert"):
        cols = self.parse_row(table, rows)
        if cols is None:
            return
        _cols = "`" + "`, `".join(cols) + "`"
        _vals = "%(" + ")s, %(".join(cols) + ")s"
        sql = insert+ " into `{0}` ({1}) values ({2})".format(table, _cols, _vals)
        cursor = self.con.cursor()
        for rws in chunks(rows, 2000):
            cursor.executemany(sql, rws)
        cursor.close()
        self.con.commit()

    def upsert(self, table, skipNull=True, **row):
        cols = self.parse_row(table, row, skipNull=skipNull)
        if cols is None:
            return
        _cols = "`" + "`, `".join(cols) + "`"
        _vals = "%(" + ")s, %(".join(cols) + ")s"
        sql = "insert into `{0}` ({1}) values ({2}) on duplicate key update ".format(table, _cols, _vals)
        sql_set = ["`{0}` = %({0})s".format(c) for c in cols]
        sql = sql + ", ".join(sql_set)
        cursor = self.con.cursor()
        cursor.execute(sql, row)
        cursor.close()
        self.con.commit()

    def replace(self, *args):
        self.insert(*args, insert="replace")

    def ignore(self, *args):
        self.insert(*args, insert="insert ignore")


    def _update(self, table, cols, rows, fixSet=""):
        if not cols:
            return None
        if "id" not in cols:
            raise Exception("id not found")
        cols = tuple(c for c in cols if c!="id")
        sql_set = []
        for c in cols:
            sql_set.append("`{0}` = %({0})s".format(c))
        sql = "update `{0}` set {1} ".format(table, fixSet) + ", ".join(sql_set) + " where id = %(id)s"
        cursor = self.con.cursor()
        cursor.executemany(sql, rows)
        cursor.close()
        self.con.commit()

    def update(self, table, rows, skipNull=False, fixSet=""):
        if not rows:
            return
        if skipNull:
            obj={}
            for r in rows:
                cols = self.parse_row(table, r, skipNull=True)
                if cols:
                    if cols not in obj:
                        obj[cols]=[]
                    obj[cols].append(r)
            for c, r in obj.items():
                self._update(table, c, r, fixSet=fixSet)
            return
        cols = self.parse_row(table, rows)
        self._update(table, cols, rows, fixSet=fixSet)

    def to_list(self, *args, **kargv):
        lst = list(self.select(*args, **kargv))
        if lst and len(lst[0])==1:
            return [i[0] for i in lst]
        return lst

    def execute(self, sql, *args, to_file=None):
        if os.path.isfile(sql):
            with open(sql, "r") as f:
                sql = f.read()
        if args:
            sql=sql.format(*args)
        if to_file:
            with opne(to_file, "w") as f:
                f.write(sql)
        sql = "\n".join(i for i in sql.split("\n") if i.strip()[:2] not in ("", "--"))
        cursor = self.con.cursor()
        for i in sql.split(";"):
            if i.strip():
                cursor.execute(i)
        cursor.close()
        self.con.commit()

    def close(self):
        if self.closed:
            return
        self.con.commit()
        self.con.close()
        self.closed = True

    def link_gaps(self, cursor, size=2000):
        max_id = self.one("select max(id) from LINKS")
        if max_id is not None:
            while cursor < max_id:
                ids = self.to_list('''
                    select id from
                    LINKS
                    where id>={0}
                    order by id
                    limit {1}
                '''.format(cursor, size))
                max_range = min(max_id, cursor+size+1)
                if len(ids) and max_range<=ids[-1]:
                    max_range=ids[-1]+1
                for i in range(cursor, max_range):
                    if i not in ids:
                        yield i
                cursor = max_range

    def loop_tags(self):
        for id, tags in self.select('''
            select
                id,
                tags
            from
                GENERAL
            where
                status='published' and
                tags is not null and
                id not in (select link from TAGS)
        '''):
            print(id, end="\r")
            for tag in extract_tags(tags):
                yield (tag, id)

    def insert_tags(self):
        insert = "insert into TAGS (tag, link) values (%s, %s)"
        for tags_links in chunks(self.loop_tags(), 2000):
            c = self.con.cursor()
            c.executemany(insert, tags_links)
            c.close()
            self.con.commit()
        self.commit()

    def clone(self, file, table):
        file = "file:"+file+"?mode=ro"
        lt = sqlite3.connect(file, detect_types=sqlite3.PARSE_DECLTYPES, uri=True)
        cols = self.get_cols("select * from "+table+" limit 1", lt.cursor())
        cols = set(self.tables[table]).intersection(set(cols))
        cols = sorted(cols)
        _cols = "`" + "`, `".join(cols) + "`"
        _vals = ", ".join(["%s"] * len(cols))
        insert = "replace into `{0}` ({1}) values ({2})".format(table, _cols, _vals)

        _cols = '"' + '", "'.join(cols) + '"'
        select = "select {0} from {1}".format(_cols, table)
        if "id" in cols:
            select = select + " order by id"

        cursor = lt.cursor()
        cursor.execute(select)
        for rows in chunks(ResultIter(cursor), 1000):
            c = self.con.cursor()
            c.executemany(insert, rows)
            c.close()
            self.con.commit()
        cursor.close()
        lt.close()

    def update_users(self):
        self.execute("sql/views/users.sql")
        max_user = self.one("select max(id) from USERS")
        min_user = self.one("select max(id) from USERS where `create` is not null") or 0
        api = Api()
        tm = ThreadMe(max_thread=100, list_size=2000)
        def my_tm_search_user_data(id):
            print(id, end="\r")
            u = tm_search_user_data(id)
            if u is None or u.id is None:
                return None
            if u.create is None and (u.live is None or u.live):
                return None
            return {
                "id": u.id,
                "create":u.create,
                "live":u.live
            }
        sql = "insert into USERS (id, `create`, `live`) values (%(id)s, %(create)s, %(live)s) on duplicate key update `create`=values(`create`), `live`=values(`live`)"
        for rows in tm.list_run(my_tm_search_user_data, range(min_user+1, max_user+1)):
            c = self.con.cursor()
            c.executemany(sql, rows)
            c.close()
            self.con.commit()
        def my_tm_search_user_live(id):
            r = my_tm_search_user_data(id)
            if r and r.live is False:
                return id
            return None
        sql = "update USERS set live=0 where id "
        for ids in tm.list_run(my_tm_search_user_live, self.select("select id from USERS where live=1")):
            c = self.con.cursor()
            c.execute(sql+gW(ids))
            c.close()
            self.con.commit()


if __name__ == "__main__":
    db=DB()
    arg = sys.argv[1]
    try:
        if arg == "tags":
            db.execute("delete from TAGS")
            db.commit()
            db.insert_tags()
        if arg == "users":
            db.update_users()
            db.commit()
        print("")
    finally:
        db.close()
