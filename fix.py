#!/usr/bin/env python3

from core.db import DB
from core.api import Api
from core.util import chunks
import sys
from core.util import chunks, extract_domain

import signal

db = DB()

def close_out(*args, **kargv):
    global db
    if db.closed:
        return
    db.close()

signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])

def get_items():
    for id, url in db.select('''
            select
                id, url
            from
                LINKS
            where
                domain is null and
                url is not null and
                url!='' and
                url not like 'https://www.meneame.net/%'
        '''):
        dom = extract_domain(url)
        if dom:
            print(id, dom, "         ", end="\r")
            yield (dom, id)

sql = "update LINKS set domain = %s where id = %s"
for rows in chunks(get_items(), 1000):
    cursor = db.con.cursor()
    cursor.executemany(sql, rows)
    cursor.close()

close_out()
