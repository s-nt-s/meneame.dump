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
    max_thread=100,
    list_size=2000
)


def close_out(*args, **kargv):
    global db
    if db.closed:
        return
    db.close()

signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])

def to_int(s):
    if s=="":
        return None
    try:
        return int(s)
    except:
        return s

def get_info(id):
    r = api.get_info(what='link', id=id, fields="sub_status,sub_status_id")
    if r is None:
        return None
    r["sub_status_id"]=to_int(r["sub_status_id"])
    if r["sub_status"] == "":
        r["sub_status"]=None
    r["id"] = id
    print(id, r["sub_status_id"], r["sub_status"])
    return r


def get_user(users):
   for user in users:
      user_id = api.extract_user_id(user)
      if user_id is not None:
         yield user_id, user

min_id = db.one("select max(id)-2001 from LINKS where sub_status is not null and sub_status_id is not null") or 0
links = db.select("select id from LINKS where sub_status_id is null or sub_status is null and id>"+str(min_id))
for rows in tm.list_run(get_info, links):
    db.update("LINKS", rows)

db.commit()

users = db.to_list("select distinct user from LINKS where user_id is null and user like '--%--'")
cursor = db.con.cursor()
for user_id, user in get_user(users):
   cursor.execute("update `LINKS` set `user_id` = %s where `user` = %s", (user_id, user) )
cursor.close()
db.commit()

close_out()
