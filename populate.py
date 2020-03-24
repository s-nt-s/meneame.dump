#!/usr/bin/env python3

from core.api import Api
from core.db import DBLite, one_factory

import signal
import sys


db = DBLite("meneame.db")

def close_out(*args, exit=True, **kargv):
    global db
    db.commit()
    ids = db.one("select count(id) from posts")
    print("\n"+str(ids), "links")
    db.close()
    if exit:
        sys.exit(0)

signal.signal(signal.SIGINT, close_out)

api = Api()

posts = api.get_links()
db.full_table("POSTS", posts)
db.full_table("POSTS", api.search_links())
db.commit()
ids = list(db.select("select id from posts", row_factory=one_factory))
count = 0
try:
    while api._max_min_id>0:
        api._max_min_id = api._max_min_id -1
        if api._max_min_id not in ids:
            p = api.get_link_info(api._max_min_id)
            if p:
                print(p["id"], "               ", end="\e")
                db.insert("posts", **p)
                count = count + 1
                if count % 1000 == 0:
                    db.commit()
except Exception as e:
    close_out(exit=False)
    raise e from None
#comments = api.get_comments(*posts)
#db.full_table("COMMENTS", comments)
close_out()
