#!/usr/bin/env python3

from core.api import Api
from core.db import DBLite, one_factory

api = Api()
db = DBLite("meneame.db")

posts = api.get_links()
db.full_table("POSTS", posts)
ids = list(db.select("select id from posts", row_factory=one_factory))
try:
    while api._max_min_id>0:
        api._max_min_id = api._max_min_id -1
        if api._max_min_id not in ids:
            p = api.get_link_info(api._max_min_id)
            if p:
                print(p)
                db.insert("posts", **p)
except Exception as e:
    db.close()
    raise e from None
#comments = api.get_comments(*posts)
#db.full_table("COMMENTS", comments)
db.close()
