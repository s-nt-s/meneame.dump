#!/usr/bin/env python3

from core.db import DB
from core.j2 import Jnj2
from core.api import Api
from MySQLdb.cursors import DictCursor

db = DB()
api = Api()

max_date = db.one("select max(sent_date) from LINKS")
max_date = max_date - api.mnm_config['time_enabled_comments']
s_max_date = str(max_date)

max_date, min_date = db.one('''
    select
        from_unixtime(max(sent_date)),
        from_unixtime(min(sent_date))
    from LINKS where sent_date<'''+s_max_date
)

max_portada, min_portada = db.one('''
    select
        max(id),
        min(id)
    from LINKS where (id=1 or status='published') and sent_date<'''+s_max_date
)

status = db.to_list("select distinct status from LINKS where sent_date<"+s_max_date)
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
            sent_date<{2}
    ) T
'''.format(",\n".join(sql_2), ",\n".join(sql_1), s_max_date).strip()

count=db.one(sql, cursor=DictCursor)
count={k: int(v) for k,v in count.items()}
count_cmt={}
for k,v  in list(count.items()):
    if k.startswith("cmt_"):
        count_cmt[k[4:]]=v
        del count[k]

jHtml = Jnj2("template/", "docs/")

jHtml.save("informe.md",
    links={
        "total":sum(count.values()),
        "status": sorted(count.items(), key=lambda x:(-x[1], x[0])),
    },
    comments={
        "total": sum(count_cmt.values()),
        "status": count_cmt
    },
    max_date=max_date.strftime("%d/%m/%Y %H:%M"),
    min_date=min_date.strftime("%d/%m/%Y"),
    max_portada=max_portada,
    min_portada=min_portada
)

db.close()
