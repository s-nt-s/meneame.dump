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

jHtml = Jnj2("template/", "docs/i2/")
jHtml.resources.extend([
    "docs/00-libs",
    "docs/01-js",
    "docs/css"
])

jHtml.create_script("data/modelos.js", replace=True,
    strikes=st.get_strikes_data()
)
jHtml.save("i2.html",
    destino="index.html",
    st=st
)
st.db.close()
