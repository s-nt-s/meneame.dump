#!/usr/bin/env python3

from core.db import DB
from MySQLdb.cursors import DictCursor
import json

db = DB()

links=[]
for i in db.select('''
    select
        -- title,
        id,
        datetime(date, 'unixepoch', 'localtime') date,
        tags
    from links
    where
    tags is not null and
    status='published'
''', cursor=DictCursor):
    tags = i["tags"].strip().split(",")
    tags = [t.strip().lower() for t in tags if t.strip()]
    if tags:
        i["tags"] = sorted(set(tags))
        links.append(i)

with open("out/published.json", "w") as f:
    json.dump(links, f, indent=2)
