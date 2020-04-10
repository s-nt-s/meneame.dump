#!/usr/bin/env python3

from core.db import DB
from core.api import Api
from core.util import chunks
import sys
from core.threadme import ThreadMe

import signal

db = DB()
api = Api()

tm = ThreadMe(
    fix_param=api,
    max_thread=30,
    list_size=30
)


def close_out(*args, **kargv):
    global db
    if db.closed:
        return
    db.close()

signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])

def get_info(a, id):
    r = a.get_info(what='link', id=id, fields="comments,sub_status_id")
    if r is None:
        return None
    for k, v in list(r.items()):
        if v is None or (isinstance(v, str) and not v.isdigit()):
            del r[k]
        elif isinstance(v, str) and v.isdigit():
            r[k] = int(v)
    if not r:
        return None
    r["id"] = id
    print(r)
    return r


def get_user(users, field):
   for user in users:
      user_id = api.extract_user_id(user)
      if user_id is not None:
         yield user_id, user

links = db.to_list("select id from LINKS where comments is null")
for rows in tm.list_run(get_info, links):
    obj={}
    for o in rows:
        k = tuple(sorted(o.keys()))
        obj[k] = (obj.get(k, [])) + [o]
    for vls in obj.values():
        db.update("LINKS", vls, skipNull=True)

db.commit()

users = db.to_list("select distinct user from LINKS where user_id is null and user like '--%--'")
for user_id, user in get_user(users):
   cursor = db.con.cursor()
   db.execute("update `LINKS` set `user_id` = %s where `user` = %s", (user_id, user) )
   cursor.close()
   db.commit()

close_out()
