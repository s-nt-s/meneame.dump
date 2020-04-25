#!/usr/bin/env python3

from core.stats import Stats
from core.j2 import Jnj2
from core.api import Api
from MySQLdb.cursors import DictCursor

st = Stats()

jHtml = Jnj2("template/", "docs/")

def get_root(dom):
    i=1
    while True:
        i = i + 1
        root = ".".join(dom.split(".")[-i:])
        if len(root)>5 and root!=dom:
            return "*."+root
        if root == dom:
            return root

dominios_todos = st.get_dominios()
dominios_portada = st.get_dominios("status='published'")

dominios=set()
for yr in dominios_portada.values():
    for d in yr.keys():
        dominios.add(d)
for yr in dominios_todos.values():
    for d in list(yr.keys()):
        if d not in dominios:
            del yr[d]
dominios.remove("total")
dominios = dominios.union(set(get_root(d) for d in dominios))
dominios = sorted(dominios)

jHtml.save("index.html",
    st=st,
    years_completos=sorted(st.db.to_list("select distinct floor(mes) from GENERAL")[1:-1]),
    dominios=dominios
)
jHtml.create_script("data/modelos.js", replace=True,
    modelos={
        "karma_general":st.get_karma(),
        "karma_portada": st.get_karma("status='published'"),
        "count_estados":st.get_count_mensual(),
        "count_categorias_todas": st.get_mes_categorias(),
        "count_categorias_published": st.get_mes_categorias("status='published'"),
        "horas_dia": st.get_horas_mensual(),
        "dominios_todos": dominios_todos,
        "dominios_portada": dominios_portada,
    },
    tags={
        "dominios":dominios
    }
)

st.db.close()
