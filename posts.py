#!/usr/bin/env python3

import signal
import sys
from queue import Queue
from threading import Thread

from core.api import Api
from core.db import DB
from core.threadme import ThreadMe
from core.util import mkArg
from datetime import datetime

import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

arg = mkArg(
    "Intenta recuperar todo el historico de posts",
    silent="No imprime trazas"
)
if arg.silent:
    print = lambda *args, **kargv: None


db = DB()
api = Api()
tm = ThreadMe(
    max_thread=30,
    list_size=2000
)

def close_out(*args, **kargv):
    global db
    if db.closed:
        return
    ids = db.one("select count(id) from POSTS")
    print("\n"+str(ids), "posts")
    db.close()

signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])

def get_posts(id):
    r = api.get_post_info(id)
    print(id, end="\r")
    return r

def main():
    f = datetime.fromtimestamp(api.safe_date)
    min_id = (db.one("select max(id) from POSTS where `date`< %s" % api.safe_date) or 0) + 1
    print("Obteniendo posts con id > {} and date < {} ({:%Y.%m.%d})".format(min_id, api.safe_date, f))
    for posts in tm.list_run(get_posts, range(min_id, api.last_post)):
        sz = len(posts)
        posts = [p for p in posts if p['date']<api.safe_date]
        if posts:
            db.replace("POSTS", posts)
        if len(posts)<sz:
            break

if __name__ == "__main__":
    try:
        main()
    finally:
        close_out()
