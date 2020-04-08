#!/usr/bin/env python3

from core.db import DB
from core.j2 import Jnj2

db = DB()

jHtml = Jnj2("template/", "docs/")

jHtml.save("informe.html", db=db)

db.close()
