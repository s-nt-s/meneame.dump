from .db import DB
from .api import Api
from .graph import Graph
from functools import lru_cache
from MySQLdb.cursors import DictCursor
from dateutil.relativedelta import relativedelta
from bunch import Bunch


def read_file(file, *args, **kargv):
    with open(file, "r") as f:
        txt = f.read()
        if args or kargv:
            txt = txt.format(*args, **kargv)
        return txt

def get_root(dom):
    i=1
    while True:
        i = i + 1
        root = ".".join(dom.split(".")[-i:])
        if len(root)>5 and root!=dom and not root.startswith("com."):
            return "*."+root
        if root == dom:
            return "*."+root

class Stats:
    def __init__(self):
        self.db = DB()
        self.min_tag=300
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
            },
            "posts": self.db.one("select count(*) from POSTS")
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
        if where !="":
            where = " where "+where[5:]
        max_mes = max(data.keys())
        for dt in self.db.select('''
            select
                mes,
                round(avg(karma)) karma
            from (
                select
                    date_mod(from_unixtime(`date`), 1) mes,
                    karma
                from
                    COMMENTS
                where link in (select id from GENERAL {1})
            ) T
            where
                mes <= {0}
            group by
                mes
        '''.format(max_mes, where or ""), cursor=DictCursor):
            key = float(dt["mes"])
            for k, v in dt.items():
                if k!="mes":
                    data[key]["comment_"+k]=float(v)
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

    def get_uso_tiempo(self):
        data={}
        sql=['''
            select
                YEAR(sent_date) YR,
                concat('H', sent_hour) K,
                sum(links) noticias,
                sum(comments) comentarios,
                sum(posts) posts
            from
                ACTIVIDAD
            group by
                YEAR(sent_date), sent_hour
        '''.strip()]
        i_sql='''
            select
                YEAR(sent_date) YR,
                concat('{0}', {1}(sent_date)) K,
                sum(links) noticias,
                sum(comments) commentarios,
                sum(posts) posts
            from
                ACTIVIDAD
            group by
                YEAR(sent_date), {1}(sent_date)
        '''.strip()
        for k in ("WEEKDAY", "MONTH"):
            sql.append(i_sql.format(k[0], k))
        sql = "\nUNION\n".join(sql)
        for dt in self.db.select(sql, cursor=DictCursor):
            yr = int(dt["YR"])
            if yr not in data:
                data[yr] = {}
            if dt["K"] not in data[yr]:
                data[yr][dt["K"]]={}
            for k,v in dt.items():
                if k!=k.upper():
                    data[yr][dt["K"]][k]=int(v)
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
        if self.max_date.month == 12:
            max_year = max_year + 1
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
            	domain,
            	count(*) total
            from
                GENERAL
            where
                YEAR(sent_date)>{1} and
                YEAR(sent_date)<{2} and
                domain is not null {0}
            group by
                YEAR(sent_date),
                domain
        '''.format(where, min_year, max_year), cursor=DictCursor):
            yr=int(dt["yr"])
            data[yr][dt["domain"]]=int(dt["total"])
        return data

    def get_full_dominios(self, min_count=50):

        dominios_todos = self.get_dominios()
        dominios_portada = self.get_dominios("status='published'")

        dominios=set()
        for yr in dominios_portada.values():
            for d, count in yr.items():
                if count>=min_count:
                    dominios.add(d)

        for dom in (dominios_portada, dominios_todos):
            for yr in dom.values():
                for d in list(yr.keys()):
                    if d not in dominios:
                        del yr[d]

        if "total" in dominios:
            dominios.remove("total")
        visto=set()
        for d in list(dominios):
            root = get_root(d)
            if root in visto:
                dominios.add(root)
            else:
                visto.add(root)
        dominios = sorted(dominios, key=lambda x: x.replace("*.", ""))

        return Bunch(
            todos=dominios_todos,
            portada=dominios_portada,
            claves=dominios
        )

    def get_tags(self):
        #min_dt, max_dt = self.db.one("select min(trimestre), max(trimestre) from GENERAL")
        min_dt = self.min_date.year
        max_dt = self.max_date.year
        if self.max_date.month == 12:
            max_dt = max_dt + 1
        data={}
        for key, total in self.db.select('''
            select
                YEAR(sent_date) d,
                count(*) total
            from
                GENERAL
            where
                YEAR(sent_date)>{0} and YEAR(sent_date)<{1} and
                status='published'
            group by
                YEAR(sent_date)
        '''.format(min_dt, max_dt)):
            data[int(key)]={
                "total": int(total)
            }
        tags=set()
        for dt in self.db.select('''
            select
                YEAR(sent_date) d,
                tag,
                count(distinct id) total
            from
                GENERAL JOIN TAGS on id=link
            where
                YEAR(sent_date)>{0} and YEAR(sent_date)<{1} and
                tag != 'total' and
                tag in (
                    select tag from TAGS group by tag having count(*)>={2}
                )
            group by
                YEAR(sent_date),
                tag
        '''.format(min_dt, max_dt, self.min_tag), cursor=DictCursor):
            tags.add(dt["tag"])
            data[int(dt["d"])][dt["tag"]]=int(dt["total"])
        return Bunch(
            claves=sorted(tags),
            portada=data
        )

    def get_tags_graph(self):
        g = Graph()
        for tag, size in self.db.select('''
            select
                tag,
                count(*) total
            from
                TAGS
            group by
                tag
            order by
                count(*) desc
            limit 80
        '''.format(self.min_tag)):
            g.add(tag, size)

        for a, b, size in self.db.select('''
            select
                t1.tag a,
                t2.tag b,
                count(*) size
            from
                TAGS t1 join TAGS t2 on
                    t1.link=t2.link and
                    t1.tag>t2.tag
            where
                t1.tag in {0} and t2.tag in {0}
            group by
                t1.tag, t2.tag
        '''.format(g.nodes)):
            g.add_edge(a, b, weight=size)

        return g.sigmajs

    def get_actividad(self):
        data={}
        for dt in self.db.select('''
            select
                date_mod(sent_date, 1) mes,
                sum(links) noticias,
                sum(comments) comentarios,
                sum(posts) posts,
                count(distinct user_id) `usuarios activos`
            from
                ACTIVIDAD
            group by
                date_mod(sent_date, 1)
        ''', cursor=DictCursor):
            data[float(dt["mes"])]={k:int(v) for k,v in dt.items() if k!="mes"}

        max_mes = max(data.keys())
        for dt in self.db.select('''
            select
                date_mod(`create`, 1) mes,
                count(*) `usuarios creados`
            from
                USERS
            where
                `create` is not null and
                date_mod(`create`, 1) <= {0}
            group by
                date_mod(`create`, 1)
        '''.format(max_mes), cursor=DictCursor):
            key = float(dt["mes"])
            for k, v in dt.items():
                if k!="mes":
                    data[key][k]=int(v)

        for dt in self.db.select('''
            select
                date_mod(`until`, 1) mes,
                count(*) `usuarios eliminados`
            from
                USERS
            where
                `live` = 0 and
                `until` is not null and
                date_mod(`until`, 1) <= {0}
            group by
                date_mod(`until`, 1)
        '''.format(max_mes), cursor=DictCursor):
            key = float(dt["mes"])
            for k, v in dt.items():
                if k!="mes":
                    data[key][k]=int(v)

        for dt in self.db.select('''
            select
                date_mod(`until`, 1) mes,
                count(*) `usuarios abandonados`
            from
                USERS
            where
                `live` = 1 and
                `until` is not null and
                DATEDIFF(NOW(),`until`)>365 and
                date_mod(`until`, 1) <= {0}
            group by
                date_mod(`until`, 1)
        '''.format(max_mes), cursor=DictCursor):
            key = float(dt["mes"])
            for k, v in dt.items():
                if k!="mes":
                    data[key][k]=int(v)

        return data

    def get_users_by_period(self):
        data={}
        for tp, nb in (
            ("T", "date_mod(sent_date, 3)"),
            ("S", "date_mod(sent_date, 6)"),
            ("A", "YEAR(sent_date)")
        ):
            for key, usuarios in self.db.select('''
                select
                    {0},
                    count(distinct user_id) usuarios
                from
                    ACTIVIDAD
                group by
                    {0}
            '''.format(nb)):
                if tp!="A":
                    key = "{:.2f}".format(key)
                    key = key.replace(".0", " "+tp)
                data[key] = int(usuarios)

        return data
