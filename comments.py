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


db = DB(debug_dir="sql/")
api = Api()
tm = ThreadMe(
    fix_param=api,
    max_thread=30
)

def close_out(*args, **kargv):
    global db
    if db.closed:
        return
    ids = db.one("select count(id) from COMMENTS")
    print("\n"+str(ids), "comments")
    db.close()

signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])

def get_comments(a, id):
    r = a.get_comments(id)
    db.meta.min_comment_history_id = max(db.meta.min_comment_history_id, id)
    print("%4d %s" % (len(r), id), end="\r")
    return r if r else None

def main():
    min_id  = db.meta.get("min_comment_history_id", api.first_link["id"])
    print("Obteniendo comentarios de link_id > %s and link_date < %s " % (min_id, api.mnm_config['time_enabled_comments']))
    gnr = db.comment_gaps(min_id, api.mnm_config['time_enabled_comments'])
    for comments in tm.list_run(get_comments, gnr):
        comments = api.fill_user_id(comments)
        db.replace("COMMENTS", comments)
        db.save_meta("min_comment_history_id")
    db.save_meta("min_comment_history_id")

if __name__ == "__main__":
    try:
        main()
    finally:
        close_out()
