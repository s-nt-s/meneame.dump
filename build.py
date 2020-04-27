#!/usr/bin/env python3

from core.stats import Stats
from core.j2 import Jnj2
from core.api import Api
from MySQLdb.cursors import DictCursor

st = Stats()

jHtml = Jnj2("template/", "docs/")


dominios = st.get_full_dominios()

jHtml.save("index.html",
    st=st,
    years_completos=sorted(st.db.to_list("select distinct floor(mes) from GENERAL")[1:-1]),
    dominios=dominios.claves
)
jHtml.create_script("data/modelos.js", replace=True,
    modelos={
        "karma_general":st.get_karma(),
        "karma_portada": st.get_karma("status='published'"),
        "count_estados":st.get_count_mensual(),
        "count_categorias_todas": st.get_mes_categorias(),
        "count_categorias_published": st.get_mes_categorias("status='published'"),
        "horas_dia": st.get_horas_mensual(),
        "dominios_todos": dominios.todos,
        "dominios_portada": dominios.portada,
        "tags": st.get_tags()
    },
    tags={
        "dominios": dominios.claves
    }
)

st.db.close()
