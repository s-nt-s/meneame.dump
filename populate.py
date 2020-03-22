#!/usr/bin/env python3

from core.api import Api
from core.db import DBLite

api = Api()
db = DBLite("meneame.db")

posts = api.get_posts()
db.full_table("POSTS", posts)
comments = api.get_comments(*posts)
db.full_table("COMMENTS", comments)
db.close()
