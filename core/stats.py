from .db import DB
from .api import Api
from functools import lru_cache
from MySQLdb.cursors import DictCursor


def read_file(file, *args, **kargv):
    with open(file, "r") as f:
        txt = f.read()
        if args or kargv:
            txt = txt.format(*args, **kargv)
        return txt

class Stats:
    def __init__(self):
        self.db = DB()
        self.api = Api()
        self.cut_date = self.db.one("select max(sent_date) from LINKS")
        self.cut_date = self.cut_date - self.api.mnm_config['time_enabled_comments']
        self.max_date, self.min_date = db.one('''
                select
                    from_unixtime(max(sent_date)),
                    from_unixtime(min(sent_date))
                from LINKS where sent_date<{0}
            '''.format(self.cut_date)
        )
        self.max_portada, self.min_portada = db.one('''
            select
                max(id),
                min(id)
            from LINKS
            where
                sub_status='published' and sub_status_id=1 and sent_date<{0}
            '''.format(self.cut_date)
        )

    def __del__(self):
        self.db.close()

    @property
    @lru_cache(maxsize=None)
    def base_sql():
        return read_file("sql/template/base.sql", self.cut_date)

    @property
    @lru_cache(maxsize=None)
    def counts(self):
        status = self.db.to_list('''
            select distinct sub_status
            from LINKS where sub_status_id=1 and sent_date<{0}
            '''.format(self.cut_date)
        )
        if '' in status:
            status.remove('')
            if None not in status:
                status.append(None)
        sql_1=[]
        sql_2=[]
        for s in status:
            if s is None:
                sql_1.append('''
                case
                    when status='' or status is null then 1
                    else 0
                end `sin estado`,
                case
                    when status='' or status is null then comments
                    else 0
                end `cmt_sin estado`
                '''.strip())
                sql_2.append('''
                    sum(T.`sin estado`) `sin estado`,
                    sum(T.`cmt_sin estado`) `cmt_sin estado`
                '''.format(s))
                continue
            sql_1.append('''
            case
                when status='{0}' then 1
                else 0
            end {0},
            case
                when status='{0}' then comments
                else 0
            end cmt_{0}
            '''.format(s).strip())
            sql_2.append('''
            sum(T.{0}) {0},
            sum(T.cmt_{0}) cmt_{0}
            '''.format(s).strip())
        sql = '''
            select
                {0}
            from (
                select
                    {1}
                from
                    LINKS
                where
                    sub_status_id=1 and sent_date<{0}
            ) T
        '''.format(",\n".join(sql_2), ",\n".join(sql_1), self.cut_date).strip()

        count=db.one(sql, cursor=DictCursor)
        count={k: int(v) for k,v in count.items()}
        count_cmt={}
        for k,v  in list(count.items()):
            if k.startswith("cmt_"):
                count_cmt[k[4:]]=v
                del count[k]
        return {
            "links": {
                "total": sum(count.values()),
                "status": sorted(count.items(), key=lambda x:(-x[1], x[0]))
            },
            "comments": {
                "total": sum(count_cmt.values()),
                "status": count_cmt
            }
        }
