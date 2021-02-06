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

jHtml.create_script("data/00-modelos.js", replace=True,
    strikes=st.get_strikes_data()
)
ban={
    "karma":0,
    "dias":0
}
kd=(
    (0, 0),
    (2, 1),
    (2, 2),
    (2, 5),
    (2, 20),
    (0, 90)
)
for u, s in st.strikes["user_strike"]:
    for i in range(s):
        k, d = kd[min(len(kd)-1, i)]
        ban["karma"] = ban["karma"] + k
        ban["dias"] = ban["dias"] + d

jHtml.save("i2.html",
    destino="index.html",
    st=st,
    ban=ban
)
st.db.close()
