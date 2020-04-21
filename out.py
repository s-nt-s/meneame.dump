#!/usr/bin/env python3

from core.stats import Stats
from core.j2 import Jnj2
from core.api import Api
from MySQLdb.cursors import DictCursor

st = Stats()

jHtml = Jnj2("template/", "docs/")

jHtml.save("index.html", st=st, years_completos=sorted(st.db.to_list("select distinct floor(mes) from GENERAL")[1:-1]))
jHtml.create_script("data/modelos.js", replace=True,
    modelos={
        "misce_general":st.get_data_mensual(),
        "misce_portada": st.get_data_mensual("status='published'"),
        "misce_actualidad": st.get_data_mensual("status='published' and sub='actualidad'"),
        "count_estados":st.get_count_mensual(),
        "count_categorias_todas": st.get_mes_categorias(),
        "count_categorias_published": st.get_mes_categorias("status='published'"),
        "horas_dia": st.get_horas_mensual(),
    },
)

st.db.close()
