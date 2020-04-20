from .db import DB
from .api import Api
from functools import lru_cache
from MySQLdb.cursors import DictCursor
from dateutil.relativedelta import relativedelta


def read_file(file, *args, **kargv):
    with open(file, "r") as f:
        txt = f.read()
        if args or kargv:
            txt = txt.format(*args, **kargv)
        return txt

class Stats:
    def __init__(self):
        self.db = DB()
        self.max_date, self.min_date = self.db.one('''
            select
                from_unixtime(max(sent_date)),
                from_unixtime(min(sent_date))
            from GENERAL
        ''')
        self.max_portada, self.min_portada = self.db.one('''
            select
                max(id),
                min(id)
            from GENERAL
            where
                status='published'
        ''')
        self.status = self.db.to_list('''
            select distinct status from GENERAL
        ''')
        if '' in self.status:
            self.status.remove('')
            if None not in self.status:
                self.status.append(None)
        self.status = tuple(sorted(self.status, key=lambda x:({
            "published": 1,
            "queued": 2,
            "autodiscard": 3,
            "discard": 4,
            "abuse": 5,
            None: 9
        }.get(x,8), x)))

    def __del__(self):
        self.db.close()

    @property
    @lru_cache(maxsize=None)
    def counts(self):
        sql_1=[]
        sql_2=[]
        for s in self.status:
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
                    GENERAL
            ) T
        '''.format(",\n".join(sql_2), ",\n".join(sql_1)).strip()

        count=self.db.one(sql, cursor=DictCursor)
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

    def get_data_mensual(self, where=None):
        if where is None:
            where = "where status not in ('autodiscard', 'abuse')"
        else:
            where = "where " + where
        data={}
        for dt in self.db.select('''
        select
            mes,
            -- noticias,
            round(karma) karma,
            round((votes*100/(votes+negatives))*100)/100 positives,
            round((negatives*100/(votes+negatives))*100)/100 negatives,
            round(comments) comments
        from (
            select
                mes,
                -- count(id) noticias,
                avg(karma) karma,
                sum(votes)-count(id) votes,
                sum(negatives) negatives,
                avg(comments) comments
            from
                GENERAL {0}
            group by
                mes
        ) T
        '''.format(where), cursor=DictCursor):
            data[float(dt["mes"])]={k:float(v) for k,v in dt.items() if k!="mes"}
        return data


    def get_count_mensual(self):
        counts = []
        for s in self.status:
            if s not in (None, "abuse"):
                counts.append("sum(status='{0}') {0}".format(s))
        #counts.append("sum(sub not in {0}) sub".format(Api.SUBS))
        for c in list(counts):
            rl, nm = c.rsplit(" ", 1)
            counts.append("round(({0}*100/count(*))*100)/100 prc_{1}".format(rl, nm))
        counts = ", ". join(counts)
        data={}
        for dt in self.db.select('''
        select
            mes,
            count(*) total,
            {0}
        from
            GENERAL
        group by
            mes
        '''.format(counts, Api.SUBS), cursor=DictCursor):
            data[float(dt["mes"])]={k:int(v) for k,v in dt.items() if k!="mes"}
        return data

    def get_horas_mensual(self, where=None):
        if where is None:
            where = "where status not in ('autodiscard', 'abuse')"
        else:
            where = "where " + where
        data={}
        for dt in self.db.select('''
            select
                mes,
                round(minuto/60) hora,
                count(id) todas,
                sum(status='published') published
            from
                GENERAL {0}
            group by
                mes, round(minuto/60)
            order by mes, hora
        '''.format(where), cursor=DictCursor):
            dt = {k:int(v) for k,v in dt.items()}
            obj = data.get(dt["mes"], {})
            v = obj.get("todas")
            if v is None or v[0]<dt["todas"]:
                obj["todas"] = (dt["todas"], dt["hora"])
            v = obj.get("published")
            if v is None or v[0]<dt["published"]:
                obj["published"] = (dt["published"], dt["hora"])
        return data
