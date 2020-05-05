#!/usr/bin/env python3

import signal
import sys
from queue import Queue
from threading import Thread

from core.api import Api
from core.db import DB
from core.threadme import ThreadMe
from core.util import read_yml_all, readlines, mkArg

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
    min_id = 0
    max_date = db.one("select max(date) from POSTS")
    if max_date:
        max_date = max_date - api.safe_wait
        min_id = db.one("select max(id) from POSTS where `data`< %s" % max_date) or 0
    print("Obteniendo posts con id > %s and date < %s" % (min_id, max_date))
    for posts in tm.list_run(get_posts, range(min_id+1, api.last_post+1)):
        db.replace("POSTS", posts)

if __name__ == "__main__":
    try:
        main()
    finally:
        close_out()
