#!/usr/bin/env python3

from core.db import DB
from core.api import Api
from core.util import chunks
import sys

import signal

db = DB()
api = Api()


def close_out(*args, **kargv):
    global db
    if db.closed:
        return
    db.close()

signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])

def get_info(ids):
    for i in ids:
        r = api.get_info(what='link', id=id, fields="comments,sub_status_id")
        if r is None:
            continue
        for k, v in list(r.items()):
            if v is None or (isinstance(v, str) and not v.isdigit()):
                del r[k]
            if isinstance(v, str) and v.isdigit():
                r[k] = int(v)
        if not r:
            continue
        r["id"] = id
        yield r


def get_user(users, field):
   for user in users:
      user_id = api.extract_user_id(user)
      if user_id is not None:
         yield user_id, user

links = db.to_list("select id from LINKS where comments is null")
for rows in chunks(get_info(links), 2000):
   db.update("LINKS", rows, skipNull=True)

db.commit()

users = db.to_list("select distinct user from LINKS where user_id is null and user like '--%--'")
for user_id, user in get_user(users):
   cursor = db.con.cursor()
   db.execute("update `LINKS` set `user_id` = %s where `user` = %s", (user_id, user) )
   cursor.close()
   db.commit()

close_out()
