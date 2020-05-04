#!/usr/bin/env python3

from core.stats import Stats
from core.j2 import Jnj2
from core.api import Api
from MySQLdb.cursors import DictCursor

st = Stats()

jHtml = Jnj2("template/", "docs/")


dominios = st.get_full_dominios()
tags = st.get_tags()

jHtml.save("index.html",
    st=st,
    years_completos=sorted(st.db.to_list("select distinct floor(mes) from GENERAL")[1:-1]),
    dominios=dominios.claves,
    tags=tags.claves
)
jHtml.create_script("data/modelos.js", replace=True,
    modelos={
        "karma_general":st.get_karma(),
        "karma_portada": st.get_karma("status='published'"),
        "count_estados":st.get_count_mensual(),
        "count_categorias_todas": st.get_mes_categorias(),
        "count_categorias_published": st.get_mes_categorias("status='published'"),
        "horas_dia": st.get_horas_mensual(),
        "actividad": st.get_actividad(),
        "dominios_todos": dominios.todos,
        "dominios_portada": dominios.portada,
        "tags_portada": tags.portada
    },
    tags={
        "dominios": dominios.claves,
        "tags": tags.claves
    },
    modelos_aux={
        "actividad": st.get_users_by_period()
    }
)

False and jHtml.create_script("data/graph.js", replace=True,
    graphs={
        "tags": st.get_tags_graph()
    }
)
st.db.close()
