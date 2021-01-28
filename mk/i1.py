#!/usr/bin/env python3

from core.stats import Stats
from core.j2 import Jnj2
from core.api import Api
from MySQLdb.cursors import DictCursor

import argparse

parser = argparse.ArgumentParser(description='Genera la 2º informe')
parser.add_argument('--fast', action='store_true', help="No regenera los modelos")
arg = parser.parse_args()

st = Stats()

jHtml = Jnj2("template/", "docs/i1/")
jHtml.resources.extend([
    "docs/00-libs",
    "docs/01-js",
    "docs/css"
])


dominios = st.get_full_dominios()
tags = st.get_tags()
tags_graph = st.get_tags_graph()

jHtml.save("i1.html",
    destino="index.html",
    st=st,
    years_completos=sorted(st.db.to_list("select distinct floor(mes) from GENERAL")[1:-1]),
    dominios=dominios.claves,
    tags=tags.claves,
    tags_nodes=len(tags_graph["nodes"])
)
if not arg.fast:
    jHtml.create_script("data/modelos.js", replace=True,
        modelos={
            "karma_general":st.get_karma(),
            "karma_portada": st.get_karma("status='published'"),
            "count_estados":st.get_count_mensual(),
            "count_categorias_todas": st.get_mes_categorias(),
            "count_categorias_published": st.get_mes_categorias("status='published'"),
            "uso_tiempo": st.get_uso_tiempo(),
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

jHtml.create_script("data/graph.js", replace=True,
    graphs={
        "tags": tags_graph
    }
)
st.db.close()
