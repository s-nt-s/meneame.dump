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
    "Intenta recuperar todo el historico de meneame.net",
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
    ids = db.one("select count(id) from COMMENTS")
    print("\n"+str(ids), "comments")
    db.close()

signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])

def get_comments(id):
    r = api.get_comments(id)
    print("%4d %s" % (len(r), id), end="\r")
    return r if r else None

def main():
    print("Obteniendo comentarios", end="\r")
    min_id = (db.one("select max(link) from COMMENTS") or 0)
    print("Obteniendo comentarios de link_id > %s" % min_id)
    gnr = db.select("select id from LINKS where id>{}".format(min_id))
    for comments in tm.list_run(get_comments, gnr):
        comments = api.fill_user_id(comments, what='comments')
        db.replace("COMMENTS", comments)

if __name__ == "__main__":
    try:
        main()
    finally:
        close_out()
