#!/usr/bin/env python3

from core.stats import Stats
from core.j2 import Jnj2
from core.api import Api
from MySQLdb.cursors import DictCursor

st = Stats()

jHtml = Jnj2("template/", "docs/")

jHtml.save("index.html", st=st)

del st
