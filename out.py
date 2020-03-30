#!/usr/bin/env python3

from core.db import DBLite, dict_factory
import json

db = DBLite("meneame.db", readonly=True)

links=[]
for i in db.select('''
    select
        --title,
        id,
        datetime(date, 'unixepoch', 'localtime') date,
        tags
    from links
    where
    tags is not null and
    status='published'
''', row_factory=dict_factory):
    tags = i["tags"].strip().split(",")
    tags = [t.strip().lower() for t in tags if t.strip()]
    if tags:
        i["tags"] = sorted(set(tags))
        links.append(i)

with open("out/published.json", "w") as f:
    json.dump(links, f, indent=2)
