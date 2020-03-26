#!/usr/bin/env python3

from core.api import Api
from core.db import DBLite, one_factory

import signal
import sys


db = DBLite("meneame.db")

def close_out(*args, **kargv):
    global db
    db.commit()
    ids = db.one("select count(id) from LINKS")
    print("\n"+str(ids), "links")
    db.close()

def my_range(ini, avoid):
    for i in range(ini-1, 0, -1):
        if i not in avoid:
            yield i

signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])

api = Api()

posts = api.get_links()
db.full_table("LINKS", posts)
#db.full_table("LINKS", api.search_links())
db.commit()
ids = list(db.select("select id from LINKS", row_factory=one_factory))
count = 0
try:
    for id in my_range(api.max_min.id, ids):
        p = api.get_link_info(id)
        if p:
            print(id, "               ", end="\r")
            db.insert("posts", **p)
            count = count + 1
            if count % 1000 == 0:
                db.commit()
except Exception as e:
    close_out()
    raise e from None
#comments = api.get_comments(*posts)
#db.full_table("COMMENTS", comments)
close_out()
