#!/usr/bin/env python3

from core.stats import Stats
from core.j2 import Jnj2
from core.api import Api
from MySQLdb.cursors import DictCursor

st = Stats()

jHtml = Jnj2("template/", "docs/")

jHtml.save("index.html", st=st, years_completos=sorted(st.db.to_list("select distinct floor(mes) from GENERAL")[1:-1]))
jHtml.create_script("data/mensual.js", replace=True,
    mensual={
        "general":st.get_data_mensual(),
        "portada": st.get_data_mensual("status='published'"),
        "actualidad": st.get_data_mensual("status='published' and sub='actualidad'"),
        "estados":st.get_count_mensual(),
        "horas": st.get_horas_mensual(),
    },
)

st.db.close()
