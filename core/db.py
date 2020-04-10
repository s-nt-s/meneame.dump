import os
import re
import textwrap

import unidecode
import yaml
from bunch import Bunch
import MySQLdb
from .util import chunks, parse_tag
import sqlite3

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
        self.meta = Bunch()
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
        self.load_meta()

    def load_meta(self):
        self.meta = {}
        for k, v in self.select("select id, value from META_INT"):
            self.meta[k]=v
        for k, v in self.select("select id, value from META_STR"):
            self.meta[k]=v
        self.meta=Bunch(**self.meta)

    def save_meta(self, *keys):
        meta_int = []
        meta_str = []
        for k, v in self.meta.items():
            if len(keys)>0 and k not in keys:
                continue
            if isinstance(v, int):
                meta_int.append((k, v))
            else:
                meta_str.append((k, v))
        if not meta_int and not meta_str:
            return
        cursor = self.con.cursor()
        if meta_int:
            cursor.executemany("replace into META_INT (id, value) values (%s, %s)", meta_int)
        if meta_str:
            cursor.executemany("replace into META_STR (id, value) values (%s, %s)", meta_str)
        cursor.close()
        self.commit()

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

    def one(self, sql, cursor=None):
        sql = self._build_select(sql)
        cursor = self.con.cursor(cursor)
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
        return cols

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


    def _update(self, table, cols, rows):
        if not cols:
            return None
        if "id" not in cols:
            raise Exception("id not found")
        cols.remove("id")
        sql_set = []
        for c in cols:
            sql_set.append("`{0}` = %({0})s".format(c))
        sql = "update `{0}` set ".format(table) + ", ".join(sql_set) + " where id = %(id)s"
        cursor = self.con.cursor()
        cursor.executemany(sql, rows)
        cursor.close()
        self.con.commit()

    def update(self, table, rows, skipNull=False):
        if not row:
            return
        if skipNull:
            obj={}
            for r in row:
                cols = self.parse_row(table, r, skipNull=True)
                if cols:
                    if cols not in obj:
                        obj[cols]=[]
                    obj[cols].append(o)
            for c, r in obj.items():
                self._update(table, c, r)
            return
        cols = self.parse_row(table, rows)
        self._update(table, cols, rows)

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
        self.save_meta()
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

    def comment_gaps(self, cursor, time_enabled_comments, size=2000):
        max_date = self.one("select max(sent_date) from LINKS")
        if max_date is not None:
            max_date = max_date - time_enabled_comments
            max_id = self.one("select max(id) from LINKS where sent_date<"+str(max_date))
            if max_id is not None:
                while cursor < max_id:
                    ids = self.to_list('''
                        select id from
                        COMMENTS
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

    def loop_tags(self, where=""):
        max_date = self.meta.get("max_date")
        if max_date is not None:
            where = ("sent_date < %s and " % max_date)+where
        if where.strip() and not where.strip().endswith(" and"):
            where = where + " and "
        for id, tags, status in self.select('''
            select
                id,
                tags,
                status
            from LINKS
            where {0} tags is not null and TRIM(tags)!=''
            order by id
        '''.format(where)):
            tags = tags.lower().strip().split(",")
            tags = set(t.strip() for t in tags if t.strip())
            tags = set([parse_tag(t) for t in tags])
            tags = sorted(t for t in tags if t is not None)
            for tag in tags:
                yield (tag, id, status)

    def fix(self, time_enabled_comments=None):
        if time_enabled_comments:
            max_date = self.one("select max(sent_date) from LINKS")
            if max_date is not None:
                self.meta.max_date = max_date - time_enabled_comments
                self.save_meta("max_date")
        self.execute("sql/update_users.sql")
        self.commit()
        self.execute("delete from TAGS;")
        self.commit()
        insert = "insert into TAGS (tag, link, status) values (%s, %s, %s)"
        for tags_links in chunks(self.loop_tags(), 2000):
            c = self.con.cursor()
            c.executemany(insert, tags_links)
            c.close()
            self.con.commit()
        self.commit()
        self.execute('''
            delete from TAGS
            where tag not in (
                select tag from TAGS
                where status='published'
                group by tag
                having count(link)>=100
            )
        ''')
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
