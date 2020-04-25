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
                max(sent_date),
                min(sent_date)
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
    def main_subs(self):
        return tuple(self.db.to_list("""
            select sub from GENERAL where status='published' group by sub having count(*)>1000 order by count(*) desc limit 10
        """))

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

    def get_karma(self, where=None):
        if where is None:
            where = ""
        else:
            where = " and "+where
        data={}
        for dt in self.db.select('''
        select
            mes,
            -- noticias,
            round(karma) karma,
            positives,
            negatives
        from (
            select
                mes,
                avg(karma) karma,
                sum(votes)-count(id) positives,
                sum(negatives) negatives
            from
                GENERAL
            where
              (votes>1 or negatives>0) and -- si solo esta el voto del autor, la noticia no la 'vio' nadie
              not(status='autodiscard' and negatives=0) -- si se autodescarto sin negativos seria un error
              {0}
            group by
                mes
        ) T
        '''.format(where or ""), cursor=DictCursor):
            data[float(dt["mes"])]={k:float(v) for k,v in dt.items() if k!="mes"}
        return data


    def get_count_mensual(self):
        counts = []
        for s in self.status:
            if s not in (None, "abuse"):
                counts.append("sum(status='{0}') {0}".format(s))
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
        '''.format(counts), cursor=DictCursor):
            data[float(dt["mes"])]={k:int(v) for k,v in dt.items() if k!="mes"}
        return data

    def get_horas_mensual(self):
        data={}
        min_year = self.min_date.year
        max_year = self.max_date.year
        for dt in self.db.select('''
            select
                YEAR(sent_date) yr,
                floor(minuto/60) hora,
                count(id) todas,
                sum(status='published') published
            from
                GENERAL
            where
                YEAR(sent_date)>{0} and
                YEAR(sent_date)<{1}
            group by
                YEAR(sent_date), floor(minuto/60)
            order by YEAR(sent_date), floor(minuto/60)
        '''.format(min_year, max_year), cursor=DictCursor):
            yr = int(dt["yr"])
            hora = int(dt["hora"])
            horas = data.get(yr, {})
            horas[hora] = {k:int(v) for k,v in dt.items() if k not in ("yr", "hora")}
            data[yr]=horas
        return data

    def get_mes_categorias(self, where=None):
        if where is None:
            where = ""
        else:
            where = "and " + where
        data={}
        counts=[]
        for sub in self.main_subs:
            counts.append("sum(sub='{0}') `{0}`".format(sub))
        counts.append("sum(sub not in {0}) `otros`".format(self.main_subs))
        counts = ", ".join(counts)
        for dt in self.db.select('''
            select
                mes,
                count(id) total,
                {0}
            from
                GENERAL
            where
                sub is not null and sub!='' and YEAR(sent_date)>2013 {1}
            group by
                mes
            order by mes
        '''.format(counts, where), cursor=DictCursor):
            data[float(dt["mes"])]={k:int(v or 0) for k,v in dt.items() if k!="mes"}
        return data

    def get_dominios(self, where=None):
        if where is None:
            where = ""
        else:
            where = "and " + where
        min_year = self.min_date.year
        max_year = self.max_date.year
        data={}
        for yr, total in self.db.select('''
            select
                YEAR(sent_date) yr,
                count(*) total
            from
                GENERAL
            where
                YEAR(sent_date)>{1} and
                YEAR(sent_date)<{2} {0}
            group by
                YEAR(sent_date)
        '''.format(where, min_year, max_year)):
            data[int(yr)]={
                "total": int(total)
            }
        for dt in self.db.select('''
            select
            	YEAR(sent_date) yr,
            	dominio,
            	count(*) total
            from
                GENERAL
            where
                YEAR(sent_date)>{1} and
                YEAR(sent_date)<{2} and
                dominio is not null and
                dominio!='' {0}
            group by
                YEAR(sent_date),
                dominio
            having
                count(*)>50
        '''.format(where, min_year, max_year), cursor=DictCursor):
            yr=int(dt["yr"])
            data[yr][dt["dominio"]]=int(dt["total"])
        return data
