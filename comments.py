#!/usr/bin/env python3

import signal
import sys
from queue import Queue
from threading import Thread

from core.api import Api
from core.db import DB
from core.threadme import ThreadMe
from core.util import read_yml_all, readlines

import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

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
    db.fix()
    ids = db.one("select count(id) from COMMENTS")
    print("\n"+str(ids), "comments")
    db.close()

signal.signal(signal.SIGINT, lambda *args, **kargv: [close_out(), sys.exit(0)])

def get_comments(a, id):
    r = a.get_comments(id)
    print("%4d %s" % (len(r), id), end="\r")
    return r if r else None

def main():
    tm.rt_null=[]
    gnr = db.comment_gaps(api.mnm_config['time_enabled_comments'])
    for comments in tm.list_run(get_comments, gnr):
        db.replace("COMMENTS", comments)
        if tm.rt_null:
            db.replace("broken_id", [{"what": 'zero_comment', 'id': i} for i in tm.rt_null])
            tm.rt_null = []

if __name__ == "__main__":
    try:
        main()
    finally:
        close_out()
